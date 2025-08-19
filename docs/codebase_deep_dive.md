# Codebase Deep Dive: SetForge Pipeline

This document provides a detailed, function-by-function analysis of the SetForge codebase. It is intended for developers who wish to understand the internal workings, algorithms, and design patterns used throughout the project.

## Table of Contents

1.  [**Core Utilities**](#1-core-utilities)
    -   `src/utils/config_manager.py`: Configuration Handling
    -   `src/utils/api_client_manager.py`: API Interaction & Resilience
    -   `src/utils/json_parser.py`: Robust JSON Extraction
    -   `src/utils/prompt_provider.py` & `schema_provider.py`: Asset Management
2.  [**Part 1: The Knowledge Forge**](#2-part-1-the-knowledge-forge)
    -   `run.py`: Primary Entry Point
    -   `production_pipeline.py`: Orchestration
    -   `src/pipeline/content_extractor.py`: Content Cleaning
    -   `src/pipeline/data_structuring.py`: Core Structuring Logic
    -   `src/components/document_splitter.py`: Semantic Chunking
    -   `src/components/knowledge_aggregator.py`: Data Aggregation
3.  [**Part 2: The Q&A Forge**](#3-part-2-the-qa-forge)
    -   `run_qa_pipeline.py`: Pipeline Orchestration
    -   `src/pipeline/qa_generator.py`: Q&A Pair Generation
4.  [**Part 3: The Quality Assurance Forge**](#4-part-3-the-quality-assurance-forge)
    -   `run_quality_assurance.py`: Deduplication Logic

---

## 1. Core Utilities

These modules provide foundational services used across all parts of the pipeline.

### `src/utils/config_manager.py`

-   **Purpose**: To load the `config.yaml` file and provide easy, attribute-style access to its contents.
-   **Key Functions**:
    -   `__init__`: Loads the YAML file into a nested dictionary.
    -   `__getattr__`: This magic method is the core of the utility. It allows accessing dictionary keys as if they were object attributes (e.g., `config.data_config.raw_dir` instead of `config['data_config']['raw_dir']`). It recursively wraps nested dictionaries in new `ConfigManager` instances, so this convenient access works at any depth.
    -   `update_from_args`: Allows command-line arguments from `run.py` to override settings from the `config.yaml` file, providing dynamic control over the pipeline.

### `src/utils/api_client_manager.py`

-   **Purpose**: A highly resilient and sophisticated client for managing interactions with multiple LLM APIs. This is a critical component for the project's scalability and cost-management.
-   **Key Functions**:
    -   `_initialize_clients`: Reads the `api_providers` list from the config. For each provider, it creates a configuration dictionary and initializes two `AsyncRateLimiter` instances: one for Requests Per Minute (RPM) and one for Tokens Per Minute (TPM). It then sorts the clients to prioritize `paid` tiers over `free` tiers.
    -   `get_available_client`: Implements a round-robin scheduling algorithm. It checks the next client in a `deque` (a highly efficient queue). If a client is in a cool-down period (due to a previous error) or has hit its rate limit, it is rotated to the back of the queue, and the next one is checked. This ensures traffic is spread evenly and failed clients are temporarily sidelined.
    -   `make_request`: The main public method. It acquires an available client, then wraps the actual API call in the client's rate limiters (`async with client['rate_limiter'], ...`). It handles exceptions like HTTP 429 (Too Many Requests) by parsing the `Retry-After` header and setting the cool-down time for that specific client.
    -   `_make_vertex_request` & `_make_studio_request`: These methods handle the provider-specific logic for making the actual API call, one using the Vertex AI SDK and the other using `aiohttp` for direct REST API calls to Google AI Studio.

### `src/utils/json_parser.py`

-   **Purpose**: To robustly extract a JSON object or array from the raw text response of an LLM.
-   **Key Functions**:
    -   `extract_json_from_response`: This function is designed to be tolerant of common LLM response quirks. It first looks for a markdown JSON block (```json ... ```). If that's not found, it uses a broader regex (`\{[\s\S]*\}|\[[\s\S]*\]`) to find the first valid JSON-like structure. It also includes a fallback mechanism to fix common errors like trailing commas before attempting to parse.

### `src/utils/prompt_provider.py` & `schema_provider.py`

-   **Purpose**: To centralize the loading and management of text-based assets like prompts and schemas.
-   **Key Functions**:
    -   `_load_all_prompts` (in `prompt_provider.py`): On initialization, it scans the `src/prompts/` directory, reads every `.txt` file, and loads its content into a dictionary (cache) where the key is the filename (without extension).
    -   `get_prompt`: Retrieves a specific prompt from the cache by its name. This is used by the `DataStructurer` to dynamically select the correct prompt for a given topic.
    -   The `schema_provider.py` works identically, but for `.json` files in the `src/schemas/` directory.

---

## 2. Part 1: The Knowledge Forge

This pipeline is responsible for the "data preparation" phase, turning raw web content into a structured knowledge base.

### `run.py`: Primary Entry Point

-   **Purpose**: The main command-line interface for orchestrating the entire pipeline, with a focus on Part 1.
-   **Key Functions**:
    -   `parse_arguments`: Uses Python's `argparse` library to define a rich set of command-line arguments, such as `--mode`, `--steps`, `--target`, and `--quality`. This allows for flexible control over the pipeline's execution without modifying the code.
    -   `main`: The primary execution function. It initializes the `ConfigManager` and `logger`, validates the environment, and then calls the appropriate pipeline runner (`run_production_pipeline`, `run_test_pipeline`, etc.) based on the `--mode` argument. It also updates the configuration with any provided command-line arguments.

### `production_pipeline.py`: Orchestration

-   **Purpose**: Contains the `SetForgeProductionPipeline` class, which orchestrates the high-level steps of the Knowledge Forge.
-   **Key Functions**:
    -   `run`: The main method. It first calls `_setup_pipeline` to ensure all necessary data directories exist. It then executes the core processing steps based on the `steps` defined in the configuration (e.g., `['clean', 'structure']`).
    -   `_load_and_process_contexts`: This function instantiates and runs the main components. It creates an instance of `ContentExtractor` and runs it, then creates an instance of `DataStructurer` and runs it. This separation of concerns keeps the orchestration logic clean.

### `src/pipeline/content_extractor.py`

-   **Purpose**: To extract the main content from raw source files and normalize it.
-   **Key Functions**:
    -   `run`: Iterates through all `.html` and `.txt` files found in the `raw_data_dir`.
    -   `_process_file`: Reads the content of a file. If it's HTML, it uses `trafilatura.extract` to intelligently remove boilerplate and extract the core text.
    -   `_normalize_text`: Uses regular expressions to clean up the extracted text, standardizing whitespace and removing excessive blank lines.
    -   `_save_cleaned_file`: Saves the processed, clean text to the `cleaned_data_dir`, maintaining the original file's relative path for organization.

### `src/pipeline/data_structuring.py`

-   **Purpose**: The heart of the Knowledge Forge. This module orchestrates the complex, multi-stage process of structuring the cleaned text.
-   **Key Functions**:
    -   `run`: The entry point. It finds all cleaned text files and creates an `asyncio` task for each one, using `tqdm.asyncio` to display a progress bar for the concurrent operations.
    -   `_process_file`: This is the main workflow for a single file. It's wrapped in a semaphore to limit concurrency. Its steps are:
        1.  Call the `DocumentSplitter` to get topic-based text chunks.
        2.  Iterate through each chunk, calling `_structure_chunk` to process it.
        3.  Pass the list of structured chunks to the `KnowledgeAggregator`.
        4.  Save the final, aggregated JSON object.
        5.  Includes robust `try...except` blocks to catch errors and move failed files to a dead-letter queue.
    -   `_structure_chunk`: This is where the core LLM interaction happens. It dynamically gets the correct prompt and schema for the chunk's topic using the `PromptProvider` and `SchemaProvider`. It then formats the prompt, calls the `APIClientManager` to get a response, and parses the JSON. This entire process is wrapped in a `for` loop that serves as a retry mechanism with exponential backoff.

### `src/components/document_splitter.py`

-   **Purpose**: To perform the AI-driven semantic chunking (triage).
-   **Key Functions**:
    -   `split_by_topic`: Formats the `triage_prompt.txt` with the full content of a cleaned file. It then calls the `APIClientManager` and uses the `extract_json_from_response` utility to parse the LLM's response, which is expected to be a list of `{"topic": "...", "content": "..."}` objects. It includes a fallback to treat the whole document as "general_info" if the LLM call fails.

### `src/components/knowledge_aggregator.py`

-   **Purpose**: A simple but important component for consolidating the results.
-   **Key Functions**:
    -   `aggregate`: Takes the list of structured topic chunks and merges them into a single parent JSON object. It creates a top-level `structured_data` key and places each chunk's data under its respective topic key, adding the `source_file` for metadata.

---

## 3. Part 2: The Q&A Forge

This pipeline takes the structured JSON files from Part 1 and uses them to generate the final Q&A dataset.

### `run_qa_pipeline.py`: Pipeline Orchestration

-   **Purpose**: The main entry point and orchestrator for the Q&A generation process.
-   **Key Classes & Functions**:
    -   `QAPipeline`: The main class that encapsulates the pipeline's logic.
    -   `__init__`: Loads all necessary configuration from `config.yaml`, including concurrency limits, retry counts, and directory paths. It also prepares the checkpoint file path.
    -   `_load_processed_files` & `_save_processed_files`: These methods handle the checkpointing. Before running, the pipeline loads a set of filenames that have already been successfully processed. After the run, it saves the updated set back to the JSON file. This makes the pipeline resumable.
    -   `run`: The core orchestration method. It determines the list of new files to process by taking the difference between all structured files and the already processed files. It then creates a list of `asyncio` tasks, calling `_process_file_wrapper` for each new file.
    -   `_process_file_wrapper`: A crucial resilience wrapper. It uses an `asyncio.Semaphore` to limit the number of files being processed concurrently. It also contains the retry logic, calling the main processing function up to `max_retries` times with exponential backoff before finally giving up and moving the file to the dead-letter queue.
    -   `_process_file`: Reads a structured JSON file, instantiates the `QAGenerator`, calls it to get the Q&A pairs, and then appends them to the output `.jsonl` file.

### `src/pipeline/qa_generator.py`

-   **Purpose**: To generate high-quality Q&A pairs from a single structured JSON object.
-   **Key Functions**:
    -   `__init__`: Takes the `APIClientManager` as a dependency and loads the main `qa_generation_prompt.md` from disk.
    -   `generate_qa_pairs`: This is the core logic. It takes the structured data dictionary, serializes it into a pretty-printed JSON string, and injects this string into the prompt template. It then calls the `APIClientManager` to get a response from the LLM. Finally, it uses the `extract_json_from_response` utility to parse the expected list of Q&A pairs and performs a validation check to ensure each item has the required keys (`question`, `answer`, etc.) before returning the final list.

---

## 4. Part 3: The Quality Assurance Forge

This final, standalone pipeline cleans the generated dataset.

### `run_quality_assurance.py`: Deduplication Logic

-   **Purpose**: To read the raw Q&A dataset and produce a final, clean version with duplicate questions removed.
-   **Key Classes & Functions**:
    -   `QualityAssurance`: The main class for the pipeline.
    -   `__init__`: Takes the input and output file paths as arguments and initializes a Python `set` called `seen_questions`, which will be used to track unique questions efficiently.
    -   `_normalize_question`: A helper function that standardizes a question string by converting it to lowercase and removing common punctuation. This is critical for ensuring that semantically identical questions (e.g., "What is the fee?" vs. "what is the fee") are correctly identified as duplicates.
    -   `run_deduplication`: The main method. It reads the input `.jsonl` file line by line (which is memory-efficient). For each line, it normalizes the question and checks if the normalized version exists in the `seen_questions` set.
        -   If the question is new, it is added to the set, and the original, unmodified line is written to the output file.
        -   If the question has been seen before, it is discarded.
    -   The script is self-contained and uses `argparse` to handle command-line arguments for the input and output files.

---

This deep dive covers the primary components and logic of the SetForge pipeline. The design emphasizes separation of concerns, resilience, and configurability, creating a robust system for generating high-quality, domain-specific datasets.
