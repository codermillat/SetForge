from pathlib import Path

def find_missing_structured_files():
    data_dir = Path("data")
    structured_dir = Path("data_structured")

    raw_files = {p.stem for p in data_dir.rglob("*.txt")}
    structured_files = {p.stem.replace('_structured', '') for p in structured_dir.rglob("*.json")}

    missing_files = raw_files - structured_files

    if not missing_files:
        print("All raw files have a corresponding structured file.")
    else:
        print("The following raw files are missing a corresponding structured file:")
        for missing_file in sorted(missing_files):
            print(missing_file)

if __name__ == "__main__":
    find_missing_structured_files()
