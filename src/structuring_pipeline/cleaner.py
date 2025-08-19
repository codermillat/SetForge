import os
import logging
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataCleaner:
    """
    Parses raw HTML files to extract clean, readable text content.
    """
    def __init__(self, raw_data_dir: str, cleaned_data_dir: str):
        """
        Initializes the DataCleaner.

        Args:
            raw_data_dir (str): The directory containing raw HTML files.
            cleaned_data_dir (str): The directory where cleaned text files will be saved.
        """
        self.raw_data_dir = raw_data_dir
        self.cleaned_data_dir = cleaned_data_dir
        if not os.path.exists(self.cleaned_data_dir):
            os.makedirs(self.cleaned_data_dir)
            logging.info(f"Created directory: {self.cleaned_data_dir}")

    def clean_html_file(self, file_path: str) -> str:
        """
        Reads an HTML file, extracts the main text content, and cleans it.

        Args:
            file_path (str): The full path to the HTML file.

        Returns:
            str: The cleaned text content, or an empty string if an error occurs.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')

            # Remove script, style, header, footer, and navigation elements
            for element in soup(["script", "style", "header", "footer", "nav"]):
                element.decompose()

            # Get text and clean it up
            text = soup.get_text(separator='\\n', strip=True)
            
            # Further cleaning can be added here (e.g., regex to remove extra whitespace)
            
            return text

        except Exception as e:
            logging.error(f"Error cleaning file {file_path}: {e}")
            return ""

    def process_file(self, relative_file_path: str) -> str:
        """
        Processes a single file: cleans it and saves the output.

        Args:
            relative_file_path (str): The path of the file relative to the raw_data_dir.

        Returns:
            str: The path to the cleaned file, or an empty string if processing fails.
        """
        raw_file_full_path = os.path.join(self.raw_data_dir, relative_file_path)
        
        if not os.path.exists(raw_file_full_path):
            logging.warning(f"File not found: {raw_file_full_path}")
            return ""

        cleaned_text = self.clean_html_file(raw_file_full_path)

        if cleaned_text:
            # Construct the output path maintaining the directory structure
            cleaned_file_path = os.path.join(self.cleaned_data_dir, relative_file_path)
            cleaned_file_dir = os.path.dirname(cleaned_file_path)

            if not os.path.exists(cleaned_file_dir):
                os.makedirs(cleaned_file_dir)

            try:
                with open(cleaned_file_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_text)
                logging.info(f"Successfully cleaned and saved: {cleaned_file_path}")
                return cleaned_file_path
            except Exception as e:
                logging.error(f"Error writing cleaned file {cleaned_file_path}: {e}")
                return ""
        
        return ""

if __name__ == '__main__':
    # Example usage:
    # This allows the script to be tested standalone.
    
    # Assume the script is run from the root of the project directory
    RAW_DIR = 'data' 
    CLEANED_DIR = 'data_cleaned'
    
    cleaner = DataCleaner(raw_data_dir=RAW_DIR, cleaned_data_dir=CLEANED_DIR)
    
    # Example of processing a single file
    # Replace with a real file path from your data directory for testing
    test_file = 'sharda.ac.in/B_Tech_Computer_Science_CSE_College_in_Noida_-_Courses_Details_Fees_Admissio_raw_2025-08-10-18-29-23'
    
    # To run this test, you would need to create a dummy file at the path above,
    # or change the path to an existing file in your `data` directory.
    # For example:
    # if os.path.exists(os.path.join(RAW_DIR, test_file)):
    #     cleaner.process_file(test_file)
    # else:
    #     print(f"Test file not found: {os.path.join(RAW_DIR, test_file)}")

    print("DataCleaner script finished. Run with a valid file path for testing.")
