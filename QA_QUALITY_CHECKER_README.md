# SetForge QA Quality Checker

A comprehensive quality analysis tool for SetForge-generated question-answer datasets. This tool performs detailed validation of QA pairs to ensure high-quality, extractive, and hallucination-free content.

## 🎯 Features

### Core Quality Checks
- **✅ Extractive Validation**: Ensures answers are direct substrings of source text
- **📏 Length Validation**: Validates question/answer length requirements  
- **🚫 Hallucination Detection**: Identifies opinion/speculation patterns
- **🎯 Semantic Analysis**: Optional similarity scoring with embeddings
- **📊 Quality Scoring**: Validates against SetForge quality thresholds
- **🏷️ Type Validation**: Ensures valid question types

### Advanced Features
- **📈 Batch Analysis**: Process entire datasets efficiently
- **📋 Detailed Reporting**: Comprehensive statistics and issue breakdown
- **🔍 Filtering**: Separate high/low quality pairs automatically
- **📄 Export Options**: JSON/CSV output for further analysis
- **🛠️ Customizable**: Extend validation rules for specific requirements
- **⚡ Performance**: Optimized for large datasets

## 🚀 Quick Start

### Basic Usage
```bash
# Analyze a SetForge dataset
python check_qa_quality.py educational_dataset_final.jsonl

# With detailed output
python check_qa_quality.py dataset.jsonl --output report.json

# Custom quality threshold
python check_qa_quality.py dataset.jsonl --threshold 0.9
```

### Command Line Options
```bash
python check_qa_quality.py <dataset.jsonl> [OPTIONS]

Options:
  --output, -o              Output file for detailed report (JSON)
  --threshold, -t           Quality score threshold (default: 0.8)
  --min-question-length     Minimum question length (default: 8)
  --min-answer-length       Minimum answer length (default: 3)
  --semantic-threshold      Semantic similarity threshold (default: 0.6)
```

## 📊 Quality Checks Performed

### 1. Extractive Validation
Ensures answers are extractive (directly from source text):
- **Direct substring matching** (case-insensitive)
- **Word overlap analysis** (≥80% overlap required)
- **Normalization** of punctuation and whitespace

### 2. Length Validation
Validates content length requirements:
- **Question length**: 8-300 characters (configurable)
- **Answer length**: 3-500 characters (configurable)
- **Severity**: Critical for too short, warning for too long

### 3. Hallucination Detection
Identifies problematic opinion/speculation patterns:
```
Forbidden patterns:
• "in my opinion", "I think", "I believe"
• "probably", "might be", "could be"  
• "seems like", "appears to be"
• "likely", "possibly", "perhaps"
• "maybe", "assume", "guess", "speculate"
```

### 4. Question Type Validation
Ensures valid question types:
```
Valid types:
• factual, definition, process
• comparison, list, explanation
• analytical, descriptive
```

### 5. Quality Score Validation
Validates against SetForge quality thresholds:
- **Default threshold**: 0.8
- **Extractive score**: Direct from validation metadata
- **Overall score**: Weighted combination of metrics

### 6. Semantic Analysis (Optional)
Uses sentence-transformers for semantic similarity:
- **Model**: all-MiniLM-L6-v2 (lightweight, fast)
- **Threshold**: 0.6 (configurable)
- **Purpose**: Detect semantic drift from source

## 📈 Sample Output

```
============================================================
🔍 SETFORGE QA QUALITY ANALYSIS REPORT
============================================================

📊 OVERALL STATISTICS:
   Total QA pairs: 400
   Valid pairs: 400
   Invalid pairs: 0
   Validity rate: 100.0%
   Average quality score: 0.939
   Average validation score: 0.939

🎯 QUALITY DISTRIBUTION:
   Excellent: 400 (100.0%)
   Good: 0 (0.0%)
   Fair: 0 (0.0%)
   Poor: 0 (0.0%)

❓ QUESTION TYPES:
   factual: 181
   definition: 85
   list: 69
   process: 55
   comparison: 10

📁 TOP SOURCE FILES:
   real_world_questions.txt: 40
   university_comparison.txt: 23
   visa_requirements.txt: 18

🏁 OVERALL ASSESSMENT:
   ✅ EXCELLENT: Dataset meets high quality standards
============================================================
```

## 🛠️ Programmatic Usage

