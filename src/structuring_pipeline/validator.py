import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataValidator:
    """
    Validates extracted data against a JSON schema and enriches it with metadata.
    """
    def __init__(self, schema: Dict[str, Any]):
        """
        Initializes the DataValidator.

        Args:
            schema (Dict[str, Any]): The JSON schema to validate against.
        """
        self.schema = schema

    def validate_and_enrich(self, extracted_data: Dict[str, Any], source_file: str) -> Optional[Dict[str, Any]]:
        """
        Validates the data, and if successful, enriches it with metadata.

        Args:
            extracted_data (Dict[str, Any]): The data extracted by the LLM.
            source_file (str): The original source file path for traceability.

        Returns:
            Optional[Dict[str, Any]]: The enriched data if valid, otherwise None.
        """
        try:
            # Validate the core extracted data against the schema
            validate(instance=extracted_data, schema=self.schema)
            
            # Enrich the data with metadata after successful validation
            enriched_data = extracted_data.copy()
            enriched_data['source_file'] = source_file
            enriched_data['retrieval_timestamp'] = datetime.now(timezone.utc).isoformat()
            
            logging.info(f"Data from {source_file} validated and enriched successfully.")
            return enriched_data

        except ValidationError as e:
            logging.error(f"Schema validation failed for {source_file}: {e.message}")
            logging.debug(f"Validation error details: {e}")
            return None
        except Exception as e:
            logging.error(f"An unexpected error occurred during validation for {source_file}: {e}")
            return None

if __name__ == '__main__':
    # Example Usage
    
    # 1. Load the schema
    try:
        with open('schema.json', 'r') as f:
            main_schema = json.load(f)
    except FileNotFoundError:
        print("Error: schema.json not found. Run this from the project root.")
        main_schema = None

    if main_schema:
        validator = DataValidator(schema=main_schema)

        # 2. Example of valid data (replace with a more complex example as needed)
        valid_data_example = {
            "content_type": "university_profile",
            "university_profile": {
                "university_name": "Test University",
                "course_catalog": [
                    {
                        "program_name": "Computer Science",
                        "indian_degree_name": "B.Tech",
                        "duration_years": 4
                    }
                ]
            }
        }

        # 3. Example of invalid data
        invalid_data_example = {
            "content_type": "university_profile",
            "university_profile": {
                # Missing required 'university_name'
                "course_catalog": []
            }
        }

        print("--- Testing with valid data ---")
        enriched = validator.validate_and_enrich(valid_data_example, "dummy/valid_source.html")
        if enriched:
            print("Validation successful. Enriched data:")
            print(json.dumps(enriched, indent=2))
        else:
            print("Validation failed unexpectedly.")

        print("\\n--- Testing with invalid data ---")
        enriched = validator.validate_and_enrich(invalid_data_example, "dummy/invalid_source.html")
        if not enriched:
            print("Validation failed as expected.")
        else:
            print("Validation succeeded unexpectedly.")
