# SetForge - Quality Dataset Generator

A production-ready tool for generating high-quality Q&A datasets for Mistral 7B fine-tuning, specifically designed for Bangladeshi educational content and Indian university guidance.

## 🚀 Quick Start

1. **Setup Environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure API:**
   ```bash
   cp .env.example .env
   # Edit .env with your DigitalOcean API key
   ```

3. **Generate Dataset:**
   ```bash
   python cli.py generate data/educational output/dataset.jsonl --target 1000
   ```

## 📁 Project Structure

```
SetForge/
├── main_generator.py      # Core Q&A generation engine
├── cli.py                 # Command-line interface
├── quality_checker.py     # Quality validation and analysis
├── utils.py              # Bangladeshi grading system utilities
├── config.yaml           # Configuration settings
├── requirements.txt      # Python dependencies
├── data/educational/     # Educational content files (48 files)
├── output/               # Generated datasets
├── checkpoints/          # Generation checkpoints
└── docs/
    ├── README.md         # This file
    ├── API_KEY_SETUP_GUIDE.md
    ├── LICENSE
    └── rules.md          # Generation rules and guidelines
```

## ✨ Features

- **Bangladeshi Grading System Integration** - Full support for SSC, HSC, CGPA conversions
- **Cultural Authenticity Validation** - Ensures content relevance for Bangladeshi students
- **Quality Assurance** - ≥0.7 overall score, ≥60% extractive content
- **Cost Optimization** - Built-in budget monitoring ($200 DigitalOcean API)
- **Real-time Monitoring** - Progress tracking and quality validation
- **Production Scale** - Capable of generating 15K-20K quality pairs

## � Quality Standards

- Overall Quality Score: ≥0.70
- Cultural Relevance: ≥60%
- Extractive Content: ≥60%
- Bangladeshi Terminology: ≥50%
- Answer Length: 50-1000 characters
- Question Length: 20-200 characters

## 📊 Current Status

- **Project Phase**: Phase 2 - Quality Dataset Generation
- **Budget Remaining**: $195.00 of $200.00
- **Quality Threshold**: Met (≥0.7 overall score)
- **Cultural Relevance**: Validated
- **Codebase**: Cleaned and optimized (from 6,252 to 67 files)
