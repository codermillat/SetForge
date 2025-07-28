# SetForge AI Agent Instructions

## Architecture Overview

SetForge is a production-ready async pipeline for generating extractive QA pairs from educational text with zero hallucinations. The core flow: `TextProcessor` → `QAGenerator` → `ProductionQAValidator` → `ProductionExporter` with comprehensive monitoring and quality checking.

**NEW: Production TXT Dataset Generator** - Complete modular system for transforming .txt files into structured Q&A datasets with rich metadata, university-specific scholarship logic, and intelligent grade normalization. Designed to outperform GPT-4/Gemini 2.5 Pro for Bangladeshi student guidance.

**ENHANCED: Context-Rich Educational Analysis** - Comprehensive context-aware prompt engineering with mandatory context specification, multilingual support, and complete source attribution for cultural authenticity.

### Directory Structure
```
SetForge/
├── src/                                    # Core source code
│   ├── setforge_production.py             # Production orchestrator
│   ├── context_enhanced_qa_generator.py   # Context-rich QA generation
│   ├── educational_data_analyzer.py       # Educational data analysis
│   ├── context_rich_prompts.py           # Context-aware prompts
│   ├── config.py                         # Environment-aware config management
│   ├── text_processor.py                 # Intelligent chunking
│   ├── qa_generator.py                   # LLM API integration
│   ├── validator_enhanced.py             # Multi-stage validation
│   ├── exporter_enhanced.py              # Traceability & audit export
│   └── monitoring.py                     # Cost tracking & optimization
├── production_txt_dataset_generator.py    # NEW: Production TXT dataset generator
├── enhanced_production_qa_generator.py    # NEW: Enhanced multi-university QA generator  
├── enhanced_grade_scale_detection.py      # NEW: Intelligent grade normalization
├── official_sharda_scholarship_integration.py # NEW: Official scholarship logic
├── data_validator.py                      # NEW: Comprehensive dataset validation
├── test_dataset_generator.py              # NEW: CLI testing interface
├── demo_production_system.py              # NEW: Interactive demo system
├── config/config.yaml                     # Configuration files
├── config/normalization_config.json       # NEW: Grade conversion rules
├── config/scholarship_rules.json          # NEW: University scholarship criteria
├── data/educational/                      # Educational content (48 files with source attribution)
├── tests/                                 # Production test suite
├── docs/                                  # Documentation
├── output/datasets/                       # Generated outputs with source tracking
├── check_qa_quality.py                    # Comprehensive QA quality analyzer
├── launch_context_enhanced_production.py  # Context-enhanced launcher
├── demo_context_enhanced_analysis.py      # Context demo
├── setforge_cli.py                        # Production CLI interface
└── *_corrected_*.py                       # Data correction utilities
```

### Key Production Components
- **`ProductionSetForge`**: Main orchestrator with health checks, graceful shutdown
- **`ProductionTxtDatasetGenerator`**: NEW - Complete TXT-to-QA transformation system with persona awareness
- **`EnhancedProductionQAGenerator`**: NEW - Multi-university scholarship calculation with official 2025-26 criteria
- **`EnhancedScholarshipCalculator`**: NEW - Intelligent grade scale detection and normalization
- **`OfficialShardaScholarshipCalculator`**: NEW - Official Sharda University scholarship integration
- **`ContextEnhancedQAGenerator`**: Context-rich QA generation with mandatory context specification and source attribution
- **`EducationalDataAnalyzer`**: Comprehensive educational data analysis (48 files) with source tracking
- **`ContextRichPromptTemplates`**: Context-aware prompts with cultural sensitivity and source verification
- **`ProductionMonitor`**: Real-time cost tracking, performance metrics, budget alerts
- **`CostOptimizer`**: Dynamic batch sizing, optimization recommendations
- **`ProductionQAValidator`**: Enhanced validation with caching, detailed diagnostics
- **`ProductionExporter`**: Full data lineage, audit trails, quality-based separation with source tracking

## Critical Design Patterns

### 1. Environment-Aware Configuration
```python
# Production/Staging/Development environments with automatic optimization
config = Config.from_yaml('config/config.yaml')  # NOT Config()
processor = TextProcessor(config)

# API key: DIGITALOCEAN_API_KEY from .env file (required unless dry_run=true)
# Test mode: Set SETFORGE_DRY_RUN=true to bypass API validation
```