### Basic Analysis
```python
from check_qa_quality import QAQualityChecker

# Initialize checker
checker = QAQualityChecker(quality_threshold=0.8)

# Analyze single QA pair
qa_data = {
    "question": "What is the minimum balance required?",
    "answer": "BDT 1,00,000", 
    "source_text": "Bank statement showing minimum balance of BDT 1,00,000.",
    "question_type": "factual"
}

result = checker.check_qa_pair(qa_data, 0)
print(f"Valid: {result.is_valid}")
print(f"Quality: {result.quality_score}")
print(f"Issues: {len(result.issues)}")
```

### Batch Analysis
```python
# Analyze entire dataset
analysis = checker.analyze_dataset("dataset.jsonl")

# Access results
summary = analysis['summary']
flagged_pairs = analysis['flagged_pairs']
quality_dist = analysis['quality_distribution']

print(f"Validity rate: {summary['validity_rate']:.1%}")
print(f"Flagged pairs: {len(flagged_pairs)}")
```

### Custom Validation Rules
```python
class CustomQAChecker(QAQualityChecker):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Add custom forbidden patterns
        self.forbidden_patterns.extend([
            r'\bobviously\b',
            r'\bclearly\b'
        ])
    
    def check_custom_rules(self, qa_data):
        """Add domain-specific validation"""
        issues = []
        
        # Custom rule: Educational content should be formal
        if qa_data.get('answer', '').lower().count('lol') > 0:
            issues.append({
                'type': 'formality',
                'severity': 'warning',
                'description': 'Informal language detected'
            })
        
        return issues
```

## 📋 Quality Assessment Criteria

### Excellent (≥95% valid, ≥0.9 avg quality)
- ✅ All critical checks pass
- ✅ High extractive accuracy
- ✅ No hallucinations detected
- ✅ Consistent quality scores

### Good (≥90% valid, ≥0.8 avg quality)  
- ✅ Most critical checks pass
- ⚠️ Minor length/formatting issues
- ✅ Low hallucination rate
- ✅ Acceptable quality scores

### Fair (≥80% valid, ≥0.7 avg quality)
- ⚠️ Some quality issues present
- ⚠️ Moderate extractive accuracy
- ⚠️ Some hallucinations detected
- ⚠️ Mixed quality scores

### Poor (<80% valid, <0.7 avg quality)
- ❌ Significant quality problems
- ❌ Low extractive accuracy  
- ❌ High hallucination rate
- ❌ Inconsistent quality

## 🔧 Installation & Dependencies

### Required Dependencies
```bash
pip install json argparse pathlib collections dataclasses
```

### Optional Dependencies (Enhanced Features)
```bash
# For semantic similarity analysis
pip install sentence-transformers

# For advanced text processing  
pip install nltk spacy

# For data export/visualization
pip install pandas matplotlib seaborn
```

## 📄 Output Formats

### Console Report
- Human-readable summary
- Key statistics and distributions
- Sample flagged pairs
- Overall assessment

### JSON Report (--output)
```json
{
  "summary": {
    "total_pairs": 400,
    "valid_pairs": 400,
    "validity_rate": 1.0,
    "avg_quality_score": 0.939
  },
  "quality_distribution": {
    "excellent": 400,
    "good": 0,
    "fair": 0, 
    "poor": 0
  },
  "flagged_pairs": [
    {
      "index": 42,
      "question": "What do you think...",
      "issues": [
        {
          "issue_type": "hallucination",
          "severity": "critical",
          "description": "Question contains forbidden patterns"
        }
      ]
    }
  ]
}
```

## 🎯 Use Cases

### 1. Dataset Validation
- Validate SetForge output before training
- Ensure quality standards for production
- Identify problematic patterns early

### 2. Quality Improvement
- Filter high-quality subsets
- Identify common failure modes
- Guide prompt engineering improvements

### 3. Research & Analysis
- Analyze quality trends across domains
- Compare different generation methods
- Benchmark against quality standards

### 4. Production Monitoring
- Continuous quality monitoring
- Automated quality gates
- Performance tracking over time

## 🤝 Integration with SetForge

This quality checker is designed to work seamlessly with SetForge datasets:

1. **Automatic Format Detection**: Handles SetForge JSONL format
2. **Metadata Awareness**: Skips metadata lines automatically  
3. **Score Integration**: Uses SetForge validation scores
4. **Source Tracking**: Leverages source text for extractive validation
5. **Type Compatibility**: Recognizes SetForge question types

## 📞 Support & Contributing

- **Issues**: Report bugs or request features
- **Documentation**: Comprehensive usage examples
- **Extensions**: Custom validation rules supported
- **Integration**: API for programmatic usage

---

**SetForge QA Quality Checker** - Ensuring high-quality, extractive, hallucination-free QA datasets for production ML/AI applications.
