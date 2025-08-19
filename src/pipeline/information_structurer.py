#!/usr/bin/env python3
"""
SetForge Information Structurer
===============================

This module uses an LLM to transform annotated text into structured JSON data
based on a predefined schema.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional

from src.utils.api_client_manager import APIClientManager

logger = logging.getLogger("SetForge")

class InformationStructurer:
    """
    Consumes annotated text and uses an LLM to generate structured JSON data.
    """

    def __init__(self, annotated_data_dir: str, structured_data_dir: str, api_manager: APIClientManager):
        """
        Initializes the InformationStructurer.

        Args:
            annotated_data_dir: Directory containing annotated text files.
            structured_data_dir: Directory to save structured JSON files.
            api_manager: The client manager for making LLM API calls.
        """
        self.annotated_data_dir = Path(annotated_data_dir)
        self.structured_data_dir = Path(structured_data_dir)
        self.structured_data_dir.mkdir(parents=True, exist_ok=True)
        self.api_manager = api_manager
        self.schema = self._load_schema()

    def _load_schema(self) -> Optional[Dict[str, Any]]:
        """Loads the master JSON schema."""
        try:
            schema_path = Path('schema.json')
            with open(schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("schema.json not found! The structurer cannot operate without it.")
            return None
        except json.JSONDecodeError:
            logger.error("schema.json is not valid JSON.")
            return None

    async def run(self):
        """
        Executes the full information structuring pipeline, yielding structured data.
        """
        if not self.schema:
            logger.error("Aborting structuring process due to missing or invalid schema.")
            return

        logger.info("Starting information structuring process...")
        filepaths = list(self.annotated_data_dir.rglob("*.txt"))

        for filepath in filepaths:
            structured_data = await self._process_file(filepath)
            if structured_data:
                yield structured_data

        logger.info("Information structuring process completed.")

    async def _process_file(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """
        Processes a single annotated text file and returns structured data.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            prompt = self._create_structuring_prompt(content)
            response = await self.api_manager.make_request(prompt)

            if response and response.get("success"):
                structured_data = self._parse_llm_response(response.get("content", ""))
                if structured_data:
                    # Add source document information
                    structured_data['source_documents'] = [str(filepath.relative_to(self.annotated_data_dir))]
                    return structured_data
            else:
                logger.error(f"Failed to get a valid response for {filepath}")
                return None

        except Exception as e:
            logger.error(f"Error processing file {filepath}: {e}", exc_info=True)
            return None

    def _create_structuring_prompt(self, text: str) -> str:
        """
        Creates the precise, schema-enforcing prompt for the LLM.
        """
        prompt = (
            "You are a data structuring expert. Based on the provided text, populate the following JSON object. "
            "Adhere strictly to the schema provided below. Do NOT add any information that is not "
            "explicitly present in the text. If a field cannot be filled, omit it. Your output MUST be a single, valid JSON object.\n\n"
            f"SCHEMA:\n{json.dumps(self.schema, indent=2)}\n\n"
            f"TEXT:\n---\n{text}\n---\n\n"
            "JSON_OUTPUT:"
        )
        return prompt

    def _parse_llm_response(self, response_content: str) -> Optional[Dict[str, Any]]:
        """
        Parses the JSON object from the LLM's response string.
        """
        try:
            # The LLM might sometimes include markdown ```json ... ```
            if "```json" in response_content:
                response_content = response_content.split("```json")[1].split("```")[0]
            
            return json.loads(response_content)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from LLM response: {response_content}")
            return None
        except IndexError:
            logger.error(f"Could not parse JSON from malformed markdown: {response_content}")
            return None
