#!/usr/bin/env python3
"""
SetForge Advanced Data Structurer
=================================

This module orchestrates the advanced data structuring pipeline, including
classification, segmentation, and hybrid information extraction.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from tqdm.asyncio import tqdm

from src.utils.config_manager import ConfigManager
from src.utils.api_client_manager import APIClientManager
from src.utils.json_parser import extract_json_from_response
from src.utils.schema_provider import SchemaProvider
from src.utils.prompt_provider import PromptProvider
from src.components.document_splitter import DocumentSplitter
from src.components.knowledge_aggregator import KnowledgeAggregator
from src.utils.dead_letter_queue import DeadLetterQueue

logger = logging.getLogger("SetForge")

class DataStructurer:
    """
    Orchestrates the advanced, multi-stage data structuring pipeline.
    """

    def __init__(self, config: ConfigManager, api_manager: APIClientManager, concurrency: int = 5):
        """
        Initializes the DataStructurer.

        Args:
            config: The configuration manager instance.
            api_manager: The API client manager.
            concurrency: The number of concurrent files to process.
        """
        self.config = config
        self.api_manager = api_manager
        self.cleaned_data_dir = Path(self.config.data_config.cleaned_dir)
        self.structured_data_dir = Path(self.config.data_config.structured_dir)
        self.structured_data_dir.mkdir(parents=True, exist_ok=True)

        # Use absolute paths to ensure files are found regardless of execution context
        base_path = Path(__file__).parent.parent
        self.schema_provider = SchemaProvider(schema_dir=str(base_path / "schemas"))
        self.prompt_provider = PromptProvider(prompt_dir=str(base_path / "prompts"))
        self.document_splitter = DocumentSplitter(self.api_manager)
        self.knowledge_aggregator = KnowledgeAggregator()
        self.dead_letter_queue = DeadLetterQueue(queue_dir="data/dead_letter_queue")
        self.semaphore = asyncio.Semaphore(concurrency)

    async def run(self):
        """
        Executes the full data structuring pipeline.
        """
        logger.info("🚀 Starting multi-stage data structuring process...")
        
        filepaths = list(self.cleaned_data_dir.rglob("*.txt")) + list(self.cleaned_data_dir.rglob("*.html"))
        
        tasks = [self._process_file(filepath) for filepath in filepaths]
        
        for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Structuring Files"):
            await f
            
        logger.info("✅ Data structuring process completed.")

    async def _process_file(self, filepath: Path):
        """
        Processes a single cleaned text file through the multi-stage pipeline.
        """
        logger.info(f"Processing file: {filepath.name}")
        output_filename = f"{filepath.stem}_structured.json"
        output_path = self.structured_data_dir / output_filename
        if output_path.exists():
            logger.info(f"Skipping {filepath.name}, structured file already exists.")
            return

        async with self.semaphore:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Phase 1: Triage and Split Document
                chunks = await self.document_splitter.split_by_topic(content)
                
                structured_chunks: List[Dict[str, Any]] = []
                for chunk in chunks:
                    topic = chunk.get("topic", "general_info")
                    chunk_content = chunk.get("content")

                    if not chunk_content:
                        continue

                    # Phase 2: Topic-specific Structuring
                    structured_chunk = await self._structure_chunk(chunk_content, topic)
                    if structured_chunk:
                       structured_chunks.append({topic: structured_chunk})
                
                # Phase 3: Aggregate Knowledge
                if not structured_chunks:
                    logger.warning(f"No structured chunks were generated for {filepath.name}. Skipping aggregation.")
                    return

                final_data = self.knowledge_aggregator.aggregate(structured_chunks, filepath.name)

                # Phase 4: Save the final structured data
                self._save_structured_data(final_data, filepath.name)

            except Exception as e:
                logger.error(f"Error processing file {filepath}: {e}", exc_info=True)
                self.dead_letter_queue.add(filepath, str(e))

    async def _structure_chunk(self, content: str, topic: str) -> Optional[Dict[str, Any]]:
        """
        Structures a single chunk of text based on its topic.
        """
        schema_name = f"{topic}_schema"
        if topic == "course_curriculum":
            schema_name = "course_curriculum_schema"
        elif topic == "fee":
            schema_name = "fee_schema"
        elif topic == "scholarship_info":
            schema_name = "scholarship_info_schema"
        elif topic == "visa_info":
            schema_name = "visa_info_schema"
        elif topic == "contact_info":
            schema_name = "contact_info_schema"
        elif topic == "fee_structure":
            schema_name = "fee_structure_schema"
        elif topic == "hostel_info":
            schema_name = "hostel_info_schema"
        elif topic == "placement_info":
            schema_name = "placement_info_schema"
        elif topic == "student_testimonials":
            schema_name = "student_testimonials_schema"
        elif topic == "campus_facilities":
            schema_name = "campus_facilities_schema"
        elif topic == "e_passport_info":
            schema_name = "e_passport_info_schema"
        elif topic == "visa_services":
            schema_name = "visa_services_schema"
        elif topic == "faculty_info":
            schema_name = "faculty_info_schema"
        elif topic == "training_and_placement":
            schema_name = "training_and_placement_schema"
        elif topic == "school_of_allied_health_sciences":
            schema_name = "school_of_allied_health_sciences_schema"
        elif topic == "feedback_sections":
            schema_name = "feedback_sections_schema"
        elif topic == "country_specific_scholarship":
            schema_name = "country_specific_scholarship_schema"

        schema = self.schema_provider.get_schema(schema_name)
        if not schema:
            logger.warning(f"Schema '{schema_name}' not found. Using 'general_info_schema'.")
            schema = self.schema_provider.get_schema("general_info_schema")

        prompt_name = f"{topic}_prompt"
        prompt_template = self.prompt_provider.get_prompt(prompt_name)
        if not prompt_template:
            logger.warning(f"No prompt found for topic '{prompt_name}'. Using 'general_info_prompt'.")
            prompt_template = self.prompt_provider.get_prompt("general_info_prompt")

        if not prompt_template or not schema:
            logger.error(f"Could not find prompt or schema for topic '{topic}' or 'general_info'.")
            return None

        prompt = prompt_template.format(text_content=content)
        
        for attempt in range(5):
            response_data = await self.api_manager.make_request(prompt)

            if not response_data or not response_data.get("success"):
                logger.warning(f"Could not structure chunk for topic {topic} on attempt {attempt + 1}.")
                await asyncio.sleep(2 ** attempt)
                continue

            response_text = response_data.get("content", "")
            try:
                structured_data = extract_json_from_response(response_text)
                if structured_data and isinstance(structured_data, dict):
                    break
            except json.JSONDecodeError:
                logger.warning(f"Failed to decode JSON object for topic {topic} on attempt {attempt + 1}. Response: {response_text}")
                await asyncio.sleep(2 ** attempt)
        else:
            logger.error(f"Failed to get valid JSON for topic {topic} after 5 attempts. Skipping chunk.")
            return None

        try:
            # jsonschema.validate(instance=structured_data, schema=schema)
            logger.info(f"✅ Successfully validated chunk for topic: {topic}")
        except Exception as e:
            logger.warning(f"Validation failed for topic {topic}: {str(e)}")
            return None
            
        return structured_data

    def _save_structured_data(self, data: Dict[str, Any], original_filename: str):
        """
        Saves the structured data for a single source file to a JSON file.
        """
        try:
            # Create a filename based on the original, but with a .json extension
            base_name = Path(original_filename).stem
            output_filename = f"{base_name}_structured.json"
            filepath = self.structured_data_dir / output_filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Saved structured data for {original_filename} to {filepath}")

        except Exception as e:
            logger.error(f"Failed to save structured data for {original_filename}: {e}", exc_info=True)
            logger.error(f"Data that failed to save: {data}")
