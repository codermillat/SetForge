---
license: mit
language:
  - en
  - bn
tags:
  - question-answering
  - education
  - bengali
  - instruction-tuning
---

# Indian University Guidance for Bangladeshi Students Dataset

## Dataset Description

This dataset contains **7,044 high-quality, instruction-formatted Question-Answer pairs** designed for fine-tuning Large Language Models (LLMs). The primary goal of this dataset is to create a specialized AI counselor that provides accurate, culturally relevant, and comprehensive guidance on Indian universities for Bangladeshi students.

The dataset was generated through a sophisticated, multi-stage pipeline known as **SetForge**, which transforms unstructured web data into a clean, structured, and context-aware format suitable for generating high-fidelity training data.

-   **Source Repository:** [codermillat/SetForge](https://github.com/codermillat/SetForge)
-   **Data Collection Tool:** [codermillat/WebScrape](https://github.com/codermillat/WebScrape)

## Dataset Structure

The dataset is provided in a `.jsonl` (JSON Lines) format, where each line is a distinct JSON object representing a single Q&A pair.

### Data Fields

Each JSON object has the following structure:

-   `question`: (string) The question posed, typically from the perspective of a Bangladeshi student.
-   `answer`: (string) A comprehensive, direct answer to the question.
-   `context`: (string) A brief description of the context or topic the Q&A pair belongs to.
-   `source`: (string) The source of the information used to generate the answer.
-   `metadata`: (object) A nested object containing additional metadata for advanced filtering or analysis:
    -   `degree_equivalence`: (string) Information on degree equivalencies, if applicable.
    -   `grading_conversion`: (string) Information on converting grading systems (e.g., GPA to percentage), if applicable.
    -   `country_origin`: (string) The country of origin for the student persona (e.g., "Bangladesh").
    -   `tone`: (string) The intended tone of the answer (e.g., "informative").
    -   `cultural_sensitivity`: (boolean) A flag indicating if the Q&A pair involves cultural-specific context.

### Example Record

```json
{
  "question": "I have a GPA of 3.8 and want to study BBA at Sharda. Will I get a 50% scholarship or a 20% scholarship?",
  "answer": "You will receive a 50% scholarship on your tuition fees. Since your GPA of 3.8 out of 5 (≈ 76% ≈ CGPA 7.6/10 in India) is above 3.5, you are eligible for the 50% scholarship. The BBA program is listed under the programs that qualify for the 50% scholarship for Bangladeshi students at Sharda University. Keep in mind, you need to maintain 75% attendance and pass your exams each year to continue receiving it.",
  "context": "Sharda University Scholarship policy for Bangladeshi students and BBA program eligibility.",
  "source": "Sharda University Scholarship Policy",
  "metadata": {
    "degree_equivalence": "N/A",
    "grading_conversion": "GPA 3.8/5 ≈ 76% ≈ CGPA 7.6/10",
    "country_origin": "Bangladesh",
    "tone": "informative",
    "cultural_sensitivity": true
  }
}
```

## Data Curation

The creation of this dataset was a rigorous, research-oriented process designed to maximize quality and relevance. The process was orchestrated by the **SetForge** pipeline, which is divided into three main parts.

### Part 1: The Knowledge Forge (Data Structuring)

1.  **Data Collection**: Raw data was collected from various Indian university websites, educational portals, and visa information sites using the **WebScrape** Chrome extension.
2.  **Content Extraction**: The pipeline used the `trafilatura` library to extract the main textual content from raw HTML, discarding irrelevant boilerplate.
3.  **Semantic Chunking**: An LLM was used to perform a "triage" step, segmenting the cleaned text into logical, topic-based chunks (e.g., 'admissions', 'fee_structure').
4.  **Schema-Guided Structuring**: Each chunk was then processed by an LLM with a topic-specific prompt and a corresponding JSON schema, transforming the unstructured text into a highly structured knowledge base.

### Part 2: The Q&A Forge (Dataset Generation)

1.  **Context-Aware Generation**: The structured JSON files from Part 1 were used as the full context for an LLM.
2.  **Instruction Prompting**: A master prompt (`qa_generation_prompt.md`) guided the LLM to generate relevant Q&A pairs from the perspective of a Bangladeshi student, including the answer and all relevant metadata fields.

### Part 3: The Quality Assurance Forge

1.  **Deduplication**: A final pipeline step was performed to ensure the quality of the dataset. This stage normalized all questions (by lowercasing and removing punctuation) to identify and remove semantic duplicates.
2.  **Final Output**: The result of this process is the clean, deduplicated `dataset.jsonl` file.

## Intended Use

This dataset is intended for fine-tuning instruction-based LLMs (such as Mistral, Llama, or Gemma) to create a specialized chatbot or AI assistant. The goal is to build a model that can answer questions about Indian universities for Bangladeshi students with a high degree of accuracy and cultural understanding.

## Limitations

-   The information is based on data scraped from public websites at a specific point in time and may become outdated.
-   While the pipeline is designed to be comprehensive, it may not cover every possible topic or university.
-   The dataset is highly specialized and may not be suitable for general-purpose chatbot training.

## License

This dataset is released under the **MIT License**.
