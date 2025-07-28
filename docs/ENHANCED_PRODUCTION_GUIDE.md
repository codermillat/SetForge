# SetForge Enhanced Production Guide

## 🚀 Quick Start for Enhanced Production

SetForge now features comprehensive tracking, resumability, and quality assurance for production-grade dataset creation.

### 1. Environment Setup

```bash
# Set your API key
export DIGITALOCEAN_API_KEY=your_key_here

# Or for testing without API calls
export SETFORGE_DRY_RUN=true

# Optional: Set environment type
export SETFORGE_ENV=production  # or development, staging
```

### 2. Launch Options

#### Option A: Enhanced Production Launcher (Recommended)
```bash
python launch_enhanced_production.py
```

This provides:
- Interactive resume capability
- Cost estimation with enhancement details
- Configuration overview
- Progress monitoring setup
- Graceful error handling

#### Option B: Enhanced CLI Commands

**New Processing with Dashboard:**
```bash
python setforge_enhanced_cli.py process data/educational output/qa_dataset.jsonl --dashboard
```

**Resume from Checkpoint:**
```bash
python setforge_enhanced_cli.py resume data/educational output/qa_dataset.jsonl
```

**Live Status Monitoring:**
```bash
python setforge_enhanced_cli.py status --live
```

**Quality Analysis:**
```bash
python setforge_enhanced_cli.py quality-report
```

**Performance Analysis:**
```bash
python setforge_enhanced_cli.py performance-report
```

### 3. Enhanced Features Overview

#### 🎯 Target Optimized System
- **Goal**: 10,000-15,000 high-quality extractive QnA pairs
- **Source**: 47 educational text files (your current data)
- **Approach**: Micro-chunking + enhanced generation + deduplication
- **Quality**: Zero-hallucination extractive QA with validation

#### 📊 Real-time Progress Tracking
- Live progress bars with ETA calculation
- Processing speed monitoring (files/minute, QA pairs/minute)
- Cost tracking in real-time
- Quality metrics monitoring
- Resource usage tracking

#### 💾 Resumable Processing
- Automatic checkpointing every 5 files or 10 minutes
- Graceful interruption handling (Ctrl+C)
- Resume from any checkpoint
- State persistence across sessions
- Emergency checkpoint on crashes

#### 🔍 Quality Monitoring
- Real-time quality score calculation
- Hallucination detection and alerts
- Quality trend analysis
- Distribution analysis (excellent, good, poor quality)
- Validation caching for performance

#### 📈 Live Status Dashboard
- Real-time visual progress display
- Color-coded status indicators
- Performance metrics
- Quality indicators
- Cost tracking
- ETA calculations

## 🔧 Configuration

### Enhanced Configuration Structure

The system uses enhanced configuration with new sections:

```yaml
# config/config.yaml

# ... existing config sections ...

# New: Progress Tracking Configuration
progress:
  enabled: true
  checkpoint_interval_files: 5
  checkpoint_interval_minutes: 10
  dashboard_enabled: true
  save_progress_reports: true

# New: Quality Monitoring Configuration  
quality:
  monitoring_enabled: true
  alert_threshold: 0.6
  save_quality_reports: true
  cache_size: 1000
  trend_analysis_enabled: true

# New: Input Processing Configuration
input:
  file_patterns: ["*.txt"]
  ignore_patterns: [".DS_Store", "*.tmp"]
  parallel_processing: false
  max_concurrent_files: 3
```

## 📋 Enhanced Commands Reference

### Processing Commands

```bash
# Enhanced processing with full tracking
python setforge_enhanced_cli.py process INPUT_DIR OUTPUT_FILE [options]

Options:
  --config CONFIG_FILE          # Use custom config
  --dashboard / --no-dashboard   # Enable/disable live dashboard
  --checkpoint-interval N        # Checkpoint every N files
  --quality-threshold SCORE      # Quality alert threshold

# Examples:
python setforge_enhanced_cli.py process data/educational output/dataset.jsonl --dashboard
python setforge_enhanced_cli.py process data/educational output/dataset.jsonl --checkpoint-interval 3
```

