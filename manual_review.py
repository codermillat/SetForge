import json
from typing import List, Dict, Any

def conduct_manual_review(input_file: str, review_file: str) -> None:
    """
    Conducts a manual review of a sampled Q&A dataset.

    Args:
        input_file (str): The path to the sampled JSONL file.
        review_file (str): The path to store the review results.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if not lines:
            print("Sampled dataset is empty. No review to conduct.")
            return

        reviews: List[Dict[str, Any]] = []
        for i, line in enumerate(lines):
            try:
                qa_pair: Dict[str, Any] = json.loads(line)
                print(f"\n--- Reviewing Q&A Pair {i+1}/{len(lines)} ---")
                print(f"Question: {qa_pair.get('question')}")
                print(f"Answer: {qa_pair.get('answer')}")
                print(f"Context: {qa_pair.get('context')}")
                print(f"Source: {qa_pair.get('source')}")
                print(f"Metadata: {qa_pair.get('metadata')}")

                while True:
                    feedback = input("Is this Q&A pair correct? (y/n): ").lower()
                    if feedback in ['y', 'n']:
                        break
                    print("Invalid input. Please enter 'y' or 'n'.")

                review: Dict[str, Any] = {
                    "qa_pair": qa_pair,
                    "is_correct": feedback == 'y'
                }
                reviews.append(review)

            except json.JSONDecodeError:
                print(f"Skipping malformed JSON on line {i+1}")
                continue

        with open(review_file, 'w', encoding='utf-8') as f:
            json.dump(reviews, f, indent=2)

        print(f"\nManual review complete. Results saved to '{review_file}'")

    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_file}'")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    SAMPLED_DATASET_PATH = "data_qa/sampled_qna_dataset.jsonl"
    REVIEW_RESULTS_PATH = "data_qa/review_results.json"
    
    conduct_manual_review(SAMPLED_DATASET_PATH, REVIEW_RESULTS_PATH)
