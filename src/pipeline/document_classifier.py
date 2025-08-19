#!/usr/bin/env python3
"""
SetForge Document Classifier
============================

This module is responsible for classifying documents into predefined categories
to enable specialized downstream processing.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from src.components.llm_api import VertexAIGenerator

logger = logging.getLogger("SetForge")

class DocumentClassifier:
    """
    Classifies documents using a zero-shot approach with an LLM.
    """

    def __init__(self, llm_generator: VertexAIGenerator):
        """
        Initializes the DocumentClassifier.

        Args:
            llm_generator: An instance of a language model generator.
        """
        self.llm_generator = llm_generator
        self.classification_prompt_template = self._create_prompt_template()

    def _create_prompt_template(self) -> str:
        """Creates the prompt template for classification."""
        return """
        You are an expert document classifier for an academic advisory service.
        Your task is to classify the following document content into one of the predefined categories.
        Provide only the category name as the output.

        **Categories:**
        - Fee_Structure
        - Course_Details
        - Scholarship_Policy
        - Admission_Procedure
        - Hostel_Information
        - Visa_Information
        - Passport_Information
        - FRRO_Information
        - General_University_Info
        - General_Government_Info

        **Document Content:**
        ---
        {document_content}
        ---

        **Category:**
        """

    async def classify_document(self, content: str) -> Optional[str]:
        """
        Classifies a single document's content.

        Args:
            content: The text content of the document.

        Returns:
            The classified category name, or None if classification fails.
        """
        try:
            prompt = self.classification_prompt_template.format(document_content=content[:4000]) # Truncate for safety
            category = await self.llm_generator.generate_text(prompt)
            
            if category and category.strip() in self._get_valid_categories():
                return category.strip()
            else:
                logger.warning(f"LLM returned an invalid or empty category: {category}")
                return "General_Info" # Fallback category

        except Exception as e:
            logger.error(f"Error during document classification: {e}", exc_info=True)
            return None

    def _get_valid_categories(self) -> List[str]:
        """Returns a list of valid category names."""
        return [
            "Fee_Structure", "Course_Details", "Scholarship_Policy",
            "Admission_Procedure", "Hostel_Information", "Visa_Information",
            "Passport_Information", "FRRO_Information", "General_University_Info",
            "General_Government_Info"
        ]