### 2. Production TXT Dataset Generation (NEW)
```python
# Complete TXT-to-QA dataset generation with persona awareness
from production_txt_dataset_generator import ProductionTxtDatasetGenerator

# Initialize with sophisticated components
generator = ProductionTxtDatasetGenerator(config_path="config/config.yaml")

# Process educational directory into structured QA pairs
results = await generator.process_txt_files(
    input_directory="data/educational/",
    output_path="output/enhanced_dataset.jsonl",
    target_size=1000
)

# Rich metadata includes: student personas, university context, grade normalization,
# cultural sensitivity, quality validation, and comprehensive source attribution
```

### 3. Enhanced Grade Scale Detection & Normalization (NEW)
```python
# Intelligent grade normalization across different educational systems
from enhanced_grade_scale_detection import EnhancedScholarshipCalculator

calculator = EnhancedScholarshipCalculator()

# Support for multiple scales: GPA/5 (SSC/HSC), CGPA/4 (diploma), CGPA/10 (Indian universities)
normalized = calculator.detect_and_normalize_grade("3.8 CGPA", "HSC")
# Returns: {"normalized_gpa": 3.8, "scale": "gpa_5", "confidence": 0.85}

# Official university scholarship integration
from official_sharda_scholarship_integration import OfficialShardaScholarshipCalculator
sharda_calc = OfficialShardaScholarshipCalculator()
scholarship = sharda_calc.calculate_scholarship(ssc_grade=3.5, hsc_grade=4.0)
```

### 4. Student Persona-Aware Generation (NEW)
```python
# Persona-specific QA generation based on student_personas_and_scenarios.txt
from production_txt_dataset_generator import StudentPersona

# Personas: HIGH_ACHIEVER, VALUE_SEEKER, BUDGET_CONSCIOUS, GAP_YEAR_STUDENT, 
#          DIPLOMA_HOLDER, INTERNATIONAL_FOCUSED

generator.select_persona_for_question(paragraph_info)
# Automatically selects appropriate persona based on content indicators

# Each persona has specific focus areas, tone, and decision factors
```

### 5. Context-Enhanced QA Generation (ENHANCED)
```python
# Context-rich QA generation with mandatory context specification
from context_enhanced_qa_generator import ContextEnhancedQAGenerator, ContextMetadata
from educational_data_analyzer import EducationalDataAnalyzer

# Analyze educational data for context patterns
analyzer = EducationalDataAnalyzer()
analysis_results = await analyzer.analyze_directory('data/educational/')

# Generate context-rich QA pairs with mandatory elements
context_generator = ContextEnhancedQAGenerator(config)
contextual_qa_pairs = await context_generator.generate_context_rich_qa_pairs(chunk)

# Context requirements: university, program, student_background, timeline, academic_level, audience

# Example context-rich QA with source attribution:
question = "What is the annual tuition fee for B.Tech CSE at Sharda University for Bangladeshi students in 2025-26?"
answer = "For Bangladeshi students applying to B.Tech Computer Science & Engineering (CSE) at Sharda University for the 2025-26 academic year, the annual tuition fee is ₹2,80,000..."
source_attribution = {
    "data_source_file": "fees_scholarship_btech.txt",
    "original_source": "Sharda University B.Tech Admission Brochure 2025",
    "source_url": "https://sharda.ac.in/admissions/btech",
    "verification_date": "January 2025",
    "source_type": "Official university brochure"
}
```
### 6. Production Processing Pipeline
```python
# Main orchestrator pattern in setforge_production.py
pipeline = ProductionSetForge('config/config.yaml')
await pipeline.process_files_async(input_paths, output_path)

# NEW: Context-enhanced production launcher
from launch_context_enhanced_production import ContextEnhancedProductionLauncher
launcher = ContextEnhancedProductionLauncher()
results = await launcher.run_complete_pipeline()

# NEW: Production TXT dataset generator
from production_txt_dataset_generator import ProductionTxtDatasetGenerator
txt_generator = ProductionTxtDatasetGenerator()
dataset = await txt_generator.process_txt_files("data/educational/", "output/dataset.jsonl")
```

