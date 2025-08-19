#!/usr/bin/env python3
"""
SetForge Q&A Generation Pipeline (Part 2)
Orchestrates the generation of question-answer pairs from structured data.
"""

import asyncio
import json
import logging
import shutil
from pathlib import Path
from typing import Set, List, Tuple, Coroutine, Any, Optional

from src.utils.config_manager import ConfigManager
from src.utils.api_client_manager import APIClientManager
from src.pipeline.qa_generator import QAGenerator

# Ensure logs directory exists before configuring logging
Path("logs").mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/qa_pipeline.log"),
        logging.StreamHandler()
    ]
)

class QAPipeline:
    """
    Orchestrates the Q&A generation pipeline.
    """

    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.api_manager = APIClientManager(config, self.logger)
        
        # Load configs
        qa_config = self.config.get('qa_pipeline_config', {})
        data_config = self.config.get('data_config', {})

        # Pipeline parameters
        self.concurrency_limit = qa_config.get('concurrency_limit', 5)
        self.max_retries = qa_config.get('max_retries', 3)
        
        # Directories and files
        self.structured_data_dir = Path(data_config.get('structured_dir', 'data_structured'))
        self.qa_output_dir = Path(data_config.get('qa_dir', 'data_qa'))
        self.dlq_dir = Path(qa_config.get('dead_letter_queue_dir', 'data/dead_letter_queue/qa'))
        self.output_file = Path(qa_config.get('qa_output_file', 'data_qa/qna_dataset.jsonl'))
        self.review_file = Path(qa_config.get('qa_review_file', 'data_qa/needs_review.jsonl'))

        # Ensure directories exist
        self.qa_output_dir.mkdir(parents=True, exist_ok=True)
        self.dlq_dir.mkdir(parents=True, exist_ok=True)

        # Checkpoint file for tracking processed files
        self.checkpoint_dir = Path(data_config.get('checkpoint_dir', 'checkpoints'))
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_file = self.checkpoint_dir / 'qa_processed_files.json'

    def _load_processed_files(self) -> Set[str]:
        """Loads the set of already processed filenames from the checkpoint file."""
        if not self.checkpoint_file.exists():
            return set()
        try:
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except (json.JSONDecodeError, FileNotFoundError):
            return set()

    def _save_processed_files(self, processed_files: Set[str]):
        """Saves the set of processed filenames to the checkpoint file."""
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(list(processed_files), f, indent=4)

    async def run(self, test_mode: bool = False, sample_files: Optional[List[str]] = None):
        """
        Runs the Q&A generation pipeline with concurrency control and retries.
        """
        processed_files: Set[str] = set()
        if test_mode:
            self.logger.info("🚀 Starting SetForge Q&A Generation Pipeline (Part 2) in TEST MODE")
            if not sample_files:
                self.logger.error("❌ Test mode requires a list of sample files.")
                return
            files_to_process = [self.structured_data_dir / f for f in sample_files if (self.structured_data_dir / f).exists()]
        else:
            self.logger.info("🚀 Starting SetForge Q&A Generation Pipeline (Part 2)")
            processed_files = self._load_processed_files()
            self.logger.info(f"Loaded {len(processed_files)} processed files from checkpoint.")
            all_structured_files = [f for f in self.structured_data_dir.glob('*.json')]
            files_to_process = [f for f in all_structured_files if f.name not in processed_files]

        if not files_to_process:
            self.logger.info("✅ No new structured data files to process. Pipeline is up-to-date.")
            return

        self.logger.info(f"Found {len(files_to_process)} new structured data files to process.")

        # Initialize tools
        qa_generator = QAGenerator(self.api_manager)
        semaphore = asyncio.Semaphore(self.concurrency_limit)

        tasks: List[Coroutine[Any, Any, Tuple[Path, bool]]] = [
            self._process_file_wrapper(qa_generator, structured_file, semaphore)
            for structured_file in files_to_process
        ]

        results: List[Tuple[Path, bool]] = await asyncio.gather(*tasks)

        newly_processed_count = sum(1 for _, success in results if success)
        self._save_processed_files(processed_files.union(f.name for f, s in results if s))

        self.logger.info(f"✅ Q&A Generation Pipeline completed. Processed {newly_processed_count} new files.")
        await self.api_manager.close_session()

    async def _process_file_wrapper(self, qa_generator: QAGenerator, structured_file: Path, semaphore: asyncio.Semaphore) -> tuple[Path, bool]:
        """
        A wrapper for _process_file that includes semaphore, retries, and DLQ logic.
        """
        async with semaphore:
            for attempt in range(self.max_retries):
                try:
                    return await self._process_file(qa_generator, structured_file)
                except Exception as e:
                    self.logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed for {structured_file.name}: {e}")
                    if attempt + 1 == self.max_retries:
                        self.logger.error(f"All {self.max_retries} retries failed for {structured_file.name}. Moving to DLQ.", exc_info=True)
                        self._move_to_dlq(structured_file)
                        return structured_file, False
                    await asyncio.sleep(2 ** attempt) # Exponential backoff
            return structured_file, False # Should not be reached

    def _move_to_dlq(self, file_path: Path):
        """Moves a file to the dead-letter queue."""
        try:
            shutil.move(str(file_path), self.dlq_dir / file_path.name)
            self.logger.info(f"Moved {file_path.name} to {self.dlq_dir}")
        except Exception as e:
            self.logger.error(f"Failed to move {file_path.name} to DLQ: {e}", exc_info=True)

    async def _process_file(self, qa_generator: QAGenerator, structured_file: Path) -> tuple[Path, bool]:
        """
        Processes a single structured data file: generates and saves Q&A pairs.
        """
        self.logger.info(f"Processing file: {structured_file.name}")
        
        with open(structured_file, 'r', encoding='utf-8') as f:
            structured_content = json.load(f)

        if not structured_content:
            self.logger.warning(f"Skipping empty file: {structured_file.name}")
            return structured_file, True

        qa_pairs = await qa_generator.generate_qa_pairs(structured_content)
        if not qa_pairs:
            self.logger.info(f"No Q&A pairs generated for {structured_file.name}")
            return structured_file, True

        with open(self.output_file, 'a', encoding='utf-8') as f:
            for qa_pair in qa_pairs:
                f.write(json.dumps(qa_pair, ensure_ascii=False) + '\n')

        self.logger.info(f"Processed and saved {len(qa_pairs)} Q&A pairs for {structured_file.name}.")
        
        return structured_file, True

async def main(test: bool = False):
    """
    Main entry point for the Q&A generation pipeline.
    
    Args:
        test (bool): If True, runs in test mode.
    """
    config = ConfigManager()
    
    pipeline = QAPipeline(config)
    
    if test:
        sample_files = [
            "www.sharda.ac.in_B_Tech_Computer_Science_CSE_College_in_Noida_-_Courses_Details_Fees_Admissio_raw_2025-08-10-18-29-23_structured.json",
            "bdhcdelhi.org_MRP_against_Lost_Passport_raw_2025-08-10-18-34-50_structured.json",
            "niu.edu.in_Eligibility_Criteria_and_Fee_Structure_Noida_International_University_raw_2025-08-10-18-48-38_structured.json",
            "admissions.galgotiasuniversity.edu.in_Home_raw_2025-08-10-20-22-14_structured.json",
            "amity.edu_amity_edu_raw_2025-08-11-11-44-33_structured.json"
        ]
        await pipeline.run(test_mode=True, sample_files=sample_files)
    else:
        await pipeline.run()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the SetForge Q&A Generation Pipeline.")
    parser.add_argument('--test', action='store_true', help='Run in test mode on a small sample of files.')
    args = parser.parse_args()
    
    asyncio.run(main(test=args.test))
