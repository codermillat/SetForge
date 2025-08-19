#!/usr/bin/env python3
"""
SetForge Data Validator
=======================

This module is the quality assurance gate for the pipeline. It validates
structured data against the master JSON schema.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional
import jsonschema

logger = logging.getLogger("SetForge")

def _load_schema() -> Optional[Dict[str, Any]]:
    """Loads the master JSON schema."""
    try:
        schema_path = Path('schema.json')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        # Check if the schema itself is valid
        jsonschema.Draft7Validator.check_schema(schema)
        logger.info("Master JSON schema loaded and validated successfully.")
        return schema
    except FileNotFoundError:
        logger.error("schema.json not found! The validator cannot operate.")
        return None
    except json.JSONDecodeError:
        logger.error("schema.json is not a valid JSON file.")
        return None
    except jsonschema.SchemaError as e:
        logger.error(f"Master schema.json is invalid: {e}")
        return None

class DataValidator:
    """
    Validates structured JSON data against a predefined schema.
    """

    def __init__(self):
        """Initializes the DataValidator."""
        self.schema = _load_schema()

    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validates a single data object against the master schema.

        Args:
            data: The structured data object to validate.

        Returns:
            True if the data is valid, False otherwise.
        """
        if not self.schema:
            logger.error("Cannot validate data: Schema is not loaded.")
            return False

        try:
            jsonschema.validate(instance=data, schema=self.schema)
            logger.debug("Data validation successful.")
            return True
        except jsonschema.ValidationError as e:
            logger.warning(f"Data validation failed: {e.message}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during validation: {e}")
            return False