### 7. Enhanced Data Classes & Validation
- **`ValidationResult`**: Now includes processing_time, confidence_level, diagnostics
- **`QAPair`**: Extended with source_file, processing_metadata, validation_score
- **`ContextualQAPair`**: NEW - Extended with university_context, program_context, multilingual_keywords
- **`ContextMetadata`**: NEW - Comprehensive context tracking for educational content
- **`CostBreakdown`**: Real-time cost tracking per file/model with efficiency scoring

### 8. Context-Rich Validation Framework (NEW)
```python
# Mandatory context elements (100% compliance required)
REQUIRED_CONTEXT = [
    "university",           # Specific university specification
    "program",             # Exact program/course specification
    "student_background",  # "for Bangladeshi students" inclusion
    "timeline",           # "for 2025-26 academic year" specification
    "academic_level",     # Education level clarification
    "audience"            # Target audience specification
]

# Mandatory source attribution elements (100% compliance required)
REQUIRED_SOURCE_ATTRIBUTION = [
    "data_source_file",    # Exact .txt file name where information was extracted
    "original_source",     # Original source (brochure, website, official document)
    "source_url",         # Official website URL or document reference
    "verification_date",   # When the information was last verified
    "source_type"         # Type of source (official website, brochure, government document)
]

# Context completeness scoring with cultural sensitivity and source verification
context_score = validate_context_completeness(qa_pair, REQUIRED_CONTEXT)
cultural_score = validate_cultural_appropriateness(qa_pair, "bangladeshi_students")
source_score = validate_source_attribution(qa_pair, REQUIRED_SOURCE_ATTRIBUTION)
```

### 9. Production Validation Scoring
```python
# ProductionQAValidator weighted scoring with caching:
overall_score = (
    extractive * 0.4 +          # Most important: must be extractive
    non_hallucination * 0.3 +   # Critical: no hallucinations  
    relevancy * 0.2 +           # Important: semantic relevancy
    quality * 0.1               # Nice to have: content quality
)
# Results cached for performance, validation stats tracked
```

## Development Workflows

### Production Testing
```bash
# Comprehensive production test suite
python tests/test_production_complete.py    # Full production features test
python tests/test_production_final.py       # Final validation test
python tests/test_setforge.py               # Unit tests with unittest

# NEW: Production TXT dataset generator testing
python test_dataset_generator.py --dry-run --input data/educational/
python test_enhanced_grade_detection.py     # Grade normalization tests
python demo_production_system.py            # Interactive demo system

# Set dry run mode for testing without API calls
SETFORGE_DRY_RUN=true python tests/test_production_final.py
```

### CLI Commands (Production-Ready)
```bash
# Main processing with production orchestrator
python setforge_cli.py process data/educational/ output/my_dataset.jsonl

# Enhanced CLI with dashboard and resumability
python setforge_enhanced_cli.py process data/educational output/dataset.jsonl --dashboard
python setforge_enhanced_cli.py resume data/educational output/dataset.jsonl

# NEW: Production TXT dataset generator CLI
python production_txt_dataset_generator.py --input data/educational/ --output output/enhanced_dataset.jsonl
python enhanced_dataset_cli.py --target-size 1000 --config config/config.yaml

# Cost estimation before processing
python setforge_cli.py estimate data/educational/ --config config/config.yaml

# Health checks and monitoring
python setforge_cli.py health-check
python setforge_cli.py status --config config/config.yaml
python setforge_enhanced_cli.py status --live

# Configuration management
python setforge_cli.py create-config config/my_config.yaml
```

### Production Launchers (High-Level Workflows)
```bash
# Complete workflow: test → validate → confirm → produce
python run_complete_workflow.py

# NEW: Context-enhanced production with 6-phase pipeline
python launch_context_enhanced_production.py

# NEW: Enhanced multi-university production system
python launch_enhanced_multi_university_production.py

# Enhanced production with resumability and live monitoring
python launch_enhanced_production.py

# Final production with comprehensive reporting
python launch_final_production.py

# Basic production launcher
python launch_production.py
```

