#!/usr/bin/env python3
"""
Data Validator for TXT Dataset Generator
========================================

Comprehensive validation tool that checks:
1. Required fields presence and format
2. JSON/JSONL format validation
3. Duplicate detection and quality analysis
4. University and metadata distribution
5. Quality score thresholds
6. Cultural sensitivity and language integration

Usage:
    python data_validator.py <dataset_path> [--output report.json] [--fix-issues]
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple
from collections import defaultdict, Counter
import re
from datetime import datetime


class DatasetValidator:
    """Comprehensive dataset validator for production Q&A datasets."""
    
    def __init__(self):
        self.required_fields = {
            "question", "answer", "context", "university", "audience",
            "answer_type", "tone", "confidence_level", "source_file"
        }
        
        self.metadata_fields = {
            "student_persona", "question_complexity", "financial_details",
            "grade_calculation", "multi_university", "bengali_integration",
            "actionable_guidance", "difficulty_level", "expected_response_time",
            "requires_calculation", "requires_verification"
        }
        
        self.quality_fields = {
            "extractive_score", "factual_accuracy", "cultural_sensitivity",
            "uniqueness_score", "validation_status"
        }
        
        self.validation_results = {
            "total_entries": 0,
            "valid_entries": 0,
            "issues": [],
            "statistics": {},
            "recommendations": []
        }
    
    def validate_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """Main validation function."""
        
        print(f"🔍 Validating dataset: {dataset_path}")
        
        # Load dataset
        try:
            dataset = self._load_dataset(dataset_path)
        except Exception as e:
            return {"error": f"Failed to load dataset: {e}"}
        
        self.validation_results["total_entries"] = len(dataset)
        
        # Run validation checks
        self._validate_format(dataset)
        self._validate_required_fields(dataset)
        self._validate_data_types(dataset)
        self._validate_quality_scores(dataset)
        self._detect_duplicates(dataset)
        self._analyze_distribution(dataset)
        self._validate_cultural_elements(dataset)
        self._validate_extractive_content(dataset)
        
        # Generate statistics
        self._generate_statistics(dataset)
        
        # Generate recommendations
        self._generate_recommendations()
        
        return self.validation_results
    
    def _load_dataset(self, dataset_path: str) -> List[Dict[str, Any]]:
        """Load dataset from JSONL or JSON file."""
        
        dataset = []
        file_path = Path(dataset_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {dataset_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix == '.jsonl':
                # JSONL format
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        entry = json.loads(line)
                        dataset.append(entry)
                    except json.JSONDecodeError as e:
                        self.validation_results["issues"].append({
                            "type": "format_error",
                            "line": line_num,
                            "message": f"Invalid JSON: {e}"
                        })
            else:
                # JSON format
                try:
                    dataset = json.load(f)
                    if not isinstance(dataset, list):
                        raise ValueError("JSON file must contain a list of entries")
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON format: {e}")
        
        return dataset
    
    def _validate_format(self, dataset: List[Dict[str, Any]]):
        """Validate basic format requirements."""
        
        if not dataset:
            self.validation_results["issues"].append({
                "type": "empty_dataset",
                "severity": "critical",
                "message": "Dataset is empty"
            })
            return
        
        if len(dataset) < 10:
            self.validation_results["issues"].append({
                "type": "small_dataset",
                "severity": "warning",
                "message": f"Dataset has only {len(dataset)} entries (recommended: 100+)"
            })
    
    def _validate_required_fields(self, dataset: List[Dict[str, Any]]):
        """Validate that all required fields are present."""
        
        missing_fields_count = defaultdict(int)
        
        for i, entry in enumerate(dataset):
            if not isinstance(entry, dict):
                self.validation_results["issues"].append({
                    "type": "invalid_entry_type",
                    "entry_index": i,
                    "severity": "critical",
                    "message": f"Entry {i} is not a dictionary"
                })
                continue
            
            missing_fields = self.required_fields - set(entry.keys())
            
            if missing_fields:
                for field in missing_fields:
                    missing_fields_count[field] += 1
                
                self.validation_results["issues"].append({
                    "type": "missing_required_fields",
                    "entry_index": i,
                    "severity": "critical",
                    "fields": list(missing_fields),
                    "message": f"Entry {i} missing required fields: {', '.join(missing_fields)}"
                })
        
        # Report common missing fields
        if missing_fields_count:
            most_missing = sorted(missing_fields_count.items(), key=lambda x: x[1], reverse=True)
            self.validation_results["issues"].append({
                "type": "field_analysis",
                "severity": "info",
                "message": f"Most commonly missing fields: {most_missing[:3]}"
            })
    
    def _validate_data_types(self, dataset: List[Dict[str, Any]]):
        """Validate data types for key fields."""
        
        type_validations = {
            "question": str,
            "answer": str,
            "context": str,
            "university": str,
            "confidence_level": (int, float),
            "source_file": str
        }
        
        for i, entry in enumerate(dataset):
            for field, expected_type in type_validations.items():
                if field in entry:
                    if not isinstance(entry[field], expected_type):
                        self.validation_results["issues"].append({
                            "type": "invalid_data_type",
                            "entry_index": i,
                            "field": field,
                            "expected": str(expected_type),
                            "actual": str(type(entry[field])),
                            "severity": "error",
                            "message": f"Entry {i}: {field} should be {expected_type}, got {type(entry[field])}"
                        })
    
    def _validate_quality_scores(self, dataset: List[Dict[str, Any]]):
        """Validate quality score ranges and consistency."""
        
        score_fields = [
            "confidence_level",
            "extractive_score",
            "factual_accuracy", 
            "cultural_sensitivity",
            "uniqueness_score"
        ]
        
        low_quality_count = 0
        
        for i, entry in enumerate(dataset):
            # Check confidence level
            if "confidence_level" in entry:
                conf = entry["confidence_level"]
                if not (0.0 <= conf <= 1.0):
                    self.validation_results["issues"].append({
                        "type": "invalid_score_range",
                        "entry_index": i,
                        "field": "confidence_level",
                        "value": conf,
                        "severity": "error",
                        "message": f"Entry {i}: confidence_level {conf} not in range [0.0, 1.0]"
                    })
                
                if conf < 0.6:
                    low_quality_count += 1
            
            # Check quality scores in metadata
            if "quality" in entry:
                quality = entry["quality"]
                for field in self.quality_fields:
                    if field in quality and field.endswith("_score"):
                        score = quality[field]
                        if isinstance(score, (int, float)) and not (0.0 <= score <= 1.0):
                            self.validation_results["issues"].append({
                                "type": "invalid_score_range",
                                "entry_index": i,
                                "field": field,
                                "value": score,
                                "severity": "error",
                                "message": f"Entry {i}: {field} {score} not in range [0.0, 1.0]"
                            })
        
        # Report low quality entries
        if low_quality_count > len(dataset) * 0.2:  # More than 20% low quality
            self.validation_results["issues"].append({
                "type": "quality_concern",
                "severity": "warning",
                "count": low_quality_count,
                "percentage": (low_quality_count / len(dataset)) * 100,
                "message": f"{low_quality_count} entries ({(low_quality_count/len(dataset)*100):.1f}%) have low confidence scores (<0.6)"
            })
    
    def _detect_duplicates(self, dataset: List[Dict[str, Any]]):
        """Detect duplicate and near-duplicate questions."""
        
        questions = []
        duplicates = []
        near_duplicates = []
        
        for i, entry in enumerate(dataset):
            if "question" in entry:
                question = entry["question"].lower().strip()
                questions.append((i, question))
        
        # Exact duplicates
        question_counts = Counter([q for _, q in questions])
        exact_duplicates = {q: count for q, count in question_counts.items() if count > 1}
        
        if exact_duplicates:
            self.validation_results["issues"].append({
                "type": "exact_duplicates",
                "severity": "error",
                "count": len(exact_duplicates),
                "examples": list(exact_duplicates.keys())[:3],
                "message": f"Found {len(exact_duplicates)} exact duplicate questions"
            })
        
        # Near duplicates (Jaccard similarity > 0.8)
        for i, (idx1, q1) in enumerate(questions):
            for idx2, q2 in questions[i+1:]:
                similarity = self._calculate_similarity(q1, q2)
                if similarity > 0.8:
                    near_duplicates.append((idx1, idx2, similarity))
        
        if near_duplicates:
            self.validation_results["issues"].append({
                "type": "near_duplicates",
                "severity": "warning",
                "count": len(near_duplicates),
                "examples": near_duplicates[:3],
                "message": f"Found {len(near_duplicates)} near-duplicate question pairs"
            })
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts."""
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0
    
    def _analyze_distribution(self, dataset: List[Dict[str, Any]]):
        """Analyze distribution across universities, personas, etc."""
        
        distributions = {
            "universities": defaultdict(int),
            "personas": defaultdict(int),
            "question_complexity": defaultdict(int),
            "answer_types": defaultdict(int),
            "source_files": defaultdict(int)
        }
        
        for entry in dataset:
            # University distribution
            if "university" in entry:
                distributions["universities"][entry["university"]] += 1
            
            # Persona distribution
            if "metadata" in entry and "student_persona" in entry["metadata"]:
                distributions["personas"][entry["metadata"]["student_persona"]] += 1
            
            # Complexity distribution
            if "metadata" in entry and "question_complexity" in entry["metadata"]:
                distributions["question_complexity"][entry["metadata"]["question_complexity"]] += 1
            
            # Answer type distribution
            if "answer_type" in entry:
                distributions["answer_types"][entry["answer_type"]] += 1
            
            # Source file distribution
            if "source_file" in entry:
                distributions["source_files"][entry["source_file"]] += 1
        
        # Check for imbalanced distributions
        for category, dist in distributions.items():
            if dist:
                total = sum(dist.values())
                max_percentage = max(dist.values()) / total * 100
                
                if max_percentage > 70:  # One category dominates
                    dominant_category = max(dist.items(), key=lambda x: x[1])
                    self.validation_results["issues"].append({
                        "type": "imbalanced_distribution",
                        "category": category,
                        "dominant": dominant_category[0],
                        "percentage": max_percentage,
                        "severity": "warning",
                        "message": f"{category} distribution imbalanced: {dominant_category[0]} dominates with {max_percentage:.1f}%"
                    })
        
        self.validation_results["statistics"]["distributions"] = dict(distributions)
    
    def _validate_cultural_elements(self, dataset: List[Dict[str, Any]]):
        """Validate cultural sensitivity and Bengali integration."""
        
        bengali_count = 0
        bangladesh_specific = 0
        cultural_sensitivity_scores = []
        
        for entry in dataset:
            question = entry.get("question", "")
            answer = entry.get("answer", "")
            combined_text = (question + " " + answer).lower()
            
            # Check for Bengali text
            bengali_patterns = ['বিশ্ববিদ্যালয়', 'শিক্ষার্থী', 'টাকা', 'ভর্তি', 'এই']
            if any(pattern in answer for pattern in bengali_patterns):
                bengali_count += 1
            
            # Check for Bangladesh-specific content
            bangladesh_indicators = ['bangladeshi', 'bangladesh', 'bdt', 'taka', 'dhaka', 'chittagong']
            if any(indicator in combined_text for indicator in bangladesh_indicators):
                bangladesh_specific += 1
            
            # Collect cultural sensitivity scores
            if "quality" in entry and "cultural_sensitivity" in entry["quality"]:
                cultural_sensitivity_scores.append(entry["quality"]["cultural_sensitivity"])
        
        # Report cultural integration
        bengali_percentage = (bengali_count / len(dataset)) * 100
        bangladesh_percentage = (bangladesh_specific / len(dataset)) * 100
        
        if bengali_percentage < 10:
            self.validation_results["issues"].append({
                "type": "low_bengali_integration",
                "severity": "warning",
                "percentage": bengali_percentage,
                "message": f"Only {bengali_percentage:.1f}% of entries contain Bengali text (recommended: 15%+)"
            })
        
        if bangladesh_percentage < 50:
            self.validation_results["issues"].append({
                "type": "low_bangladesh_specificity",
                "severity": "warning", 
                "percentage": bangladesh_percentage,
                "message": f"Only {bangladesh_percentage:.1f}% of entries are Bangladesh-specific (recommended: 60%+)"
            })
        
        # Report average cultural sensitivity
        if cultural_sensitivity_scores:
            avg_cultural_score = sum(cultural_sensitivity_scores) / len(cultural_sensitivity_scores)
            if avg_cultural_score < 0.7:
                self.validation_results["issues"].append({
                    "type": "low_cultural_sensitivity",
                    "severity": "warning",
                    "average_score": avg_cultural_score,
                    "message": f"Average cultural sensitivity score {avg_cultural_score:.2f} is below threshold (0.7)"
                })
    
    def _validate_extractive_content(self, dataset: List[Dict[str, Any]]):
        """Validate that answers are extractive and not hallucinated."""
        
        low_extractive_count = 0
        hallucination_indicators = [
            "probably", "might be", "in my opinion", "i think", "perhaps",
            "could be", "maybe", "it seems", "appears to be"
        ]
        
        for i, entry in enumerate(dataset):
            answer = entry.get("answer", "").lower()
            
            # Check extractive score
            if "quality" in entry and "extractive_score" in entry["quality"]:
                extractive_score = entry["quality"]["extractive_score"]
                if extractive_score < 0.5:
                    low_extractive_count += 1
            
            # Check for hallucination indicators
            hallucination_count = sum(1 for indicator in hallucination_indicators if indicator in answer)
            if hallucination_count > 0:
                self.validation_results["issues"].append({
                    "type": "potential_hallucination",
                    "entry_index": i,
                    "indicators": [ind for ind in hallucination_indicators if ind in answer],
                    "severity": "error",
                    "message": f"Entry {i}: Answer contains hallucination indicators"
                })
        
        # Report low extractive content
        if low_extractive_count > len(dataset) * 0.1:  # More than 10%
            self.validation_results["issues"].append({
                "type": "low_extractive_content",
                "severity": "warning",
                "count": low_extractive_count,
                "percentage": (low_extractive_count / len(dataset)) * 100,
                "message": f"{low_extractive_count} entries have low extractive scores (<0.5)"
            })
    
    def _generate_statistics(self, dataset: List[Dict[str, Any]]):
        """Generate comprehensive statistics."""
        
        if not dataset:
            return
        
        # Basic statistics
        stats = {
            "total_entries": len(dataset),
            "valid_entries": len(dataset) - len([issue for issue in self.validation_results["issues"] 
                                                if issue.get("severity") == "critical"]),
            "avg_question_length": 0,
            "avg_answer_length": 0,
            "quality_metrics": {}
        }
        
        # Length statistics
        question_lengths = []
        answer_lengths = []
        
        for entry in dataset:
            if "question" in entry:
                question_lengths.append(len(entry["question"]))
            if "answer" in entry:
                answer_lengths.append(len(entry["answer"]))
        
        if question_lengths:
            stats["avg_question_length"] = sum(question_lengths) / len(question_lengths)
            stats["min_question_length"] = min(question_lengths)
            stats["max_question_length"] = max(question_lengths)
        
        if answer_lengths:
            stats["avg_answer_length"] = sum(answer_lengths) / len(answer_lengths)
            stats["min_answer_length"] = min(answer_lengths)
            stats["max_answer_length"] = max(answer_lengths)
        
        # Quality metrics
        quality_scores = {
            "confidence_level": [],
            "extractive_score": [],
            "factual_accuracy": [],
            "cultural_sensitivity": [],
            "uniqueness_score": []
        }
        
        for entry in dataset:
            if "confidence_level" in entry:
                quality_scores["confidence_level"].append(entry["confidence_level"])
            
            if "quality" in entry:
                quality = entry["quality"]
                for metric in quality_scores:
                    if metric in quality:
                        quality_scores[metric].append(quality[metric])
        
        for metric, scores in quality_scores.items():
            if scores:
                stats["quality_metrics"][f"avg_{metric}"] = sum(scores) / len(scores)
                stats["quality_metrics"][f"min_{metric}"] = min(scores)
                stats["quality_metrics"][f"max_{metric}"] = max(scores)
        
        self.validation_results["statistics"].update(stats)
    
    def _generate_recommendations(self):
        """Generate actionable recommendations based on validation results."""
        
        recommendations = []
        issues = self.validation_results["issues"]
        
        # Critical issues
        critical_issues = [issue for issue in issues if issue.get("severity") == "critical"]
        if critical_issues:
            recommendations.append({
                "priority": "high",
                "category": "data_integrity",
                "action": "Fix critical data issues before using dataset",
                "details": f"Found {len(critical_issues)} critical issues that prevent dataset use"
            })
        
        # Quality improvements
        low_quality_issues = [issue for issue in issues if "quality" in issue.get("type", "")]
        if low_quality_issues:
            recommendations.append({
                "priority": "medium",
                "category": "quality_improvement",
                "action": "Improve quality scores through better extraction and validation",
                "details": "Consider regenerating low-quality entries or enhancing extraction algorithms"
            })
        
        # Balance improvements
        imbalance_issues = [issue for issue in issues if "imbalanced" in issue.get("type", "")]
        if imbalance_issues:
            recommendations.append({
                "priority": "medium",
                "category": "balance_improvement",
                "action": "Rebalance dataset distribution across categories",
                "details": "Generate more content for underrepresented categories"
            })
        
        # Cultural enhancements
        cultural_issues = [issue for issue in issues if "cultural" in issue.get("type", "") or "bengali" in issue.get("type", "")]
        if cultural_issues:
            recommendations.append({
                "priority": "medium",
                "category": "cultural_enhancement",
                "action": "Increase Bengali integration and cultural specificity",
                "details": "Add more Bengali text and Bangladesh-specific context"
            })
        
        # Duplicate handling
        duplicate_issues = [issue for issue in issues if "duplicate" in issue.get("type", "")]
        if duplicate_issues:
            recommendations.append({
                "priority": "high",
                "category": "duplicate_removal",
                "action": "Remove or modify duplicate entries",
                "details": "Deduplicate dataset to improve training effectiveness"
            })
        
        self.validation_results["recommendations"] = recommendations
    
    def generate_report(self, output_path: str = None):
        """Generate comprehensive validation report."""
        
        report = {
            "validation_summary": {
                "total_entries": self.validation_results["total_entries"],
                "valid_entries": self.validation_results["valid_entries"],
                "issues_found": len(self.validation_results["issues"]),
                "validation_date": datetime.now().isoformat()
            },
            "issues_by_severity": self._group_issues_by_severity(),
            "statistics": self.validation_results.get("statistics", {}),
            "recommendations": self.validation_results.get("recommendations", []),
            "detailed_issues": self.validation_results["issues"]
        }
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"📋 Validation report saved to: {output_path}")
        
        return report
    
    def _group_issues_by_severity(self) -> Dict[str, int]:
        """Group issues by severity level."""
        
        severity_counts = defaultdict(int)
        
        for issue in self.validation_results["issues"]:
            severity = issue.get("severity", "unknown")
            severity_counts[severity] += 1
        
        return dict(severity_counts)
    
    def print_summary(self):
        """Print validation summary to console."""
        
        print("\n" + "="*60)
        print("📋 DATASET VALIDATION SUMMARY")
        print("="*60)
        
        total = self.validation_results["total_entries"]
        valid = self.validation_results["valid_entries"]
        issues = len(self.validation_results["issues"])
        
        print(f"📊 Total Entries: {total}")
        print(f"✅ Valid Entries: {valid} ({(valid/total*100):.1f}%)")
        print(f"⚠️  Issues Found: {issues}")
        
        # Group by severity
        severity_counts = self._group_issues_by_severity()
        if severity_counts:
            print("\nIssues by Severity:")
            for severity, count in severity_counts.items():
                icon = {"critical": "🔴", "error": "🟠", "warning": "🟡", "info": "🔵"}.get(severity, "⚪")
                print(f"  {icon} {severity.capitalize()}: {count}")
        
        # Quality metrics
        if "statistics" in self.validation_results and "quality_metrics" in self.validation_results["statistics"]:
            print("\n📈 Quality Metrics:")
            quality = self.validation_results["statistics"]["quality_metrics"]
            if "avg_confidence_level" in quality:
                print(f"  Average Confidence: {quality['avg_confidence_level']:.3f}")
            if "avg_extractive_score" in quality:
                print(f"  Average Extractive Score: {quality['avg_extractive_score']:.3f}")
            if "avg_cultural_sensitivity" in quality:
                print(f"  Average Cultural Sensitivity: {quality['avg_cultural_sensitivity']:.3f}")
        
        # Top recommendations
        recommendations = self.validation_results.get("recommendations", [])
        if recommendations:
            print("\n💡 Top Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec["priority"], "⚪")
                print(f"  {i}. {priority_icon} {rec['action']}")
        
        print("="*60)


def main():
    """CLI interface for dataset validation."""
    
    parser = argparse.ArgumentParser(description="Validate Q&A dataset for production use")
    parser.add_argument("dataset_path", help="Path to dataset file (.json or .jsonl)")
    parser.add_argument("--output", "-o", help="Output path for validation report")
    parser.add_argument("--summary-only", action="store_true", help="Show only summary (no detailed report)")
    
    args = parser.parse_args()
    
    # Validate dataset
    validator = DatasetValidator()
    result = validator.validate_dataset(args.dataset_path)
    
    if "error" in result:
        print(f"❌ Validation failed: {result['error']}")
        sys.exit(1)
    
    # Print summary
    validator.print_summary()
    
    # Generate detailed report
    if not args.summary_only:
        output_path = args.output or f"{Path(args.dataset_path).stem}_validation_report.json"
        validator.generate_report(output_path)
    
    # Return appropriate exit code
    critical_issues = len([issue for issue in result["issues"] if issue.get("severity") == "critical"])
    if critical_issues > 0:
        print(f"\n❌ Dataset has {critical_issues} critical issues - not ready for production")
        sys.exit(1)
    else:
        print(f"\n✅ Dataset validation completed - ready for use")
        sys.exit(0)


if __name__ == "__main__":
    main()
