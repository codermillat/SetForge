# SetForge Project Documentation

Welcome to the SetForge project documentation. This project is a sophisticated data processing pipeline designed to generate high-quality Question-Answer datasets for fine-tuning Large Language Models (LLMs).

The project is divided into two main parts:

1.  **Part 1: The Knowledge Forge**: This pipeline is responsible for taking raw data (HTML, text files), cleaning it, structuring it into a consistent JSON format based on topics, and creating a comprehensive knowledge base.

2.  **Part 2: The Q&A Forge**: This pipeline takes the structured JSON files from the Knowledge Forge and uses them to generate high-quality, contextually relevant Question-Answer pairs, which are then saved into a final dataset file.

3.  **Part 3: The Quality Assurance Forge**: This final pipeline performs quality checks on the generated dataset, starting with identifying and removing duplicate questions to ensure the final dataset is clean and efficient for fine-tuning.

## Navigation

-   [**Part 1: The Knowledge Forge**](./part_1_knowledge_forge.md): Detailed documentation on the data structuring pipeline.
-   [**Part 2: The Q&A Forge**](./part_2_qa_forge.md): Detailed documentation on the Question-Answer generation pipeline.
-   [**Part 3: The Quality Assurance Forge**](./part_3_quality_assurance.md): Detailed documentation on the deduplication and quality control pipeline.
