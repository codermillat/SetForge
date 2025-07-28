# SetForge AI Agent Instructions

## 🎯 Architecture Overview

SetForge is a **production-ready educational AI dataset generation platform** for creating fine-tuning datasets targeting Bangladeshi students applying to Indian universities. The system uses a **4-tier generator architecture** with escalating volume and sophistication.

**CORE PURPOSE:** Generate 10k-15k extractive Q&A pairs from 48 educational .txt files covering real-world scenarios Bangladeshi students face (admissions, scholarships, visa, accommodation, cultural adaptation).

**KEY DIFFERENTIATORS:**
- **Zero Hallucination:** All answers strictly extracted from source .txt files
- **Cultural Authenticity:** Bengali-English mixed content with proper transliteration  
- **Production-Ready:** Comprehensive validation, quality metrics, and error handling
- **University-Specific Intelligence:** Official 2025-26 criteria for 5+ universities
- **Student Persona Awareness:** 6 distinct personas drive generation style

### 🏗️ Cleaned Project Structure (Post-Cleanup)
```
SetForge/ (61MB, production-optimized)
├── data/educational/                       # 48 source .txt files (PRESERVED)
│   ├── sharda_scholarship_policy.txt      # Official 2025-26 scholarship criteria  
│   ├── common_questions_and_concerns.txt  # 1000+ real student queries
│   ├── student_personas_and_scenarios.txt # 6 persona profiles 
│   └── comparative_analysis_*.txt         # Multi-university comparisons
├── production_txt_dataset_generator.py    # Tier 1: Base generator (1437 lines)
├── high_volume_qa_generator.py            # Tier 2: Mid-volume (5k pairs)
├── ultra_high_volume_generator.py         # Tier 3: High-volume (10k pairs)
├── large_scale_qa_dataset_generator.py    # Tier 4: Large-scale (15k pairs)
├── enhanced_production_qa_generator.py    # Multi-university scholarship engine
├── enhanced_grade_scale_detection.py      # GPA/CGPA normalization system
├── official_sharda_scholarship_integration.py # Official university integration
├── data_validator.py                      # Comprehensive dataset validation
├── check_qa_quality.py                    # Quality analysis with cultural metrics
├── setforge_cli.py                        # Production CLI interface
├── enhanced_dataset_cli.py                # Enhanced CLI with dashboard
├── demonstrate_grounded_15k_success.py    # Specification fulfillment demo
├── enhanced_grounded_15k_generator.py     # Grounded content extraction
├── output/datasets/                       # Essential datasets only
│   ├── enhanced_grounded_15k_dataset.jsonl (37.7MB)
│   └── true_15k_unique_dataset.jsonl (22.2MB)
└── src/                                   # Core production components
```

## ⚡ Critical Production Workflows

### **Primary Development Commands**
```bash
# 🎯 Core Production Generation (Choose based on requirements)
# Tier 1: High quality, smaller volume (1k pairs)
python production_txt_dataset_generator.py --target 1000 --config config/config.yaml

# Tier 2: Balanced quality-volume (5k pairs)  
python high_volume_qa_generator.py --target 5000

# Tier 3: Maximum volume (10k+ pairs)
python ultra_high_volume_generator.py --target 10000

# Tier 4: Comprehensive large-scale (15k pairs)
python large_scale_qa_dataset_generator.py --target 15000

# ✅ Production CLI Interface
python setforge_cli.py process data/educational/ output/my_dataset.jsonl
python enhanced_dataset_cli.py --target-size 1000 --config config/config.yaml

# 🔍 Quality Analysis & Validation
python check_qa_quality.py output/my_dataset.jsonl --threshold 0.85
python data_validator.py output/my_dataset.jsonl

# 📊 Demonstration & Verification
python demonstrate_grounded_15k_success.py  # Verify 15K spec fulfillment
python test_dataset_generator.py --dry-run  # Test without API calls

# 🧹 Project Maintenance
python cleanup_project.py  # Remove unnecessary files (already executed)
```

### **Essential Environment Setup**
```bash
# Required environment variables
export DIGITALOCEAN_API_KEY=your_key_here    # From .env file
export SETFORGE_ENV=production               # Environment setting
export SETFORGE_DRY_RUN=true                # Testing mode (bypasses API)

# Dependencies installation
pip install -r requirements.txt
```