### Context-Enhanced Workflows (NEW)
```bash
# Educational data analysis demo
python demo_context_enhanced_analysis.py

# Context-enhanced system validation
python test_context_enhanced_setup.py

# Context-rich QA generation for Bangladeshi students
python launch_context_enhanced_production.py --phase all

# Source attribution validation
python validate_source_attribution.py --source-check

# Context completeness analysis
python analyze_context_completeness.py --threshold 0.95
```

### Quality Analysis & Data Correction
```bash
# Comprehensive quality analysis of generated datasets
python check_qa_quality.py output/datasets/my_dataset.jsonl

# Quality checker with custom threshold and output
python check_qa_quality.py dataset.jsonl --threshold 0.85 --output quality_report.json

# Demo quality checker usage patterns
python demo_qa_quality_checker.py

# Data accuracy analysis and correction tools
python analyze_lateral_entry_issues.py        # Identify data accuracy issues
python correct_lateral_entry_dataset.py       # Apply corrections to datasets
python validate_lateral_entry_corrections.py  # Validate corrections applied
```

### Setup & Dependencies
```bash
# Production setup script
chmod +x scripts/setup.sh && scripts/setup.sh

# With example testing
scripts/setup.sh --run-example
```

### Environment Setup Patterns
```bash
# Essential environment variables (production launchers)
export DIGITALOCEAN_API_KEY=your_key_here  # Required for API access (from .env file)
export SETFORGE_ENV=production              # Environment setting
export SETFORGE_DRY_RUN=true               # Testing mode (bypasses API)
export SETFORGE_LOG_LEVEL=INFO             # Logging level

# Quick test setup (used in run_complete_workflow.py)
os.environ['DIGITALOCEAN_API_KEY'] = 'hardcoded-for-testing'
os.environ['SETFORGE_ENV'] = 'production'
```

## Project-Specific Conventions

### 1. Hallucination Prevention
- All QA generation uses **extractive-only prompts** (`qa_generator.py:base_system_prompt`)
- Validation requires **70%+ word overlap** with source text (`config.validation.min_source_overlap`)
- **Forbidden patterns** detected: "probably", "might be", "in my opinion" (`config.qa.forbidden_patterns`)

### 2. Cost Management & Optimization
- Real-time cost tracking in `qa_generator.total_cost` and `ProductionMonitor`
- Budget enforcement: processing stops at `config.cost.max_total_cost_usd`
- Token estimation: ~4 chars per token (`qa_generator._estimate_cost()`)
- **Dynamic optimization**: `CostOptimizer` adjusts batch sizes based on performance
- **Efficiency scoring**: Tracks cost per QA pair and processing efficiency

### 3. Enhanced Error Handling
- **Exponential backoff**: Retry logic with increasing delays (`qa_generator._make_api_call()`)
- **Graceful degradation**: Individual file failures don't stop batch processing
- **Health checks**: Production system includes startup and runtime health validation
- **Graceful shutdown**: SIGINT/SIGTERM handling for clean production stops

### 4. Production Data Flow
- **Chunking**: Section-aware with overlap management for context continuity
- **Validation**: Multi-stage with caching for performance (1000 result cache limit)
- **Export**: Quality-based separation, audit trails, data lineage tracking
- **Monitoring**: Real-time metrics, alerts, structured logging in production mode

### 5. Enhanced Production Features
- **Resumability**: Checkpoint-based recovery with `launch_enhanced_production.py`
- **Live Dashboard**: Real-time progress tracking via `setforge_enhanced_cli.py status --live`
- **Quality Trending**: Continuous quality monitoring with alert thresholds
- **Dynamic Optimization**: Batch size adjustment based on performance metrics
- **Cost Estimation**: Pre-flight cost analysis with budget validation

### 6. Data Quality & Accuracy Management
- **Quality Checking**: Comprehensive analysis via `check_qa_quality.py` with extractive validation, hallucination detection, semantic analysis
- **Data Correction**: Systematic approach to identify and fix accuracy issues using analysis scripts
- **Validation Workflows**: Multi-stage validation with before/after comparison for data corrections
- **Content Consistency**: Source files must maintain consistency across educational programs and policies

