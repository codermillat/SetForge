# SetForge Project Cleanup Plan

## 🎯 GOAL
Create a streamlined dataset generation system for fine-tuning Mistral 7B on Indian university guidance for Bangladeshi students.

**Target:** 15K-20K Q&A pairs | **Budget:** $200 | **Timeline:** 2-3 weeks

## 📊 CURRENT STATE ANALYSIS
- **Total Size:** 879MB (TOO LARGE)
- **Python Files:** 10,907+ files (EXTREMELY OVER-ENGINEERED)
- **Educational Data:** 48 files (~500KB) ✅ KEEP
- **Essential:** Less than 1% of current codebase

## 🗑️ FILES TO REMOVE

### 1. MULTIPLE GENERATOR FILES (KEEP ONLY ONE)
**Remove these 50+ generator files:**
- `competitive_15k_generator.py`
- `enhanced_grounded_15k_generator.py`
- `enhanced_sophisticated_qa_generator.py`
- `extreme_scale_15k_generator.py`
- `final_15k_generator.py`
- `grounded_15k_educational_generator.py`
- `high_volume_15k_generator.py`
- `large_scale_qa_dataset_generator.py`
- `maximum_yield_generator.py`
- `production_15k_generator.py`
- `production_15k_grounded_generator.py`
- `production_large_scale_generator.py`
- `production_ready_qa_generator.py`
- `production_txt_dataset_generator_enhanced.py`
- `production_txt_dataset_generator_fixed.py`
- `production_volume_generator.py`
- `sophisticated_parallel_qa_generator.py`
- `sophisticated_qa_generator.py`
- `true_15k_unique_generator.py`
- `ultimate_15k_generator.py`
- `ultimate_15k_grounded_generator.py`
- `ultimate_generator.py`
- `ultimate_generator_fixed.py`
- `ultra_high_volume_generator.py`
- All other `*generator*.py` files

**KEEP ONLY:** `production_txt_dataset_generator.py` (simplified)

### 2. COMPLEX VALIDATION SYSTEMS (KEEP SIMPLE)
**Remove:**
- `data_validator.py` (over-engineered)
- `semantic_alignment_validation_summary.py`
- `enhanced_grade_scale_detection.py` (too complex)
- `official_sharda_scholarship_integration.py` (over-engineered)

**KEEP:** `check_qa_quality.py` (simplified)

### 3. DEMO AND TEST FILES (REMOVE ALL)
**Remove 30+ demo/test files:**
- `demo_*.py` (all demo files)
- `test_*.py` (all test files)
- `launch_*.py` (all launcher files)
- `demonstrate_*.py` (all demonstration files)

### 4. OVER-ENGINEERED MONITORING SYSTEMS
**Remove:**
- `src/monitoring.py`
- `src/progress_tracker.py` 
- `src/status_dashboard.py`
- `src/quality_monitor.py`
- `src/resumable_processor.py`
- `enhanced_dataset_cli.py` (too complex)

**KEEP:** `setforge_cli.py` (simplified)

### 5. MULTIPLE CONFIGURATION FILES
**Remove:**
- `config/` directory (multiple complex configs)
- `modular_dataset_components.py`

**KEEP:** Single `config.yaml`

### 6. UNNECESSARY OUTPUT FILES
**Remove:**
- `output/` directory (large datasets)
- `*.jsonl` files (generated datasets)
- `*.log` files (generation logs)
- `dataset_stats.json`
- `quality_analysis_report.json`

### 7. DOCUMENTATION OVERLOAD
**Remove 20+ markdown files:**
- `ADVANCED_EDUCATIONAL_ANALYSIS_COMPLETE_SUMMARY.md`
- `CLEANUP_SUMMARY.md`
- `COMPETITIVE_ANALYSIS_REPORT.md`
- `COMPREHENSIVE_ENHANCED_IMPLEMENTATION_SUMMARY.md`
- `DATA_ACCURACY_CORRECTION_COMPLETE.md`
- `DATASET_QUALITY_COMPETITIVE_ANALYSIS.md`
- `ENHANCED_*.md` (all enhanced documentation)
- `FINAL_*.md` (all final documentation)
- `IMPLEMENTATION_*.md` (all implementation docs)
- `PRODUCTION_*.md` (all production docs)
- And 10+ more markdown files