## 🔧 Critical Design Patterns

### **1. Multi-Tier Generator Selection**
Choose generator based on requirements:
```python
# Tier 1: Base Production (1k pairs, highest quality)
from production_txt_dataset_generator import ProductionTxtDatasetGenerator
generator = ProductionTxtDatasetGenerator(config_path="config/config.yaml")

# Tier 2: High Volume (5k pairs, balanced quality)  
from high_volume_qa_generator import HighVolumeDatasetGenerator
generator = HighVolumeDatasetGenerator(target_pairs=5000)

# Tier 3: Ultra Volume (10k pairs, template-aggressive)
from ultra_high_volume_generator import UltraHighVolumeGenerator  
generator = UltraHighVolumeGenerator(target_pairs=10000)

# Tier 4: Large Scale (15k pairs, comprehensive)
from large_scale_qa_dataset_generator import LargeScaleDatasetGenerator
generator = LargeScaleDatasetGenerator(target_pairs=15000)
```

### **2. Student Persona-Driven Generation**
**Critical:** All generators MUST use persona awareness:
```python
from production_txt_dataset_generator import StudentPersona

# Six personas drive question style and university focus
personas = {
    StudentPersona.HIGH_ACHIEVER.value: {
        "focus": ["research opportunities", "rankings", "global exposure"],
        "tone": "confident and ambitious",
        "universities": ["Sharda", "Amity"]
    },
    StudentPersona.VALUE_SEEKER.value: {
        "focus": ["scholarship opportunities", "total cost", "ROI analysis"],
        "tone": "practical and cost-conscious"
    },
    StudentPersona.BUDGET_CONSCIOUS.value: {
        "focus": ["affordable options", "financial aid"],
        "tone": "supportive and understanding"
    }
    # Additional: GAP_YEAR_STUDENT, DIPLOMA_HOLDER, INTERNATIONAL_FOCUSED
}
```

### **3. Grade Normalization Engine** 
**Essential for scholarship calculations:**
```python
from enhanced_grade_scale_detection import EnhancedScholarshipCalculator

calculator = EnhancedScholarshipCalculator()

# Auto-detects: Percentage/100, GPA/5 (SSC/HSC), CGPA/4 (diploma), CGPA/10 (Indian)
result = calculator.detect_and_normalize_grade("3.8 CGPA", "HSC")
# Returns: {"normalized_gpa": 3.8, "scale": "gpa_5", "confidence": 0.85}

# Official university scholarship integration
from official_sharda_scholarship_integration import OfficialShardaScholarshipCalculator
sharda_calc = OfficialShardaScholarshipCalculator()
scholarship = sharda_calc.calculate_scholarship(ssc_grade=3.5, hsc_grade=4.0)
```

### **4. Quality Validation Framework**
```python
# Multi-dimensional quality scoring system
quality_thresholds = {
    "extractive_score": 0.75,      # Must be largely extracted from source
    "factual_accuracy": 0.90,      # High factual correctness required  
    "cultural_sensitivity": 0.70,  # Appropriate for Bangladeshi students
    "semantic_alignment": 1.00,    # Perfect question-answer alignment
    "uniqueness_score": 0.50       # Moderate uniqueness requirement
}

# Cultural sensitivity validation
cultural_indicators = [
    r'(?i)\bbangladeshi\s+students?\b',
    r'(?i)\bfrom\s+bangladesh\b', 
    r'(?i)\bssc\b', r'(?i)\bhsc\b',
    r'(?i)\btaka\b', r'(?i)\bbdt\b'
]
```

### **5. Bengali-English Cultural Integration**
```python
# Authentic cultural integration patterns
multilingual_terms = {
    "শিক্ষার্থী": "student",
    "বিশ্ববিদ্যালয়": "university", 
    "ভর্তি": "admission",
    "বৃত্তি": "scholarship",
    "শিক্ষা": "education"
}

# Cultural context markers in generated content
cultural_patterns = [
    "for Bangladeshi students",
    "from Bangladesh", 
    "SSC/HSC graduates",
    "in BDT (Bangladeshi Taka)",
    "যোগাযোগ করুন" # "please contact"
]

# Example culturally integrated Q&A:
question = "আমার HSC এ 4.2 CGPA, কোন scholarship পাবো Sharda University তে?"
answer = "HSC-তে 4.2 CGPA থাকায় আপনি Sharda University-তে 50% scholarship পাবেন..."
```