### 7. Production TXT Dataset Generator (NEW)
- **Persona-Aware Generation**: Student personas (HIGH_ACHIEVER, VALUE_SEEKER, BUDGET_CONSCIOUS, etc.) drive Q&A generation style
- **Grade Normalization**: Multi-scale support (GPA/5, CGPA/4, CGPA/10, Percentage) with confidence scoring
- **University-Specific Logic**: Official 2025-26 scholarship criteria for Sharda, Amity, Galgotias, NIU, G.L. Bajaj
- **Cultural Integration**: Bengali-English mixed content with transliteration and cultural context
- **Quality Thresholds**: Extractive score ≥0.75, factual accuracy ≥0.80, cultural sensitivity ≥0.85
- **Metadata Richness**: Complete traceability with source files, personas, difficulty levels, processing time

## Integration Points

### Environment Configuration
- **Development**: `debug_mode=true`, reduced retries, minimal batch sizes
- **Staging**: Balanced settings, metrics enabled, moderate optimization
- **Production**: Maximum resilience, structured logging, optimized performance
- **Dry Run**: `SETFORGE_DRY_RUN=true` bypasses API calls for testing

### LLM API (DigitalOcean Serverless)
- Uses `aiohttp.ClientSession` with connection pooling
- Rate limiting: 429 status detection with exponential backoff
- Cost tracking via `usage.total_tokens` in API response
- **Session reuse**: Single session per QAGenerator instance for efficiency

### Production Workflow Integration
- **Complete workflow**: `run_complete_workflow.py` runs test → validate → confirm → produce
- **Resume capability**: Enhanced launchers can resume from checkpoints automatically
- **Live monitoring**: Real-time progress tracking with ETA and quality metrics
- **Health checks**: Automatic system validation before processing starts

### Enhanced Output Format (JSONL with Complete Traceability)
```json
{
  "question": "What is the annual tuition fee for B.Tech CSE at Sharda University for Bangladeshi students?",
  "answer": "For Bangladeshi students applying to B.Tech Computer Science & Engineering at Sharda University for the 2025-26 academic year, the annual tuition fee is ₹2,80,000...",
  "context": "Source paragraph from .txt file",
  "university": "Sharda University",
  "audience": "bangladeshi_students", 
  "answer_type": "factual",
  "tone": "informative",
  "confidence_level": 0.95,
  "source_file": "fees_scholarship_btech.txt",
  "metadata": {
    "student_persona": "BUDGET_CONSCIOUS",
    "question_complexity": "simple", 
    "difficulty_level": 2,
    "financial_details": true,
    "grade_calculation": false,
    "multi_university": false,
    "bengali_integration": true,
    "actionable_guidance": true,
    "requires_calculation": false,
    "requires_verification": false,
    "expected_response_time": "immediate",
    "processing_time": 1.2,
    "model_used": "llama3-8b-instruct",
    "cost": 0.001
  },
  "quality": {
    "extractive_score": 0.85,
    "factual_accuracy": 0.90, 
    "cultural_sensitivity": 0.88,
    "uniqueness_score": 0.82,
    "validation_status": "passed"
  },
  "audit_trail": {
    "created_at": "2025-01-01T...",
    "config_hash": "abc123...",
    "generator_version": "production_txt_v2.0"
  },
  "university_context": ["Sharda University"], 
  "program_context": ["B.Tech CSE"], 
  "student_background_context": "bangladeshi_students",
  "timeline_context": "2025-26",
  "multilingual_keywords": ["শিক্ষার্থী", "বিশ্ববিদ্যালয়"],
  "source_attribution": {
    "data_source_file": "fees_scholarship_btech.txt",
    "original_source": "Sharda University B.Tech Admission Brochure 2025",
    "source_url": "https://www.sharda.ac.in/",
    "verification_date": "January 2025",
    "source_type": "Official university brochure",
    "source_reliability": 1.0
  }
}
```

## Critical Files for Understanding

### Core Production System
- **`src/setforge_production.py`**: Main orchestrator, study for production patterns
- **`src/monitoring.py`**: Cost tracking, performance metrics, optimization logic
- **`src/validator_enhanced.py`**: Caching, detailed diagnostics, confidence scoring
- **`src/exporter_enhanced.py`**: Data lineage, audit trails, quality separation

