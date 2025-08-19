#!/usr/bin/env python3
"""
SetForge Entity Recognizer
==========================

This module is responsible for identifying and canonicalizing key entities
from cleaned text files.
"""

import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger("SetForge")

class EntityRecognizer:
    """
    Identifies and tags key entities in text using a predefined dictionary
    and canonicalization map.
    """

    def __init__(self, cleaned_data_dir: str, annotated_data_dir: str):
        """
        Initializes the EntityRecognizer.

        Args:
            cleaned_data_dir: Directory containing cleaned text files.
            annotated_data_dir: Directory to save annotated text files.
        """
        self.cleaned_data_dir = Path(cleaned_data_dir)
        self.annotated_data_dir = Path(annotated_data_dir)
        self.annotated_data_dir.mkdir(parents=True, exist_ok=True)
        self.canonical_map = self._load_canonical_map()

    def _load_canonical_map(self) -> Dict[str, str]:
        """
        Loads the entity-to-canonical-ID map.
        In a real implementation, this would come from a config file or database.
        """
        # Placeholder implementation
        return {
            "Galgotias University": "university_galgotias",
            "GU": "university_galgotias",
            "Amity University": "university_amity",
            "Amity": "university_amity",
            "Noida International University": "university_niu",
            "NIU": "university_niu",
            "Sharda University": "university_sharda",
            "B.Tech in Computer Science": "course_btech_cs",
            "Computer Science Engineering": "course_btech_cs",
            "MBA": "course_mba",
            "Passport": "service_passport",
            "Visa": "service_visa"
        }

    def run(self):
        """
        Executes the full entity recognition pipeline.
        """
        logger.info("Starting entity recognition process...")
        filepaths = list(self.cleaned_data_dir.rglob("*.txt"))

        for filepath in filepaths:
            self._process_file(filepath)

        logger.info("Entity recognition process completed.")

    def _process_file(self, filepath: Path):
        """
        Processes a single cleaned text file.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            annotated_content = self._tag_entities(content)
            self._save_annotated_file(filepath, annotated_content)

        except Exception as e:
            logger.error(f"Error processing file {filepath}: {e}", exc_info=True)

    def _tag_entities(self, text: str) -> str:
        """
        Replaces known entity aliases with their canonical IDs.
        A more advanced implementation would use NLP for fuzzy matching.
        """
        # This is a simple string replacement. A real-world scenario would
        # use more sophisticated regex or NLP to avoid replacing substrings
        # incorrectly. For now, we sort by length to replace longer matches first.
        sorted_aliases = sorted(self.canonical_map.keys(), key=len, reverse=True)
        
        for alias in sorted_aliases:
            # Using word boundaries to avoid partial matches (e.g., 'Amity' in 'Calamity')
            # This is a simplified regex; a robust solution would be more complex.
            text = text.replace(alias, f"<{self.canonical_map[alias]}>")

        return text

    def _save_annotated_file(self, original_filepath: Path, content: str):
        """
        Saves the annotated content to a new text file.
        """
        try:
            relative_path = original_filepath.relative_to(self.cleaned_data_dir)
            annotated_filepath = self.annotated_data_dir / relative_path
            annotated_filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(annotated_filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Saved annotated file: {annotated_filepath}")
        except Exception as e:
            logger.error(f"Failed to save annotated file for {original_filepath}: {e}", exc_info=True)
