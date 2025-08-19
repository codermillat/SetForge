import asyncio
import json
import os
import logging
from typing import Dict, Any

from src.pipeline.qa_generator import QAGenerator
from src.utils.api_client_manager import APIClientManager
from src.utils.config_manager import ConfigManager

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_sample_files():
    """
    Loads a list of sample structured data files and runs them through the QAGenerator.
    """
    # Initialize managers
    config = ConfigManager()
    logger = logging.getLogger(__name__)
    api_manager = APIClientManager(config, logger)
    generator = QAGenerator(api_manager)

    # List of sample files to test
    sample_files = [
        "data_structured/global.sharda.ac.in_Bangladesh_-_Admissions_Open_2025-26_Apply_Now_at_Sharda_University_India_raw_2025-08-10-18-50-50_structured.json",
        "data_structured/niu.edu.in_Eligibility_Criteria_and_Fee_Structure_Noida_International_University_raw_2025-08-10-18-48-38_structured.json",
        "data_structured/admissions.galgotiasuniversity.edu.in_Home_raw_2025-08-10-20-22-14_structured.json"
    ]

    for file_path in sample_files:
        if not os.path.exists(file_path):
            logging.warning(f"Sample file not found: {file_path}. Skipping.")
            continue

        logging.info(f"--- Testing with file: {file_path} ---")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                structured_data: Dict[str, Any] = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Failed to read or parse {file_path}: {e}")
            continue

        # Generate Q&A pairs
        qa_results = await generator.generate_qa_pairs(structured_data)

        if qa_results:
            print(f"\nGenerated {len(qa_results)} Q&A Pairs for {os.path.basename(file_path)}:")
            for i, qa in enumerate(qa_results, 1):
                print(f"\n--- Q&A Pair {i} ---")
                print(f"Q: {qa.get('question', 'N/A')}")
                print(f"A: {qa.get('answer', 'N/A')}")
        else:
            print(f"\nNo Q&A pairs generated for {os.path.basename(file_path)}.")
        
        print("-" * 50)

    # Clean up
    await api_manager.close_session()

if __name__ == "__main__":
    # To run this test, execute `python test_qa_generator.py` from the root directory.
    # Ensure that the PYTHONPATH is set up correctly if you encounter module import errors.
    # For example: export PYTHONPATH=$PYTHONPATH:/path/to/your/project
    # A better way is to run as a module from the root: `python -m test_qa_generator`
    # but that requires the file to be in a package.
    
    # Setting up the python path to include the root directory for src imports
    import sys
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    asyncio.run(test_sample_files())