### Production TXT Dataset Generator System (NEW)
- **`production_txt_dataset_generator.py`**: Complete TXT-to-QA transformation system (1300+ lines)
- **`enhanced_grade_scale_detection.py`**: Intelligent grade normalization with confidence scoring
- **`enhanced_production_qa_generator.py`**: Multi-university scholarship calculation engine
- **`official_sharda_scholarship_integration.py`**: Official Sharda University 2025-26 criteria
- **`data_validator.py`**: Comprehensive dataset validation with issue categorization
- **`test_dataset_generator.py`**: CLI testing interface for production system
- **`demo_production_system.py`**: Interactive demonstration and validation tools
### Context-Enhanced Educational System (ENHANCED)
- **`src/context_enhanced_qa_generator.py`**: Context-rich QA generation with mandatory elements
- **`src/context_rich_prompts.py`**: Context-aware prompt templates and validation
- **`launch_context_enhanced_production.py`**: 6-phase production pipeline
- **`demo_context_enhanced_analysis.py`**: System demonstration and validation

### Production Launchers & Workflows
- **`launch_final_production.py`**: Complete production with comprehensive reporting
- **`launch_enhanced_production.py`**: Enhanced production with resumability
- **`run_complete_workflow.py`**: Full test → validate → produce workflow
- **`launch_production.py`**: Basic production launcher

### Quality Analysis & Data Correction
- **`check_qa_quality.py`**: Comprehensive QA dataset quality validation tool (850+ lines)
- **`demo_qa_quality_checker.py`**: Usage examples and integration demonstrations
- **`analyze_lateral_entry_issues.py`**: Data accuracy analysis for specific content issues
- **`correct_lateral_entry_dataset.py`**: Systematic data correction with audit trails
- **`validate_lateral_entry_corrections.py`**: Before/after validation for corrections

### Testing Patterns
- **`tests/test_production_final.py`**: Shows dry_run testing, environment setup
- **`tests/test_production_complete.py`**: Comprehensive feature validation
- **`run_complete_workflow.py`**: Complete end-to-end testing and production workflow
- **Use `SETFORGE_DRY_RUN=true`** for testing without API requirements

### Configuration Patterns
```python
# Always use from_yaml for production configs
config = Config.from_yaml('config/config.yaml')

# Environment variables override config file
os.environ['SETFORGE_DRY_RUN'] = 'true'  # For testing
os.environ['DIGITALOCEAN_API_KEY'] = 'your-key'  # Required for production (stored in .env)
os.environ['SETFORGE_ENV'] = 'production'  # Environment setting

# NEW: Production TXT dataset generator configuration
from production_txt_dataset_generator import ProductionTxtDatasetGenerator
generator = ProductionTxtDatasetGenerator(config_path="config/config.yaml")

# Grade normalization configuration (config/normalization_config.json)
normalization_config = {
    "percentage_to_gpa_5": {"90-100": 5.0, "85-89": 4.5, "80-84": 4.0},
    "cgpa_10_to_gpa_5": {"9.0-10.0": 5.0, "8.0-8.9": 4.5, "7.0-7.9": 4.0},
    "confidence_thresholds": {"high": 0.9, "medium": 0.7, "low": 0.5}
}

# University scholarship rules (config/scholarship_rules.json)
scholarship_config = {
    "Sharda University": {
        "tiers": {
            "tier_1": {"min_percentage": 85, "scholarship_percentage": 50},
            "tier_2": {"min_percentage": 75, "scholarship_percentage": 25}
        }
    }
}
```

### Production Launch Patterns
```python
# Enhanced production launcher pattern
from setforge_enhanced import EnhancedSetForgeProduction
setforge = EnhancedSetForgeProduction()
results = await setforge.process_directory_enhanced(input_dir, output_path)

# Resume capability pattern
checkpoint_file, checkpoint_info = check_resume_capability()
if checkpoint_file:
    # Resume from checkpoint or start fresh
    choice = prompt_resume_choice(checkpoint_info)
```

### Data Consistency Management
- **Educational content policy**: Lateral entry policies must be consistently applied (B.Tech only)
- **Source file integrity**: Use `*_corrected_*` scripts to identify and fix data discrepancies
- **Validation workflows**: Always run quality checks after data modifications
- **Audit trails**: Maintain full traceability for all data corrections and modifications
- **Contact information**: All university contact details must match the standardized format (global@sharda.ac.in, +91-8800996151, etc.)

