#!/usr/bin/env python3
"""
SetForge Hybrid Information Extractor
=====================================

This module extracts specific data points from text segments using a
hybrid approach of regular expressions and targeted LLM calls.
"""

import asyncio
import re
import logging
from typing import Dict, Any, Optional, List

from src.components.llm_api import VertexAIGenerator

logger = logging.getLogger("SetForge")

class InformationExtractor:
    """
    Extracts information from text segments using a hybrid approach.
    """

    def __init__(self, llm_generator: VertexAIGenerator):
        """
        Initializes the InformationExtractor.

        Args:
            llm_generator: An instance of a language model generator.
        """
        self.llm_generator = llm_generator
        self.regex_patterns = self._compile_regex_patterns()

    def _compile_regex_patterns(self) -> Dict[str, re.Pattern[str]]:
        """Compiles regex patterns for common data points."""
        patterns: Dict[str, re.Pattern[str]] = {
            "phone": re.compile(r'(\+?\d[\d\s-]{8,}\d)'),
            "email": re.compile(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'),
            "website": re.compile(r'(https?://[^\s/$.?#].[^\s]*)')
        }
        return patterns

    async def extract_information(self, segment: str, category: str) -> Optional[Dict[str, Any]]:
        """
        Extracts information from a single text segment based on its category.

        Args:
            segment: The text segment to process.
            category: The category of the document the segment belongs to.

        Returns:
            A dictionary containing the extracted information, or None.
        """
        # First, extract simple entities with regex
        extracted_data = self._extract_with_regex(segment)

        # Then, use LLM for complex, category-specific extraction
        llm_data = await self._extract_with_llm(segment, category)
        if llm_data:
            extracted_data.update(llm_data)

        return extracted_data if extracted_data else None

    def _extract_with_regex(self, segment: str) -> Dict[str, Any]:
        """Extracts data using pre-compiled regular expressions."""
        data: Dict[str, List[str]] = {"phones": [], "emails": [], "websites": []}
        
        # Using findall to get all matches
        data["phones"] = self.regex_patterns["phone"].findall(segment)
        data["emails"] = self.regex_patterns["email"].findall(segment)
        data["websites"] = self.regex_patterns["website"].findall(segment)
        
        # Return a simplified structure if only one of each is found
        simplified_data = {}
        for key, value in data.items():
            if value:
                simplified_data[key.rstrip('s')] = value[0] # e.g., phones -> phone
        
        return simplified_data

    async def _extract_with_llm(self, segment: str, category: str) -> Optional[Dict[str, Any]]:
        """Extracts complex data using a targeted LLM call."""
        prompt = self._get_llm_prompt(segment, category)
        if not prompt:
            return None

        try:
            # Add a delay before the API call to prevent rate-limiting
            await asyncio.sleep(1)
            response_text = await self.llm_generator.generate_text(prompt)
            if response_text:
                # Basic parsing of a key: value format
                data = {}
                for line in response_text.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        data[key.strip()] = value.strip()
                return data
        except Exception as e:
            logger.error(f"LLM extraction failed for category {category}: {e}", exc_info=True)
        
        return None

    def _get_llm_prompt(self, segment: str, category: str) -> Optional[str]:
        """Returns the appropriate prompt for the given category."""
        prompts = {
            "Fee_Structure": "Extract the course name, fee amount, and currency from the text.",
            "Course_Details": "Extract the program name, department, and duration in years.",
            "Scholarship_Policy": "Extract the scholarship name, eligibility criteria, and benefit details.",
            # Add more specialized prompts here
        }
        prompt_instruction = prompts.get(category)
        if not prompt_instruction:
            return None

        return f"""
        You are an expert data extractor. {prompt_instruction}
        Provide the output in a 'key: value' format, one per line.

        **Text Segment:**
        ---
        {segment}
        ---

        **Extracted Data:**
        """
