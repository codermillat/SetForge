#!/usr/bin/env python3
"""
SetForge Advanced Content Extractor
===================================

This module is responsible for intelligently extracting the main content
from raw HTML files, discarding boilerplate and other irrelevant noise.
"""

import logging
import re
from pathlib import Path
import trafilatura
from typing import Optional

logger = logging.getLogger("SetForge")

class ContentExtractor:
    """
    Extracts core content from HTML documents using trafilatura.
    """

    def __init__(self, raw_data_dir: str, cleaned_data_dir: str):
        """
        Initializes the ContentExtractor.

        Args:
            raw_data_dir: The directory containing the raw HTML files.
            cleaned_data_dir: The directory where cleaned text files will be saved.
        """
        self.raw_data_dir = Path(raw_data_dir)
        self.cleaned_data_dir = Path(cleaned_data_dir)
        self.cleaned_data_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        """
        Executes the full content extraction pipeline.
        """
        logger.info("Starting advanced content extraction process...")
        filepaths = list(self.raw_data_dir.rglob("*.html")) + list(self.raw_data_dir.rglob("*.txt"))

        for filepath in filepaths:
            self._process_file(filepath)

        logger.info("Advanced content extraction process completed.")

    def _process_file(self, filepath: Path):
        """
        Processes a single raw data file, handling HTML and TXT differently.

        Args:
            filepath: The path to the raw HTML or text file.
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                raw_content = f.read()

            extracted_text: Optional[str] = None

            if filepath.suffix == '.html':
                # For HTML files, use trafilatura to extract the main content
                extracted_text = trafilatura.extract(raw_content, include_comments=False, include_tables=True)
            elif filepath.suffix == '.txt':
                # For TXT files, we still perform normalization
                extracted_text = raw_content

            if extracted_text and extracted_text.strip():
                # Normalize the extracted text regardless of source
                normalized_text = self._normalize_text(extracted_text)
                self._save_cleaned_file(filepath, normalized_text)
            else:
                logger.warning(f"Could not extract meaningful content from {filepath}")

        except Exception as e:
            logger.error(f"Error processing file {filepath}: {e}", exc_info=True)

    def _normalize_text(self, text: str) -> str:
        """
        Performs advanced text normalization.

        - Replaces multiple newlines with a single one.
        - Replaces multiple spaces with a single space.
        - Removes leading/trailing whitespace from each line.
        """
        # Replace multiple newlines with a single newline
        text = re.sub(r'\n\s*\n', '\n', text)
        # Replace multiple spaces with a single space, but not newlines
        text = re.sub(r'[ \t]+', ' ', text)
        # Strip leading/trailing whitespace from the whole text
        text = text.strip()
        # Optional: Strip whitespace from each line individually
        lines = [line.strip() for line in text.split('\n')]
        return '\n'.join(lines)

    def _save_cleaned_file(self, original_filepath: Path, content: str):
        """
        Saves the cleaned content to a new text file.
        """
        try:
            # Create a corresponding path in the cleaned_data_dir
            relative_path = original_filepath.relative_to(self.raw_data_dir)
            cleaned_filepath = self.cleaned_data_dir / relative_path
            cleaned_filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(cleaned_filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Saved cleaned file: {cleaned_filepath}")
        except Exception as e:
            logger.error(f"Failed to save cleaned file for {original_filepath}: {e}", exc_info=True)
