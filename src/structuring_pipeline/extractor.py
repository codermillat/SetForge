import json
import logging
import asyncio
from typing import Dict, Any, Optional

# Assuming api_client_manager is in src/utils
from src.utils.api_client_manager import APIClientManager, ResponseData

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InformationExtractor:
    """
    Uses an LLM to extract structured information from cleaned text based on a JSON schema.
    """
    def __init__(self, api_manager: APIClientManager, schema: Dict[str, Any], prompt_template_path: str):
        """
        Initializes the InformationExtractor.

        Args:
            api_manager (APIClientManager): The manager for handling API calls to the LLM.
            schema (Dict[str, Any]): The JSON schema to guide the extraction.
            prompt_template_path (str): The file path to the prompt template.
        """
        self.api_manager = api_manager
        self.schema_str = json.dumps(schema, indent=2)
        self.prompt_template = self._load_prompt_template(prompt_template_path)

    def _load_prompt_template(self, path: str) -> str:
        """Loads the prompt template from a file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logging.error(f"Error loading prompt template from {path}: {e}")
            raise

    async def extract(self, cleaned_text: str, source_file: str) -> Dict[str, Any]:
        """
        Extracts structured information from the cleaned text.

        Args:
            cleaned_text (str): The text content to process.
            source_file (str): The original source file path for context.

        Returns:
            Dict[str, Any]: The extracted data as a dictionary, or an empty dict if extraction fails.
        """
        prompt = self.prompt_template.format(
            schema=self.schema_str,
            source_file=source_file,
            text_content=cleaned_text
        )

        response_data: Optional[ResponseData] = None
        try:
            response_data = await self.api_manager.make_request(prompt)

            if not response_data or not response_data.get("success"):
                error_reason = response_data.get('content') if response_data else 'No response'
                logging.error(f"Extraction failed for {source_file}. Reason: {error_reason}")
                return {}

            response_text = response_data["content"].strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            extracted_data = json.loads(response_text)
            logging.info(f"Successfully extracted data from {source_file}")
            return extracted_data

        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON from LLM response for {source_file}: {e}")
            if response_data:
                 logging.debug(f"LLM Raw Response Text: {response_data.get('content')}")
            return {}
        except Exception as e:
            logging.error(f"An unexpected error occurred during extraction for {source_file}: {e}")
            return {}

if __name__ == '__main__':
    # This is a placeholder for testing.
    # To run this, you would need to:
    # 1. Have a valid config.yaml and schema.json
    # 2. Create a prompt template file.
    # 3. Have a running API client manager.
    
    async def main():
        # This is a simplified setup for demonstrating the class.
        # A real test would require mocking these components.
        print("InformationExtractor script created. Requires a full pipeline setup for testing.")
        # Example:
        # from src.utils.config_manager import ConfigManager
        # from logging import getLogger
        #
        # config = ConfigManager('config.yaml')
        # logger = getLogger(__name__)
        # api_manager = APIClientManager(config, logger)
        #
        # with open('schema.json', 'r') as f:
        #     schema = json.load(f)
        #
        # # Create a dummy prompt file for testing
        # with open('src/prompts/structuring/test_prompt.md', 'w') as f:
        #     f.write("Extract data based on this schema: {schema}\\n\\nFile: {source_file}\\n\\nContent:\\n{text_content}")
        #
        # extractor = InformationExtractor(api_manager, schema, 'src/prompts/structuring/test_prompt.md')
        #
        # # Dummy data
        # text = "University: TestU, Program: CS, Duration: 4 years"
        # source = "dummy/file.txt"
        #
        # result = await extractor.extract(text, source)
        # print("Extraction result:", result)
        #
        # await api_manager.close_session()

    if __name__ == "__main__":
        # To run this in a real scenario, you'd use asyncio.run(main())
        asyncio.run(main())