### Resume Commands

```bash
# Resume from latest checkpoint
python setforge_enhanced_cli.py resume INPUT_DIR OUTPUT_FILE

# Resume from specific checkpoint
python setforge_enhanced_cli.py resume INPUT_DIR OUTPUT_FILE --checkpoint CHECKPOINT_FILE

# Examples:
python setforge_enhanced_cli.py resume data/educational output/dataset.jsonl
```

### Monitoring Commands

```bash
# Live status monitoring
python setforge_enhanced_cli.py status [options]

Options:
  --live                         # Live updating display
  --refresh-interval SECONDS     # Update interval for live mode
  --config CONFIG_FILE           # Use custom config

# Examples:
python setforge_enhanced_cli.py status --live
python setforge_enhanced_cli.py status --live --refresh-interval 2
```

### Reporting Commands

```bash
# Quality analysis report
python setforge_enhanced_cli.py quality-report [options]

Options:
  --output REPORT_FILE           # Save report to file
  --format FORMAT                # json, markdown, or console

# Performance analysis report  
python setforge_enhanced_cli.py performance-report [options]

# Examples:
python setforge_enhanced_cli.py quality-report --output reports/quality.md --format markdown
python setforge_enhanced_cli.py performance-report --output reports/performance.json
```

### Checkpoint Management Commands

```bash
# List available checkpoints
python setforge_enhanced_cli.py list-checkpoints

# Clear all checkpoints
python setforge_enhanced_cli.py clear-checkpoints [options]

Options:
  --confirm                      # Skip confirmation prompt

# Examples:
python setforge_enhanced_cli.py list-checkpoints
python setforge_enhanced_cli.py clear-checkpoints --confirm
```

### Utility Commands

```bash
# Enhanced cost estimation
python setforge_enhanced_cli.py estimate INPUT_DIR [options]

Options:
  --config CONFIG_FILE           # Use custom config
  --include-existing             # Include existing output in estimate

# Health check with enhanced validation
python setforge_enhanced_cli.py health-check [options]

Options:
  --comprehensive                # Run comprehensive health check

# Examples:
python setforge_enhanced_cli.py estimate data/educational --include-existing
python setforge_enhanced_cli.py health-check --comprehensive
```

## 📊 Enhanced Output Structure

### Main Dataset Output
```jsonl
# output/qa_dataset_enhanced.jsonl
{"question": "...", "answer": "...", "chunk_id": "...", "source_text": "...", "source_file": "...", "validation": {"overall_score": 0.95, "confidence_level": "high", "diagnostics": []}, "metadata": {"processing_time": 1.2, "model_used": "llama3-8b", "cost": 0.001}, "audit_trail": {"created_at": "2025-01-01T...", "config_hash": "abc123..."}}
```

### Enhanced Reports
```
output/
├── qa_dataset_enhanced.jsonl     # Main dataset
├── progress_report.json          # Processing progress details
├── quality_report.json           # Quality analysis report
├── quality_data.json             # Detailed quality metrics
├── checkpoints/                  # Checkpoint directory
│   ├── latest_checkpoint.json    # Latest processing state
│   ├── checkpoint_001.json       # Numbered checkpoints
│   └── emergency_checkpoint_*.json # Emergency saves
└── logs/                         # Enhanced logging
    ├── setforge_enhanced.log     # Main processing log
    ├── quality_monitor.log       # Quality monitoring log
    └── progress_tracker.log      # Progress tracking log
```

## 🔄 Resume Scenarios

### Scenario 1: Graceful Interruption (Ctrl+C)
```bash
# During processing, press Ctrl+C
^C
⚠️  Processing interrupted by user
💾 Progress has been saved automatically
🔄 Resume anytime with:
   python setforge_enhanced_cli.py resume data/educational output/qa_dataset.jsonl
```

### Scenario 2: System Crash or Error
```bash
# If processing fails unexpectedly
❌ Processing failed with exception: Connection timeout
💾 Emergency checkpoint saved: output/checkpoints/emergency_checkpoint_20250101_143022.json
🔄 You may be able to resume from this checkpoint
```

