#!/usr/bin/env python3
"""
Provides a centralized and robust way to manage and access JSON schemas.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("SetForge")

class SchemaProvider:
    """
    Manages loading, caching, and providing access to JSON schemas.
    """

    def __init__(self, schema_dir: str = "src/schemas"):
        """
        Initializes the SchemaProvider.

        Args:
            schema_dir: The directory where JSON schemas are stored.
        """
        self.schema_dir = Path(schema_dir)
        self._schema_cache: Dict[str, Any] = {}
        self._load_all_schemas()

    def _load_all_schemas(self):
        """
        Loads all JSON schemas from the specified directory into the cache.
        """
        if not self.schema_dir.is_dir():
            logger.warning(f"Schema directory not found: {self.schema_dir}")
            return

        for schema_file in self.schema_dir.glob("*.json"):
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                schema_name = schema_file.stem
                self._schema_cache[schema_name] = schema
                logger.info(f"Loaded schema: {schema_name}")
            except json.JSONDecodeError:
                logger.error(f"Error decoding JSON from {schema_file}")
            except Exception as e:
                logger.error(f"Error loading schema {schema_file}: {e}")

    def get_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a schema by name from the cache.

        Args:
            name: The name of the schema to retrieve (without the .json extension).

        Returns:
            The JSON schema as a dictionary, or None if not found.
        """
        return self._schema_cache.get(name)