**KEEP:** `README.md`, `LICENSE`

### 8. BACKUP AND REDUNDANT DATA
**Remove:**
- `data/backup_original/` (duplicate data)
- `scripts/` directory (unnecessary scripts)
- `docs/` directory (over-documentation)
- `tests/` directory (over-testing)

### 9. PYTHON CACHE AND BUILD FILES
**Remove:**
- `__pycache__/` directories
- `.venv/` (user can recreate)
- Build artifacts

## ✅ FILES TO KEEP (MINIMAL ESSENTIAL)

### Core Files (5 files):
1. `main_generator.py` (simplified from production_txt_dataset_generator.py)
2. `quality_checker.py` (simplified from check_qa_quality.py)
3. `utils.py` (basic utilities)
4. `config.yaml` (single configuration)
5. `requirements.txt` (minimal dependencies)

### Source Data (48 files):
- `data/educational/*.txt` (ALL 48 files - our gold mine)

### Project Files:
- `README.md` (updated)
- `LICENSE`
- `.gitignore`
- `.env` (for API key)

### CLI Interface:
- `cli.py` (simplified from setforge_cli.py)

## 🏗️ SIMPLIFIED PROJECT STRUCTURE

```
SetForge/                          # Target: <10MB
├── README.md                      # Updated project description
├── LICENSE                        # Keep license
├── .gitignore                     # Essential git settings
├── .env                          # API key storage
├── requirements.txt              # Minimal dependencies
├── config.yaml                   # Single configuration file
├── cli.py                        # Simple CLI interface
├── main_generator.py             # Core Q&A generator
├── quality_checker.py            # Basic quality validation
├── utils.py                      # Essential utilities
└── data/
    └── educational/              # 48 source files (KEEP ALL)
        ├── common_questions_and_concerns.txt
        ├── sharda_*.txt
        ├── fees_scholarship_*.txt
        └── ... (all 48 files)
```

## 🎯 SIMPLIFIED ARCHITECTURE

### Core Components:
1. **Main Generator** (`main_generator.py`)
   - Single generator class
   - Template-based Q&A creation
   - Simple persona system (3 personas max)
   - Basic grade normalization
   - Direct API calls to DigitalOcean

2. **Quality Checker** (`quality_checker.py`)
   - Basic validation (extractive score, relevancy)
   - Simple metrics (no complex scoring)
   - Duplicate detection

3. **CLI Interface** (`cli.py`)
   - Simple commands: generate, validate, estimate-cost
   - Progress bars
   - Basic error handling

4. **Configuration** (`config.yaml`)
   - API settings
   - Generation parameters
   - Quality thresholds

### Dependencies (Minimal):
```
aiohttp>=3.8.0      # For API calls
pyyaml>=6.0         # For config
click>=8.0          # For CLI
tqdm>=4.64          # For progress bars
```

## 📈 EXPECTED RESULTS AFTER CLEANUP

**Size Reduction:** 879MB → <10MB (99% reduction)
**File Count:** 10,907+ → <15 files (99.8% reduction)
**Complexity:** Extremely complex → Simple and maintainable
**Focus:** Multiple goals → Single goal (15K-20K Q&A pairs)
**Budget:** Uncontrolled → $200 strict limit
**Timeline:** Unclear → 2-3 weeks achievable

## 🚀 IMPLEMENTATION PRIORITY

1. **Phase 1:** Remove unnecessary files (this cleanup)
2. **Phase 2:** Create simplified generator
3. **Phase 3:** Test with small batch (100 Q&A pairs)
4. **Phase 4:** Scale to full production (15K-20K pairs)