### Scenario 3: Manual Resume Check
```bash
# Check available checkpoints
python setforge_enhanced_cli.py list-checkpoints

📋 Available Checkpoints:
   ├── latest_checkpoint.json (15 files processed, 3,245 QA pairs)
   ├── checkpoint_001.json (10 files processed, 2,156 QA pairs)
   └── emergency_checkpoint_20250101_143022.json (12 files processed)

# Resume from latest
python setforge_enhanced_cli.py resume data/educational output/qa_dataset.jsonl
```

## 📈 Quality Monitoring

### Quality Scoring System
The enhanced system uses weighted quality scoring:

```python
overall_score = (
    extractive * 0.4 +          # Most important: must be extractive
    non_hallucination * 0.3 +   # Critical: no hallucinations  
    relevancy * 0.2 +           # Important: semantic relevancy
    quality * 0.1               # Nice to have: content quality
)
```

### Quality Alerts
Automatic alerts for:
- Quality scores below threshold (default: 0.6)
- Hallucination detection
- Extraction failures
- Quality trend degradation

### Quality Reports
Comprehensive analysis including:
- Quality distribution (excellent/good/poor)
- Trend analysis over time
- Source file quality breakdown
- Alert summary and recommendations

## 🚀 Performance Features

### Processing Optimizations
- **Micro-chunking**: 200-400 token chunks with 50-token overlap
- **Enhanced generation**: 3-5 questions per chunk with paraphrasing
- **Intelligent deduplication**: Fuzzy matching + semantic similarity
- **Batch processing**: Optimized for API efficiency
- **Caching**: Validation result caching for performance

### Monitoring Features
- **Real-time metrics**: Processing speed, ETA, cost tracking
- **Resource monitoring**: Memory usage, disk space, API rate limits
- **Performance trends**: Speed analysis, efficiency scoring
- **Cost optimization**: Dynamic batch sizing, budget alerts

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### Issue: "Import error: No module named 'setforge_enhanced'"
```bash
# Solution: Ensure you're in the SetForge directory
cd /path/to/SetForge
python setforge_enhanced_cli.py process ...
```

#### Issue: "DIGITALOCEAN_API_KEY environment variable not set"
```bash
# Solution: Set your API key
export DIGITALOCEAN_API_KEY=your_key_here

# Or for testing without API calls
export SETFORGE_DRY_RUN=true
```

#### Issue: "No checkpoints found"
```bash
# Solution: Check checkpoint directory
ls output/checkpoints/

# If empty, start fresh processing
python setforge_enhanced_cli.py process data/educational output/dataset.jsonl
```

#### Issue: Quality scores consistently low
```bash
# Solution: Check quality report for insights
python setforge_enhanced_cli.py quality-report

# Consider adjusting config
vim config/config.yaml
# Adjust qa.questions_per_chunk, validation.min_source_overlap, etc.
```

### Debug Mode
```bash
# Enable debug logging
export SETFORGE_LOG_LEVEL=DEBUG

# Run with comprehensive health check
python setforge_enhanced_cli.py health-check --comprehensive

# Check system status
python setforge_enhanced_cli.py status
```

## 📞 Support and Next Steps

### System Validation
1. Run health check: `python setforge_enhanced_cli.py health-check --comprehensive`
2. Test with small dataset: `python setforge_enhanced_cli.py process test_data output/test.jsonl`
3. Monitor live status: `python setforge_enhanced_cli.py status --live`

### Production Deployment
1. Set production environment: `export SETFORGE_ENV=production`
2. Configure logging: Check `config/config.yaml` logging section
3. Monitor resource usage during processing
4. Set up alerting for quality thresholds
5. Schedule regular checkpoint cleanup

### Performance Tuning
1. Adjust `qa.questions_per_chunk` based on content complexity
2. Tune `validation.min_source_overlap` for quality vs quantity balance
3. Configure `progress.checkpoint_interval_files` based on processing speed
4. Set `quality.alert_threshold` appropriate for your quality requirements

The enhanced SetForge system is now production-ready with comprehensive tracking, resumability, and quality assurance! 🚀
