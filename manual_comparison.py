from pathlib import Path
from typing import Set

def manual_comparison():
    data_dir = Path("data")
    structured_dir = Path("data_structured")

    raw_files = {p for p in data_dir.rglob("*.txt") if "dead_letter_queue" not in str(p)}
    
    expected_structured_files: Set[str] = set()
    for raw_file in raw_files:
        # This is tricky because the directory structure is flattened.
        # We will just use the name of the file.
        expected_name = raw_file.name.replace('.txt', '_structured.json')
        expected_structured_files.add(expected_name)

    actual_structured_files: Set[str] = {p.name for p in structured_dir.rglob("*.json")}

    missing_files: Set[str] = expected_structured_files - actual_structured_files

    print(f"Total raw files: {len(raw_files)}")
    print(f"Total structured files: {len(actual_structured_files)}")

    if not missing_files:
        print("All raw files have a corresponding structured file.")
    else:
        print("The following raw files are missing a corresponding structured file:")
        for missing_file in sorted(missing_files):
            print(missing_file.replace('_structured.json', '.txt'))

if __name__ == "__main__":
    manual_comparison()
