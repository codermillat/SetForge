import os
import json
import asyncio
import logging
from typing import Set, Dict, Any
from datetime import datetime, timezone

from src.utils.config_manager import ConfigManager
from src.utils.api_client_manager import APIClientManager
from src.structuring_pipeline.cleaner import DataCleaner
from src.structuring_pipeline.extractor import InformationExtractor
from src.structuring_pipeline.validator import DataValidator

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Helper Functions ---

def load_schema(path: str) -> Dict[str, Any]:
    """Loads the JSON schema from a file."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.critical(f"Fatal: Could not load schema from {path}. Error: {e}")
        raise

def get_all_raw_files(raw_dir: str) -> Set[str]:
    """Recursively finds all files in the raw data directory."""
    all_files = set()
    for root, _, files in os.walk(raw_dir):
        for name in files:
            relative_path = os.path.relpath(os.path.join(root, name), raw_dir)
            all_files.add(relative_path)
    return all_files

def load_processed_files(checkpoint_file: str) -> Set[str]:
    """Loads the set of already processed files from the checkpoint file."""
    if not os.path.exists(checkpoint_file):
        return set()
    try:
        with open(checkpoint_file, 'r') as f:
            return set(json.load(f))
    except (json.JSONDecodeError, IOError):
        logger.warning(f"Could not read checkpoint file {checkpoint_file}. Starting fresh.")
        return set()

def save_processed_files(processed_files: Set[str], checkpoint_file: str):
    """Saves the set of processed files to the checkpoint file."""
    try:
        with open(checkpoint_file, 'w') as f:
            json.dump(list(processed_files), f, indent=2)
    except IOError as e:
        logger.error(f"Could not write to checkpoint file {checkpoint_file}. Error: {e}")

# --- Main Pipeline Class ---

class StructuringPipeline:
    """Orchestrates the entire data structuring pipeline."""

    def __init__(self, config: ConfigManager):
        self.config = config
        self.schema = load_schema('schema.json')
        
        # Initialize managers and modules
        self.api_manager = APIClientManager(config, logger)
        self.cleaner = DataCleaner(
            raw_data_dir=config.get('data_config.raw_dir', 'data'),
            cleaned_data_dir=config.get('data_config.cleaned_dir', 'data_cleaned')
        )
        self.extractor = InformationExtractor(
            api_manager=self.api_manager,
            schema=self.schema,
            prompt_template_path='src/prompts/structuring/extract_university_info.md'
        )
        self.validator = DataValidator(schema=self.schema)
        
        # Configuration for directories and checkpointing
        self.structured_dir = config.get('data_config.structured_dir', 'data_structured')
        self.checkpoint_file = os.path.join(
            config.get('data_config.checkpoint_dir', 'checkpoints'),
            'structured_files.json'
        )
        self.dead_letter_dir = config.get('qa_pipeline_config.dead_letter_queue_dir', 'data/dead_letter_queue/structuring')

        # Ensure directories exist
        os.makedirs(self.structured_dir, exist_ok=True)
        os.makedirs(self.dead_letter_dir, exist_ok=True)

    async def process_single_file(self, file_path: str):
        """Runs a single file through the entire structuring pipeline."""
        logger.info(f"Starting processing for: {file_path}")
        
        # 1. Clean
        cleaned_file_path = self.cleaner.process_file(file_path)
        if not cleaned_file_path:
            logger.error(f"Cleaning failed for {file_path}. Moving to dead-letter queue.")
            self._move_to_dead_letter(file_path)
            return

        # 2. Extract
        try:
            with open(cleaned_file_path, 'r', encoding='utf-8') as f:
                cleaned_text = f.read()
        except IOError as e:
            logger.error(f"Could not read cleaned file {cleaned_file_path}: {e}")
            self._move_to_dead_letter(file_path)
            return
            
        extracted_data = await self.extractor.extract(cleaned_text, file_path)
        if not extracted_data:
            logger.error(f"Extraction failed for {file_path}. Moving to dead-letter queue.")
            self._move_to_dead_letter(file_path)
            return

        # 3. Validate and Enrich
        validated_data = self.validator.validate_and_enrich(extracted_data, file_path)
        if not validated_data:
            logger.error(f"Validation failed for {file_path}. Moving to dead-letter queue.")
            self._move_to_dead_letter(file_path)
            return
            
        # 4. Save
        self._save_structured_data(validated_data, file_path)
        logger.info(f"Successfully processed and saved: {file_path}")

    def _save_structured_data(self, data: Dict[str, Any], original_path: str):
        """Saves the final structured data as a JSON file."""
        # Sanitize the filename and save it
        output_filename = original_path.replace('/', '_') + '_structured.json'
        output_path = os.path.join(self.structured_dir, output_filename)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Failed to save structured data for {original_path} to {output_path}: {e}")

    def _move_to_dead_letter(self, file_path: str):
        """Moves a failed file to the dead-letter queue."""
        try:
            # For simplicity, we'll just log it. A real implementation might move the file.
            dead_letter_log = os.path.join(self.dead_letter_dir, 'failed_files.log')
            with open(dead_letter_log, 'a') as f:
                f.write(f"{datetime.now(timezone.utc).isoformat()} - {file_path}\\n")
        except Exception as e:
            logger.error(f"Could not write to dead-letter log for file {file_path}: {e}")

    async def run(self):
        """Main execution loop for the pipeline."""
        logger.info("Starting the SetForge Data Structuring Pipeline...")
        
        raw_files = get_all_raw_files(self.config.get('data_config.raw_dir', 'data'))
        processed_files = load_processed_files(self.checkpoint_file)
        
        files_to_process = sorted(list(raw_files - processed_files))
        
        if not files_to_process:
            logger.info("No new files to process. Pipeline run complete.")
            await self.api_manager.close_session()
            return

        logger.info(f"Found {len(files_to_process)} new files to process.")
        
        # Create and run tasks concurrently
        concurrency_limit = self.config.get('qa_pipeline_config.concurrency_limit', 3)
        semaphore = asyncio.Semaphore(concurrency_limit)

        async def process_with_semaphore(file_path):
            async with semaphore:
                await self.process_single_file(file_path)
                processed_files.add(file_path)
        
        tasks = [process_with_semaphore(f) for f in files_to_process]
        await asyncio.gather(*tasks)

        # Finalize
        save_processed_files(processed_files, self.checkpoint_file)
        await self.api_manager.close_session()
        logger.info("SetForge Data Structuring Pipeline run finished.")


if __name__ == "__main__":
    try:
        config_manager = ConfigManager('config.yaml')
        pipeline = StructuringPipeline(config_manager)
        asyncio.run(pipeline.run())
    except Exception as e:
        logger.critical(f"A critical error occurred in the pipeline: {e}", exc_info=True)