### 7. Context-Rich Educational Data Patterns (NEW)
- **Mandatory Context Elements**: Every Q&A must include university, program, student background ("Bangladeshi students"), timeline ("2025-26"), academic level, and audience
- **Cultural Sensitivity**: Bengali-English integration with transliteration and cultural context
- **Entity Recognition**: Automatic extraction of universities (Sharda, Amity, Galgotias, G.L. Bajaj, NIU), programs (B.Tech CSE, BCA, BBA), and processes
- **Comparative Analysis**: Multi-university comparisons with context-specific guidance

### 8. Contact Information Standardization (NEW)
- **Centralized Contact Database**: All university contact info must be consistent across 48 educational files
- **Standardized Format**: Specific email/phone patterns for each university (see CONTACT_INFORMATION_UPDATE_REPORT.md)
- **Update Workflow**: Use systematic file updates when contact information changes - update core files first, then propagate
- **Validation Pattern**: Cross-reference contact info in comparison files, guides, and support documents

### 9. Source Attribution and Verification Framework (NEW)
- **Complete Source Tracking**: Every Q&A must include data_source_file, original_source, source_url, verification_date, source_type
- **Source Reliability Scoring**: Official university sources (1.0), government documents (0.9), verified third-party (0.7)
- **Currency Validation**: All sources must be verified for 2025-26 academic year relevance
- **Cross-Reference Verification**: Information consistency across multiple source files with attribution tracking
- **Source Hierarchy**: University brochures > official websites > government guidelines > third-party sources

### 10. Educational Data Structure Patterns (48 Files)
- **Content Categories**: University profiles (10), fees/scholarships (8), comparative analysis (6), admission processes (4), practical guidance (20)
- **Source Citation Pattern**: Every file contains "--source:" citations with official URLs and document references
- **Multilingual Content**: Bengali-English mixed content with cultural context for Bangladeshi students
- **Hierarchical Structure**: Consistent numbered sections, bullet points, tables for systematic information organization
- **Real-World Scenarios**: Based on actual student questions, parent concerns, and agent guidance needs

### 11. Production TXT Dataset Generator Patterns (NEW)
- **Student Personas System**: Six personas (HIGH_ACHIEVER, VALUE_SEEKER, BUDGET_CONSCIOUS, GAP_YEAR_STUDENT, DIPLOMA_HOLDER, INTERNATIONAL_FOCUSED) drive content generation
- **Grade Normalization Engine**: Intelligent detection and conversion across GPA/5, CGPA/4, CGPA/10, Percentage with confidence scoring
- **University-Specific Intelligence**: Official 2025-26 scholarship criteria, contact information, program details for 5 universities
- **Cultural Authenticity**: Bengali-English integration with proper transliteration and cultural context understanding
- **Quality Validation Framework**: Multi-dimensional scoring (extractive, factual, cultural, uniqueness) with threshold enforcement
- **Metadata Completeness**: Rich metadata including personas, difficulty, processing time, source attribution, audit trails

### 12. Enhanced Grade Scale Detection (NEW)
- **Multi-Scale Support**: Automatic detection of percentage (100-mark), GPA/5 (SSC/HSC), CGPA/4 (diploma), CGPA/10 (Indian universities)
- **Confidence Scoring**: Each conversion includes confidence level (high: 0.9+, medium: 0.7+, low: 0.5+)
- **University-Specific Conversions**: Sharda, NIU, Amity, Galgotias, G.L. Bajaj specific grade conversion tables
- **Bangladesh-India Equivalence**: Proper mapping between Bangladesh and Indian educational systems
- **Warning System**: Automatic detection of low grades with recommendation for university verification

### 13. Official Scholarship Integration (NEW)
- **Real-Time Calculation**: Official 2025-26 scholarship criteria with exact percentage calculations
- **Multi-Tier Support**: Tier-based scholarship systems with automatic qualification determination
- **Cost Analysis**: Complete fee breakdown with scholarship application and net cost calculation
- **Eligibility Validation**: Automatic checks for program eligibility, citizenship requirements, academic prerequisites
- **Contact Integration**: Direct integration with university contact information for verification

````
