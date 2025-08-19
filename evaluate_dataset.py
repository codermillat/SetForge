import random
import os
from typing import List

def sample_dataset(input_file: str, output_file: str, sample_percentage: float = 0.05) -> None:
    """
    Randomly samples a percentage of a JSONL file.

    Args:
        input_file (str): The path to the input JSONL file.
        output_file (str): The path to the output JSONL file for the sample.
        sample_percentage (float): The percentage of lines to sample (0.0 to 1.0).
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if not lines:
            print("Input file is empty. No sample created.")
            return

        num_lines: int = len(lines)
        sample_size: int = int(num_lines * sample_percentage)
        
        if sample_size == 0 and num_lines > 0:
            sample_size = 1 # Ensure at least one sample if the file is not empty

        print(f"Total lines in dataset: {num_lines}")
        print(f"Sample size ({sample_percentage * 100}%): {sample_size}")

        sampled_lines: List[str] = random.sample(lines, sample_size)

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in sampled_lines:
                f.write(line)

        print(f"Successfully created a sample of {sample_size} lines in '{output_file}'")

    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_file}'")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    INPUT_DATASET_PATH = "data_qa/qna_dataset.jsonl"
    SAMPLED_DATASET_PATH = "data_qa/sampled_qna_dataset.jsonl"
    
    sample_dataset(INPUT_DATASET_PATH, SAMPLED_DATASET_PATH)