### **6. Template-Based Generation Scaling**
```python
# Progressive template complexity across generators
base_templates = {
    "scholarship_analysis": [
        "My {grade_type} is {grade_value}. What scholarship can I get for {program} at {university}?",
        "With {grade_value} in {grade_type}, am I eligible for merit scholarship?"
    ],
    "university_comparison": [
        "Compare {program} at {university1} vs {university2} for overall value",
        "Which university offers better ROI for {program}?"
    ],
    "edge_case_scenarios": [
        "What if I fail one subject in my final year?",
        "Can I change my program after admission?",
        "What happens if my visa gets rejected?"
    ]
}

# Ultra-high volume uses 80+ templates across 8 categories
# Large-scale uses sophisticated template expansion with entity replacement
```

### **7. Enhanced Data Classes & Validation**
- **`ValidationResult`**: Now includes processing_time, confidence_level, diagnostics
- **`QAPair`**: Extended with source_file, processing_metadata, validation_score
- **`ContextualQAPair`**: NEW - Extended with university_context, program_context, multilingual_keywords
- **`ContextMetadata`**: NEW - Comprehensive context tracking for educational content
- **`CostBreakdown`**: Real-time cost tracking per file/model with efficiency scoring

### **8. Context-Rich Validation Framework (NEW)**
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

### **9. Production Validation Scoring**
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

## ⚡ Development Workflows

### **Production Testing**
```bash
# Comprehensive production test suite
python test_dataset_generator.py --dry-run --input data/educational/
python test_enhanced_grade_detection.py     # Grade normalization tests
python demo_production_system.py            # Interactive demo system

# Set dry run mode for testing without API calls
SETFORGE_DRY_RUN=true python test_dataset_generator.py --input data/educational/
```

### **CLI Commands (Production-Ready)**
```bash
# Main processing with production orchestrator
python setforge_cli.py process data/educational/ output/my_dataset.jsonl

# Enhanced CLI with dashboard and resumability
python enhanced_dataset_cli.py --target-size 1000 --config config/config.yaml

# Cost estimation before processing
python setforge_cli.py estimate data/educational/ --config config/config.yaml

# Health checks and monitoring
python setforge_cli.py health-check
python setforge_cli.py status --config config/config.yaml

# Configuration management
python setforge_cli.py create-config config/my_config.yaml
```

### **Generator-Specific Workflows**
```bash
# Base production generator (1k pairs, highest quality)
python production_txt_dataset_generator.py --target 1000 --config config/config.yaml

# High volume generation (5k pairs, balanced quality)
python high_volume_qa_generator.py --target 5000 --config config/high_volume_config.yaml

# Ultra high volume (10k pairs, aggressive templates)
python ultra_high_volume_generator.py --target 10000 --parallel-workers 8

# Large scale comprehensive (15k pairs, full sophistication)
python large_scale_qa_dataset_generator.py --target 15000 --config config/large_scale_config.yaml

# All generators support resumability and checkpointing
python <generator>.py --resume --checkpoint-dir output/checkpoints/
```

### **Quality Analysis & Data Correction**
```bash
# Comprehensive quality analysis of generated datasets
python check_qa_quality.py output/datasets/my_dataset.jsonl

# Quality checker with custom threshold and output
python check_qa_quality.py dataset.jsonl --threshold 0.85 --output quality_report.json

# Demo quality checker usage patterns
python demo_qa_quality_checker.py

# Data validation and integrity checks
python data_validator.py output/my_dataset.jsonl
```

### **Setup & Dependencies**
```bash
# Required environment variables
export DIGITALOCEAN_API_KEY=your_key_here    # From .env file
export SETFORGE_ENV=production               # Environment setting
export SETFORGE_DRY_RUN=false                # Testing mode (bypasses API)

# Dependencies installation
pip install -r requirements.txt
```

## 🔑 Project-Specific Conventions

