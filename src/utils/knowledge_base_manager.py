#!/usr/bin/env python3
"""
SetForge Knowledge Base Manager
===============================

This module handles the storage and deduplication of structured,
validated knowledge units.
"""

import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("SetForge")

class KnowledgeBaseManager:
    """
    Manages the saving and deduplication of knowledge units.
    """

    def __init__(self, structured_data_dir: str):
        """
        Initializes the KnowledgeBaseManager.

        Args:
            structured_data_dir: The directory where structured data is stored.
        """
        self.structured_data_dir = Path(structured_data_dir)
        self.structured_data_dir.mkdir(parents=True, exist_ok=True)

    def add_unit_id(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generates and adds a unique unit_id to the data object.
        Returns the object with the ID, or None if key fields are missing.
        """
        canonical_name = data.get("canonical_name")
        entity_type = data.get("entity_type")

        if not canonical_name or not entity_type:
            return None
        
        unit_id = self._generate_unit_id(canonical_name, entity_type)
        data['unit_id'] = unit_id
        return data

    def save_knowledge_unit(self, data: Dict[str, Any]):
        """
        Saves a validated and ID'd knowledge unit.

        Args:
            data: The validated, structured data object with a unit_id.
        """
        unit_id = data.get("unit_id")
        if not unit_id:
            logger.error("Cannot save knowledge unit: missing unit_id.")
            return

        filepath = self.structured_data_dir / f"{unit_id}.json"

        # Simple deduplication: if a file with this ID exists, we can
        # implement merging logic. For now, we'll just overwrite.
        if filepath.exists():
            logger.info(f"Knowledge unit {unit_id} already exists. Overwriting.")

        self._save_to_file(filepath, data)

    def _generate_unit_id(self, canonical_name: str, entity_type: str) -> str:
        """
        Generates a consistent, unique hash-based ID for a knowledge unit.
        """
        # Create a stable string from the core identifying information
        id_string = f"{entity_type}:{canonical_name}"
        # Use SHA256 for a stable and unique hash
        return hashlib.sha256(id_string.encode('utf-8')).hexdigest()

    def _save_to_file(self, filepath: Path, data: Dict[str, Any]):
        """
        Saves the dictionary to a JSON file.
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            logger.info(f"Saved knowledge unit to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save knowledge unit to {filepath}: {e}", exc_info=True)
