#!/usr/bin/env python3
"""
SetForge Data Cleaner
=====================

This script cleans and pre-processes the raw text files scraped from various
websites. It handles deduplication, noise removal, and basic text normalization
to prepare the data for the structuring phase.
"""

import re
import hashlib
from pathlib import Path
from typing import Set, List
from simhash import Simhash
import logging

logger = logging.getLogger("SetForge")

class DataCleaner:
    """
    Cleans and pre-processes raw text data for the SetForge project.
    """

    def __init__(self, raw_data_dir: str, cleaned_data_dir: str):
        """
        Initializes the DataCleaner.

        Args:
            raw_data_dir: The directory containing the raw text files.
            cleaned_data_dir: The directory where cleaned files will be saved.
        """
        self.raw_data_dir = Path(raw_data_dir)
        self.cleaned_data_dir = Path(cleaned_data_dir)
        self.seen_hashes: Set[str] = set()
        self.seen_simhashes: List[Simhash] = []

    def run(self):
        """
        Executes the full data cleaning pipeline.
        """
        logger.info("Starting data cleaning process...")
        self.cleaned_data_dir.mkdir(parents=True, exist_ok=True)

        for filepath in self.raw_data_dir.rglob("*.txt"):
            self._process_file(filepath)

        logger.info("Data cleaning process completed.")

    def _process_file(self, filepath: Path):
        """
        Processes a single raw data file.

        Args:
            filepath: The path to the raw text file.
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # 1. Deduplication
            if self._is_duplicate(content):
                logger.warning(f"Skipping duplicate file: {filepath}")
                return

            # 2. Noise Removal
            cleaned_content = self._remove_noise(content)

            # 3. Normalization
            normalized_content = self._normalize_text(cleaned_content)

            # Save the cleaned file
            self._save_cleaned_file(filepath, normalized_content)

        except Exception as e:
            logger.error(f"Error processing file {filepath}: {e}")

    def _is_duplicate(self, content: str) -> bool:
        """
        Checks if the content is a duplicate using MD5 and Simhash.

        Args:
            content: The text content of the file.

        Returns:
            True if the content is a duplicate, False otherwise.
        """
        # MD5 for exact duplicates
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        if content_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(content_hash)

        # Simhash for near-duplicates
        try:
            simhash = Simhash(content)
            for sh in self.seen_simhashes:
                if simhash.distance(sh) < 3:  # Threshold for near-duplicates
                    return True
            self.seen_simhashes.append(simhash)
        except Exception as e:
            logger.warning(f"Could not compute simhash for document: {e}")

        return False

    def _remove_noise(self, content: str) -> str:
        """
        Removes common web boilerplate and other noise from the text.

        Args:
            content: The raw text content.

        Returns:
            The cleaned text content.
        """
        # Remove common navigation and footer text
        patterns_to_remove = [
            r"Home\s*>\s*.*",
            r"Copyright\s*©\s*\d{4}.*",
            r"All\s*Rights\s*Reserved",
            r"Designed\s*and\s*Developed\s*by.*",
            r"Privacy\s*Policy",
            r"Terms\s*of\s*Use",
            r"Contact\s*Us",
            r"About\s*Us",
            r"Sitemap",
            r"Login",
            r"Register",
            r"Search\s*...",
            r"Enter\s*your\s*search\s*query",
            # Amity specific
            r"Amity\s*University\s*Online",
            r"Campus\s*Helpline\s*Numbers",
            r"Admission\s*helpline:",
            r"Last\s*date\s*to\s*apply",
            r"Campus\s*Tour\s*available",
            # Sharda specific
            r"Sharda\s*Launchpad",
            # General
            r"Apply\s*Now\s*\d{4}",
            r"360°\s*VIEW",
            r"Campus\s*Tour\s*Timings",
            r"Amity\s*Universe",
            r"Amity\s*Global\s*Business\s*Schools",
            r"Regular\s*Courses",
            r"Evening\s*Courses",
            r"3\s*Continent\s*Programs",
            r"International\s*/\s*Dual\s*Degree\s*Programs",
            r"Amity\s*University\s*Press",
            r"Directorate\s*of\s*Innovation\s*and\s*Technology\s*Transfer",
            r"Amity\s*Science,\s*Technology\s*&\s*Innovation\s*Foundation",
            r"Amity\s*Indian\s*Military\s*College",
            r"Amity\s*University\s*Summer\s*School",
            r"ADMISSION\s*HELPLINE\s*NUMBER",
            r"Send\s*Query\s*over\s*WHATSAPP",
            r"Toll-Free\s*Number",
            r"Website\s*Designed\s*and\s*Developed\s*by.*",
            r"For\s*Admissions\s*and\s*Scholarships",
            r"Recruiters\s*Section",
            r"GT&C\s*For\s*Online\s*Payments",
        ]
        for pattern in patterns_to_remove:
            content = re.sub(pattern, "", content, flags=re.IGNORECASE | re.DOTALL)

        # Remove lines with excessive special characters or very short lines
        cleaned_lines = []
        for line in content.splitlines():
            line = line.strip()
            if len(line) < 3:  # Keep slightly shorter lines
                continue
            # Be more lenient with special characters, as they can be part of fee structures
            if sum(c in "!@#$%^&*()[]{};<>?|`~=_+" for c in line) / (len(line) + 1) < 0.5:
                cleaned_lines.append(line)
        
        content = "\n".join(cleaned_lines)

        return content

    def _normalize_text(self, content: str) -> str:
        """
        Normalizes whitespace and performs other text cleanup.

        Args:
            content: The text content.

        Returns:
            The normalized text content.
        """
        # Replace multiple newlines with a single newline
        content = re.sub(r'\n\s*\n', '\n\n', content)
        # Replace multiple spaces with a single space
        content = re.sub(r' +', ' ', content)
        # Remove leading/trailing whitespace from each line
        content = "\n".join(line.strip() for line in content.splitlines())

        return content.strip()

    def _save_cleaned_file(self, original_filepath: Path, content: str):
        """
        Saves the cleaned content to a new file.

        Args:
            original_filepath: The path of the original raw file.
            content: The cleaned text content.
        """
        relative_path = original_filepath.relative_to(self.raw_data_dir)
        cleaned_filepath = self.cleaned_data_dir / relative_path
        cleaned_filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(cleaned_filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Saved cleaned file: {cleaned_filepath}")