### **1. Hallucination Prevention**
- All QA generation uses **extractive-only prompts** with strict source text validation
- Validation requires **75%+ word overlap** with source text for extractive scoring
- **Forbidden patterns** detected: "probably", "might be", "in my opinion", "I think"
- Questions must be directly answerable from source content without inference

### **2. Cost Management & Optimization**
- Real-time cost tracking with `DIGITALOCEAN_API_KEY` usage monitoring
- Budget enforcement: processing stops at configured `max_total_cost_usd`
- Token estimation: ~4 chars per token for accurate cost prediction
- **Dynamic optimization**: Batch size adjustment based on performance metrics
- **Efficiency scoring**: Tracks cost per QA pair generation

### **3. Enhanced Error Handling**
- **Exponential backoff**: Retry logic with increasing delays for API failures
- **Graceful degradation**: Individual file failures don't stop batch processing
- **Health checks**: Production system includes startup and runtime validation
- **Graceful shutdown**: SIGINT/SIGTERM handling for clean production stops

### **4. Production Data Flow**
- **Chunking**: Section-aware with overlap management for context continuity
- **Validation**: Multi-stage with caching for performance (1000 result cache limit)
- **Export**: Quality-based separation, audit trails, data lineage tracking
- **Monitoring**: Real-time metrics, alerts, structured logging in production mode

### **5. Enhanced Production Features**
- **Resumability**: Checkpoint-based recovery with automatic state restoration
- **Live Dashboard**: Real-time progress tracking via enhanced CLI tools
- **Quality Trending**: Continuous quality monitoring with alert thresholds
- **Dynamic Optimization**: Batch size adjustment based on performance metrics
- **Cost Estimation**: Pre-flight cost analysis with budget validation

### **6. Data Quality & Accuracy Management**
- **Quality Checking**: Comprehensive analysis via `check_qa_quality.py` with extractive validation
- **Hallucination detection**: Pattern-based detection of non-extractive content
- **Semantic analysis**: Question-answer alignment validation with perfect scoring requirement
- **Content Consistency**: Source files must maintain consistency across educational programs

### **7. Production TXT Dataset Generator Patterns**
- **Student Personas System**: Six personas (HIGH_ACHIEVER, VALUE_SEEKER, BUDGET_CONSCIOUS, GAP_YEAR_STUDENT, DIPLOMA_HOLDER, INTERNATIONAL_FOCUSED) drive content generation
- **Grade Normalization Engine**: Intelligent detection and conversion across GPA/5, CGPA/4, CGPA/10, Percentage with confidence scoring
- **University-Specific Intelligence**: Official 2025-26 scholarship criteria, contact information, program details for 5 universities
- **Cultural Authenticity**: Bengali-English integration with proper transliteration and cultural context understanding
- **Quality Validation Framework**: Multi-dimensional scoring (extractive, factual, cultural, uniqueness) with threshold enforcement
- **Metadata Completeness**: Rich metadata including personas, difficulty, processing time, source attribution, audit trails

### **8. Enhanced Grade Scale Detection**
- **Multi-Scale Support**: Automatic detection of percentage (100-mark), GPA/5 (SSC/HSC), CGPA/4 (diploma), CGPA/10 (Indian universities)
- **Confidence Scoring**: Each conversion includes confidence level (high: 0.9+, medium: 0.7+, low: 0.5+)
- **University-Specific Conversions**: Sharda, NIU, Amity, Galgotias, G.L. Bajaj specific grade conversion tables
- **Bangladesh-India Equivalence**: Proper mapping between Bangladesh and Indian educational systems
- **Warning System**: Automatic detection of low grades with recommendation for university verification

### **9. Official Scholarship Integration**
- **Real-Time Calculation**: Official 2025-26 scholarship criteria with exact percentage calculations
- **Multi-Tier Support**: Tier-based scholarship systems with automatic qualification determination
- **Cost Analysis**: Complete fee breakdown with scholarship application and net cost calculation
- **Eligibility Validation**: Automatic checks for program eligibility, citizenship requirements, academic prerequisites
- **Contact Integration**: Direct integration with university contact information for verification

## 🔧 Integration Points

### **Environment Configuration**
- **Development**: `debug_mode=true`, reduced retries, minimal batch sizes
- **Staging**: Balanced settings, metrics enabled, moderate optimization
- **Production**: Maximum resilience, structured logging, optimized performance
- **Dry Run**: `SETFORGE_DRY_RUN=true` bypasses API calls for testing

