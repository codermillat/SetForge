"""
This module is responsible for generating high-quality question-answer pairs
based on the structured data produced by Part 1 of the pipeline.
"""

import logging
import re
from typing import Dict, Any, List, cast
from src.utils.api_client_manager import APIClientManager # Import APIClientManager
import json # Import json for structured data handling
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QAGenerator:
    """
    Generates high-quality question-answer pairs from structured data using a language model.
    """
    def __init__(self, api_manager: APIClientManager):
        self.api_manager = api_manager
        prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'qa_generation_prompt.md')
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                self.prompt_template = f.read()
            logging.info("Successfully loaded Q&A generation prompt template.")
        except FileNotFoundError:
            logging.error(f"Prompt template file not found at: {prompt_path}")
            raise
        logging.info("QAGenerator initialized with APIClientManager.")

    async def generate_qa_pairs(self, structured_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates question-answer pairs from the given structured data using a language model.

        Args:
            structured_data (Dict[str, Any]): The structured data from which to generate Q&A.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing a 'question' and an 'answer'.
        """
        if not structured_data:
            logging.warning("Received empty structured data for Q&A generation.")
            return []

        qa_pairs: List[Dict[str, Any]] = []
        
        # Convert structured data to a string format suitable for the language model
        structured_data_str = json.dumps(structured_data, indent=2, ensure_ascii=False)

        prompt = self.prompt_template.format(structured_data_str=structured_data_str)

        try:
            # Use the API manager to get a response from the language model
            response_data = await self.api_manager.make_request(prompt)
            
            if not response_data or not response_data.get("success"):
                logging.error("Failed to get a successful response from the language model.")
                return []

            response_content = response_data.get("content", "")
            
            # Attempt to parse the response as JSON
            logging.info(f"Raw response from model:\n{response_content}")
            
            # Use regex to find the JSON array, ignoring any leading/trailing text
            json_match = re.search(r'\[.*\]', response_content, re.DOTALL)
            
            if not json_match:
                logging.error("No valid JSON array found in the model's response.")
                return []

            json_string = json_match.group(0)

            try:
                # The model is expected to return a JSON array of Q&A objects.
                decoded_data: Any = json.loads(json_string)
                
                if isinstance(decoded_data, list):
                    decoded_response = cast(List[Any], decoded_data)
                    # Validate that each item in the list is a valid Q&A pair
                    for item in decoded_response:
                        if (isinstance(item, dict) and 
                            "question" in item and 
                            isinstance(item.get("question"), str) and
                            "answer" in item and 
                            isinstance(item.get("answer"), dict) and
                            "short_answer" in item["answer"] and
                            isinstance(item["answer"].get("short_answer"), str) and
                            "explanation" in item["answer"] and
                            isinstance(item["answer"].get("explanation"), str)):
                            qa_pairs.append(item)
                        else:
                            logging.warning(f"Invalid Q&A item structure: {item}")
                    
                    if len(qa_pairs) != len(decoded_response):
                        logging.warning("Some items in the decoded list were not valid Q&A pairs.")
                    
                elif isinstance(decoded_data, dict) and "question" in decoded_data and "answer" in decoded_data:
                    qa_pairs.append(cast(Dict[str, Any], decoded_data))
                else:
                    logging.warning("Decoded JSON is not a list or a valid Q&A object.")

            except json.JSONDecodeError as e:
                logging.error(f"Failed to decode JSON response: {e}", exc_info=True)

            logging.info(f"Successfully generated {len(qa_pairs)} Q&A pairs.")

        except Exception as e: # Catch all other exceptions
            logging.error(f"Error during Q&A generation: {e}", exc_info=True)

        return qa_pairs

if __name__ == "__main__":
    import asyncio
    from src.utils.config_manager import ConfigManager
    from logging import getLogger

    async def main():
        # Initialize ConfigManager and APIClientManager for testing
        config = ConfigManager()
        logger = getLogger(__name__)
        api_manager = APIClientManager(config, logger)

        generator = QAGenerator(api_manager)

        sample_structured_data: Dict[str, Any] = {
            "title": "Sharda University B.Tech CSE Course Details",
            "description": "This document provides comprehensive details about the B.Tech Computer Science Engineering course at Sharda University, including fees, admission criteria, and curriculum.",
            "fees": {
                "tuition": "150000 INR",
                "hostel": "80000 INR"
            },
            "admission_criteria": {
                "eligibility": "10+2 with PCM",
                "entrance_exam": "JEE Main"
            }
        }

        qa_results = await generator.generate_qa_pairs(sample_structured_data)

        if qa_results:
            print("\nGenerated Q&A Pairs:")
            for qa in qa_results:
                print(f"Q: {qa['question']}")
                print(f"A: {qa['answer']}")
        else:
            print("No Q&A pairs generated.")

        # Example with more complex data (conceptual)
        complex_structured_data: Dict[str, Any] = {
            "university": "Amity University",
            "campuses": [
                {"name": "Noida", "courses": [{"name": "B.Tech IT", "fees": "200000 INR"}]},
                {"name": "Lucknow", "courses": [{"name": "B.Tech CSE", "fees": "180000 INR"}]}
            ],
            "government_service": {
                "service_name": "Passport Application",
                "requirements": ["Proof of Address", "Proof of Identity"],
                "process_steps": ["Fill form", "Submit documents", "Biometrics"]
            }
        }
        print("\nAttempting Q&A generation for complex data (conceptual):")
        complex_qa_results = await generator.generate_qa_pairs(complex_structured_data)
        if complex_qa_results:
            print("\nGenerated Q&A Pairs for complex data:")
            for qa in complex_qa_results:
                print(f"Q: {qa['question']}")
                print(f"A: {qa['answer']}")
        else:
            print("No Q&A pairs generated for complex data.")

        await api_manager.close_session()

    asyncio.run(main())
