#!/usr/bin/env python3
"""
SetForge Prompt Engineering Component
=====================================

This module provides a sophisticated prompt engineering component for SetForge,
designed to generate high-quality, contextual prompts for entity and attribute
extraction from educational and university-related texts.
"""

import json
from enum import Enum, auto
from typing import Dict, Any, List

class PromptType(Enum):
    """
    Enum for the different types of prompts that can be generated.
    """
    ENTITY_EXTRACTION = auto()
    ATTRIBUTE_EXTRACTION = auto()

class PromptEngine:
    """
    A sophisticated prompt engineering component for SetForge. It uses few-shot
    learning examples to guide the model towards better and more consistent output.
    """

    def create_prompt(self, prompt_type: PromptType, **kwargs: Any) -> str:
        """
        Creates a prompt for the given prompt type.

        Args:
            prompt_type: The type of prompt to create.
            **kwargs: The arguments for the prompt.

        Returns:
            The created prompt as a string.
        """
        if prompt_type == PromptType.ENTITY_EXTRACTION:
            return self._create_entity_extraction_prompt(
                text=kwargs.get("text", ""),
                filename=kwargs.get("filename", "")
            )
        elif prompt_type == PromptType.ATTRIBUTE_EXTRACTION:
            return self._create_attribute_extraction_prompt(
                text=kwargs.get("text", ""),
                entity_name=kwargs.get("entity_name", ""),
                all_entities=kwargs.get("all_entities", {})
            )
        else:
            raise ValueError(f"Invalid prompt type: {prompt_type}")

    def _create_entity_extraction_prompt(self, text: str, filename: str) -> str:
        """
        Creates a prompt for entity extraction using a few-shot approach.
        """
        # Example of a good input text and the desired JSON output
        few_shot_example = """
        Example Input Text:
        "Sharda University offers a B.Tech in Computer Science. Located in Greater Noida, the tuition fee is Rs. 1,50,000 per year. Applicants need a minimum of 60% in their 12th-grade exams. The program duration is 4 years."

        Example Output JSON:
        {
          "University": ["Sharda University"],
          "Course": ["B.Tech in Computer Science"],
          "Degree": ["B.Tech"],
          "Location": ["Greater Noida"],
          "Currency": ["Rs. 1,50,000"],
          "EligibilityCriterion": ["Minimum 60% in 12th Grade"]
        }
        """

        return f"""
        You are an expert data extractor. Your task is to extract key entities from the provided text, using the filename as a primary clue.
        The entities to extract are:
        - University: The name of the university or educational institution.
        - Course: The name of the specific course or program.
        - Degree: The type of degree (e.g., B.Tech, MBA, PhD).
        - Location: The city or campus where the university is located.
        - Currency: Any mention of tuition fees or costs.
        - EligibilityCriterion: Specific requirements for admission.

        Follow these rules:
        1.  **Analyze the filename first**: The filename is a strong indicator of the document's main subject.
        2.  Return the output as a valid JSON object.
        3.  If an entity is not found, do not include the key in the JSON. Do NOT use "N/A" or null.
        4.  If you find multiple distinct values for an entity, return them as a list of strings.

        {few_shot_example}

        Now, extract the entities from the following text:

        Filename: {filename}
        Input Text:
        "{text}"

        Output JSON:
        """

    def _create_attribute_extraction_prompt(self, text: str, entity_name: str, all_entities: Dict[str, List[str]]) -> str:
        """
        Creates a prompt for attribute extraction for a specific entity, using a
        few-shot approach and providing the context of all co-occurring entities.
        """
        # Example to guide the model
        few_shot_example = """
        Example Input Text:
        "Sharda University's B.Tech in Computer Science is a 4-year program. The annual fee is Rs. 1,50,000. The application deadline is July 31st. Prerequisites include Physics, Chemistry, and Maths in 12th grade."

        Example entity_name: "B.Tech in Computer Science"
        
        Example all_entities:
        {
            "University": ["Sharda University"],
            "Course": ["B.Tech in Computer Science"],
            "Location": ["Greater Noida"]
        }

        Example Output JSON:
        {
          "TuitionFee": "Rs. 1,50,000 per year",
          "Duration": "4 years",
          "Prerequisites": "Physics, Chemistry, and Maths in 12th grade",
          "ApplicationDeadline": "July 31st"
        }
        """

        return f"""
        You are a specialized data extractor. Your task is to extract specific attributes for the given entity from the text.
        The attributes to extract are:
        - TuitionFee: The cost of the course.
        - Duration: The length of the course.
        - Prerequisites: The requirements needed to apply for the course.
        - ApplicationDeadline: The final date for applications.

        Follow these rules:
        1.  Focus ONLY on the entity: "{entity_name}".
        2.  Use the context of all co-occurring entities to find the correct attributes.
        3.  Return the output as a valid JSON object.
        4.  If an attribute is not found, do not include the key in the JSON. Do NOT use "N/A" or null.

        Context (All Entities Found in Text):
        {json.dumps(all_entities, indent=2)}

        {few_shot_example}

        Now, extract the attributes for "{entity_name}" from the following text:

        Input Text:
        "{text}"

        Output JSON:
        """