### **LLM API (DigitalOcean Serverless)**
- Uses `aiohttp.ClientSession` with connection pooling
- Rate limiting: 429 status detection with exponential backoff
- Cost tracking via `usage.total_tokens` in API response
- **Session reuse**: Single session per QAGenerator instance for efficiency

### **Production Workflow Integration**
- **Complete workflow**: Test → validate → confirm → produce pipeline
- **Resume capability**: Checkpoint-based recovery with automatic state restoration
- **Live monitoring**: Real-time progress tracking with ETA and quality metrics
- **Health checks**: Automatic system validation before processing starts

### **Enhanced Output Format (JSONL with Complete Traceability)**
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

## 📚 Critical Files for Understanding

### **Core Production System**
- **`production_txt_dataset_generator.py`**: Complete TXT-to-QA transformation system (1437 lines)
- **`enhanced_grade_scale_detection.py`**: Intelligent grade normalization with confidence scoring
- **`enhanced_production_qa_generator.py`**: Multi-university scholarship calculation engine
- **`official_sharda_scholarship_integration.py`**: Official Sharda University 2025-26 criteria
- **`data_validator.py`**: Comprehensive dataset validation with issue categorization
- **`setforge_cli.py`**: Production CLI interface
- **`enhanced_dataset_cli.py`**: Enhanced CLI with dashboard and resumability

### **Multi-Tier Generator Architecture**
- **`high_volume_qa_generator.py`**: Mid-volume balanced approach (5k pairs target)
- **`ultra_high_volume_generator.py`**: Aggressive template-based generation (10k pairs)
- **`large_scale_qa_dataset_generator.py`**: Most sophisticated system (15k pairs target)

### **Quality Analysis & Validation**
- **`check_qa_quality.py`**: Comprehensive QA dataset quality validation tool (850+ lines)
- **`test_dataset_generator.py`**: CLI testing interface for production system
- **`demo_production_system.py`**: Interactive demonstration and validation tools

### **Educational Data Structure (48 Files)**
- **`data/educational/`**: 48 source .txt files with authentic university content
- **`data/educational/common_questions_and_concerns.txt`**: 1000+ real student queries
- **`data/educational/student_personas_and_scenarios.txt`**: 6 detailed persona profiles
- **`data/educational/comparative_analysis_*.txt`**: Multi-university comparisons

### **Essential Datasets (Post-Cleanup)**
- **`output/datasets/enhanced_grounded_15k_dataset.jsonl`**: 37.7MB production dataset
- **`output/datasets/true_15k_unique_dataset.jsonl`**: 22.2MB validated dataset

### **Configuration Patterns**
```python
# Always use from_yaml for production configs
config = Config.from_yaml('config/config.yaml')

# Environment variables override config file
os.environ['SETFORGE_DRY_RUN'] = 'true'  # For testing
os.environ['DIGITALOCEAN_API_KEY'] = 'your-key'  # Required for production (stored in .env)
os.environ['SETFORGE_ENV'] = 'production'  # Environment setting

# Production TXT dataset generator configuration
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

### **Production Launch Patterns**
```python
# Multi-tier generator selection based on requirements
# Tier 1: High quality, smaller volume (1k pairs)
generator = ProductionTxtDatasetGenerator(target_pairs=1000)

# Tier 2: Balanced quality-volume (5k pairs)
generator = HighVolumeDatasetGenerator(target_pairs=5000)

# Tier 3: Maximum volume (10k+ pairs)
generator = UltraHighVolumeGenerator(target_pairs=10000)

# Tier 4: Comprehensive large-scale (15k pairs)
generator = LargeScaleDatasetGenerator(target_pairs=15000)

# All generators support async processing and checkpointing
results = await generator.process_directory(input_dir, output_path)
```

### **Testing Patterns**
```python
# Use SETFORGE_DRY_RUN=true for testing without API requirements
os.environ['SETFORGE_DRY_RUN'] = 'true'
python test_dataset_generator.py --input data/educational/

# Testing with actual production configuration
python production_txt_dataset_generator.py --dry-run --config config/config.yaml
```

````
