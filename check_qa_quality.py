#!/usr/bin/env python3
"""
SetForge QA Quality Checker
============================

Comprehensive quality analysis tool for SetForge-generated QA datasets.
Performs extractive validation, hallucination detection, and quality scoring.

Usage:
    python check_qa_quality.py <dataset_file.jsonl> [--output report.json] [--threshold 0.8]

Author: SetForge Team
Date: July 26, 2025
"""

import json
import argparse
import re
import string
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
import sys

# Optional dependencies
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("⚠️  sentence-transformers not available. Semantic similarity checks disabled.")


@dataclass
class QualityIssue:
    """Represents a quality issue found in a QA pair"""
    issue_type: str
    severity: str  # 'critical', 'warning', 'info'
    description: str
    expected: Optional[str] = None
    actual: Optional[str] = None


@dataclass
class QAQualityResult:
    """Quality check results for a single QA pair"""
    index: int
    file: str
    question: str
    answer: str
    is_valid: bool
    quality_score: float
    validation_score: Optional[float]
    issues: List[QualityIssue]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'index': self.index,
            'file': self.file,
            'question': self.question,
            'answer': self.answer,
            'is_valid': self.is_valid,
            'quality_score': self.quality_score,
            'validation_score': self.validation_score,
            'issues': [asdict(issue) for issue in self.issues]
        }


class QAQualityChecker:
    """Comprehensive quality checker for SetForge QA datasets"""
    
    def __init__(self, 
                 min_question_length: int = 8,
                 max_question_length: int = 300,
                 min_answer_length: int = 3,
                 max_answer_length: int = 500,
                 quality_threshold: float = 0.8,
                 semantic_threshold: float = 0.6):
        
        self.min_question_length = min_question_length
        self.max_question_length = max_question_length
        self.min_answer_length = min_answer_length
        self.max_answer_length = max_answer_length
        self.quality_threshold = quality_threshold
        self.semantic_threshold = semantic_threshold
        
        # Forbidden patterns that indicate hallucination
        self.forbidden_patterns = [
            r'\bin my opinion\b',
            r'\bi think\b',
            r'\bi believe\b',
            r'\bprobably\b',
            r'\bmight be\b',
            r'\bcould be\b',
            r'\bseems like\b',
            r'\bappears to be\b',
            r'\blikely\b',
            r'\bpossibly\b',
            r'\bperhaps\b',
            r'\bmaybe\b',
            r'\bassume\b',
            r'\bguess\b',
            r'\bspeculate\b'
        ]
        
        # Valid question types
        self.valid_question_types = {
            'factual', 'definition', 'process', 'comparison', 'list', 
            'explanation', 'analytical', 'descriptive'
        }
        
        # Initialize embeddings model if available
        self.embeddings_model = None
        if EMBEDDINGS_AVAILABLE:
            try:
                print("📊 Loading sentence-transformers model for semantic analysis...")
                self.embeddings_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                print("✅ Semantic similarity checks enabled")
            except Exception as e:
                print(f"⚠️  Failed to load embeddings model: {e}")
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison (lowercase, remove punctuation/whitespace)"""
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation and extra whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def is_extractive(self, answer: str, source_text: str) -> Tuple[bool, float]:
        """Check if answer is extractive (substring of source text)"""
        if not answer or not source_text:
            return False, 0.0
        
        # Normalize both texts
        norm_answer = self.normalize_text(answer)
        norm_source = self.normalize_text(source_text)
        
        # Check if answer is a substring of source
        if norm_answer in norm_source:
            return True, 1.0
        
        # Check word overlap for partial matches
        answer_words = set(norm_answer.split())
        source_words = set(norm_source.split())
        
        if len(answer_words) == 0:
            return False, 0.0
        
        overlap = len(answer_words.intersection(source_words))
        overlap_ratio = overlap / len(answer_words)
        
        # Consider it extractive if >80% words overlap
        is_extractive = overlap_ratio >= 0.8
        return is_extractive, overlap_ratio
    
    def check_hallucination(self, text: str) -> List[str]:
        """Check for hallucination patterns in text"""
        found_patterns = []
        for pattern in self.forbidden_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                found_patterns.append(pattern.strip(r'\b'))
        return found_patterns
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> Optional[float]:
        """Calculate semantic similarity between two texts"""
        if not self.embeddings_model or not text1 or not text2:
            return None
        
        try:
            embeddings = self.embeddings_model.encode([text1, text2])
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            return float(similarity)
        except Exception as e:
            print(f"⚠️  Semantic similarity calculation failed: {e}")
            return None
    
    def check_qa_pair(self, qa_data: Dict[str, Any], index: int) -> QAQualityResult:
        """Perform comprehensive quality check on a single QA pair"""
        issues = []
        
        # Extract required fields
        question = qa_data.get('question', '')
        answer = qa_data.get('answer', '')
        source_text = qa_data.get('source_text', '')
        file = qa_data.get('file', 'unknown')
        question_type = qa_data.get('question_type', '')
        
        # Extract validation/quality scores
        validation_data = qa_data.get('validation', {})
        validation_score = validation_data.get('overall_score') if validation_data else None
        if validation_score is None:
            validation_score = qa_data.get('quality_score')
        
        # 1. Length checks
        if len(question) < self.min_question_length:
            issues.append(QualityIssue(
                'length', 'critical',
                f'Question too short ({len(question)} chars)',
                f'>= {self.min_question_length} chars',
                f'{len(question)} chars'
            ))
        
        if len(question) > self.max_question_length:
            issues.append(QualityIssue(
                'length', 'warning',
                f'Question too long ({len(question)} chars)',
                f'<= {self.max_question_length} chars',
                f'{len(question)} chars'
            ))
        
        if len(answer) < self.min_answer_length:
            issues.append(QualityIssue(
                'length', 'critical',
                f'Answer too short ({len(answer)} chars)',
                f'>= {self.min_answer_length} chars',
                f'{len(answer)} chars'
            ))
        
        if len(answer) > self.max_answer_length:
            issues.append(QualityIssue(
                'length', 'warning',
                f'Answer too long ({len(answer)} chars)',
                f'<= {self.max_answer_length} chars',
                f'{len(answer)} chars'
            ))
        
        # 2. Extractive check
        is_extractive, overlap_ratio = self.is_extractive(answer, source_text)
        if not is_extractive:
            issues.append(QualityIssue(
                'extractive', 'critical',
                f'Answer not extractive (word overlap: {overlap_ratio:.2f})',
                '>= 0.8 word overlap',
                f'{overlap_ratio:.2f} word overlap'
            ))
        
        # 3. Hallucination check
        question_hallucinations = self.check_hallucination(question)
        answer_hallucinations = self.check_hallucination(answer)
        
        if question_hallucinations:
            issues.append(QualityIssue(
                'hallucination', 'critical',
                f'Question contains forbidden patterns: {", ".join(question_hallucinations)}',
                'No opinion/speculation patterns',
                f'Found: {", ".join(question_hallucinations)}'
            ))
        
        if answer_hallucinations:
            issues.append(QualityIssue(
                'hallucination', 'critical',
                f'Answer contains forbidden patterns: {", ".join(answer_hallucinations)}',
                'No opinion/speculation patterns',
                f'Found: {", ".join(answer_hallucinations)}'
            ))
        
        # 4. Question type check
        if question_type and question_type not in self.valid_question_types:
            issues.append(QualityIssue(
                'question_type', 'warning',
                f'Invalid question type: {question_type}',
                f'One of: {", ".join(sorted(self.valid_question_types))}',
                question_type
            ))
        
        # 5. Quality score check
        if validation_score is not None and validation_score < self.quality_threshold:
            issues.append(QualityIssue(
                'quality_score', 'warning',
                f'Quality score below threshold ({validation_score:.3f})',
                f'>= {self.quality_threshold}',
                f'{validation_score:.3f}'
            ))
        
        # 6. Semantic similarity check (if available)
        semantic_score = None
        if self.embeddings_model and source_text:
            semantic_score = self.calculate_semantic_similarity(answer, source_text)
            if semantic_score is not None and semantic_score < self.semantic_threshold:
                issues.append(QualityIssue(
                    'semantic', 'warning',
                    f'Low semantic similarity ({semantic_score:.3f})',
                    f'>= {self.semantic_threshold}',
                    f'{semantic_score:.3f}'
                ))
        
        # Determine overall validity
        critical_issues = [issue for issue in issues if issue.severity == 'critical']
        is_valid = len(critical_issues) == 0
        
        # Calculate overall quality score
        quality_score = validation_score if validation_score is not None else 0.0
        if semantic_score is not None:
            quality_score = max(quality_score, semantic_score)
        
        return QAQualityResult(
            index=index,
            file=file,
            question=question,
            answer=answer,
            is_valid=is_valid,
            quality_score=quality_score,
            validation_score=validation_score,
            issues=issues
        )
    
    def load_dataset(self, file_path: str) -> List[Dict[str, Any]]:
        """Load QA pairs from JSONL file, skipping metadata"""
        qa_pairs = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        
                        # Skip metadata lines
                        if data.get('__type') == 'metadata':
                            continue
                        
                        # Check if it's a QA pair (has question and answer)
                        if 'question' in data and 'answer' in data:
                            qa_pairs.append(data)
                    
                    except json.JSONDecodeError as e:
                        print(f"⚠️  Skipping invalid JSON on line {line_num}: {e}")
                        continue
        
        except FileNotFoundError:
            print(f"❌ Dataset file not found: {file_path}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            sys.exit(1)
        
        return qa_pairs
    
    def analyze_dataset(self, file_path: str) -> Dict[str, Any]:
        """Perform comprehensive analysis of the entire dataset"""
        print(f"🔍 Loading dataset: {file_path}")
        qa_pairs = self.load_dataset(file_path)
        
        if not qa_pairs:
            print("❌ No QA pairs found in dataset")
            return {}
        
        print(f"📊 Analyzing {len(qa_pairs)} QA pairs...")
        
        results = []
        issue_counter = defaultdict(int)
        severity_counter = defaultdict(int)
        quality_scores = []
        validation_scores = []
        
        # Process each QA pair
        for i, qa_data in enumerate(qa_pairs):
            result = self.check_qa_pair(qa_data, i)
            results.append(result)
            
            # Count issues
            for issue in result.issues:
                issue_counter[issue.issue_type] += 1
                severity_counter[issue.severity] += 1
            
            # Collect scores
            if result.quality_score > 0:
                quality_scores.append(result.quality_score)
            if result.validation_score is not None:
                validation_scores.append(result.validation_score)
        
        # Calculate statistics
        total_pairs = len(results)
        valid_pairs = sum(1 for r in results if r.is_valid)
        invalid_pairs = total_pairs - valid_pairs
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        avg_validation = sum(validation_scores) / len(validation_scores) if validation_scores else 0.0
        
        # Quality distribution
        quality_dist = {
            'excellent': len([s for s in quality_scores if s >= 0.9]),
            'good': len([s for s in quality_scores if 0.8 <= s < 0.9]),
            'fair': len([s for s in quality_scores if 0.7 <= s < 0.8]),
            'poor': len([s for s in quality_scores if s < 0.7])
        }
        
        # File distribution
        file_counter = Counter(r.file for r in results)
        
        # Question type distribution
        question_types = []
        for qa_data in qa_pairs:
            qt = qa_data.get('question_type')
            if qt:
                question_types.append(qt)
        question_type_dist = Counter(question_types)
        
        return {
            'summary': {
                'total_pairs': total_pairs,
                'valid_pairs': valid_pairs,
                'invalid_pairs': invalid_pairs,
                'validity_rate': valid_pairs / total_pairs if total_pairs > 0 else 0.0,
                'avg_quality_score': avg_quality,
                'avg_validation_score': avg_validation
            },
            'issues': dict(issue_counter),
            'severity': dict(severity_counter),
            'quality_distribution': quality_dist,
            'file_distribution': dict(file_counter.most_common(10)),
            'question_type_distribution': dict(question_type_dist),
            'flagged_pairs': [r.to_dict() for r in results if not r.is_valid],
            'all_results': [r.to_dict() for r in results]
        }
    
    def print_report(self, analysis: Dict[str, Any]) -> None:
        """Print comprehensive quality report to console"""
        summary = analysis['summary']
        
        print("\n" + "="*60)
        print("🔍 SETFORGE QA QUALITY ANALYSIS REPORT")
        print("="*60)
        
        # Overall statistics
        print(f"\n📊 OVERALL STATISTICS:")
        print(f"   Total QA pairs: {summary['total_pairs']:,}")
        print(f"   Valid pairs: {summary['valid_pairs']:,}")
        print(f"   Invalid pairs: {summary['invalid_pairs']:,}")
        print(f"   Validity rate: {summary['validity_rate']:.1%}")
        print(f"   Average quality score: {summary['avg_quality_score']:.3f}")
        print(f"   Average validation score: {summary['avg_validation_score']:.3f}")
        
        # Quality distribution
        quality_dist = analysis['quality_distribution']
        total_scored = sum(quality_dist.values())
        if total_scored > 0:
            print(f"\n🎯 QUALITY DISTRIBUTION:")
            for tier, count in quality_dist.items():
                percentage = count / total_scored * 100
                print(f"   {tier.capitalize()}: {count:,} ({percentage:.1f}%)")
        
        # Issue breakdown
        issues = analysis['issues']
        if issues:
            print(f"\n⚠️  ISSUE BREAKDOWN:")
            for issue_type, count in sorted(issues.items()):
                print(f"   {issue_type.replace('_', ' ').title()}: {count:,}")
        
        # Severity breakdown
        severity = analysis['severity']
        if severity:
            print(f"\n🚨 SEVERITY BREAKDOWN:")
            for sev, count in sorted(severity.items()):
                print(f"   {sev.capitalize()}: {count:,}")
        
        # Question types
        qt_dist = analysis['question_type_distribution']
        if qt_dist:
            print(f"\n❓ QUESTION TYPES:")
            for qtype, count in sorted(qt_dist.items(), key=lambda x: x[1], reverse=True):
                print(f"   {qtype}: {count:,}")
        
        # Top source files
        file_dist = analysis['file_distribution']
        if file_dist:
            print(f"\n📁 TOP SOURCE FILES:")
            for file, count in list(file_dist.items())[:5]:
                print(f"   {file}: {count:,}")
        
        # Flagged pairs
        flagged = analysis['flagged_pairs']
        if flagged:
            print(f"\n🚩 FLAGGED QA PAIRS ({len(flagged):,}):")
            for i, pair in enumerate(flagged[:5]):  # Show first 5
                print(f"\n   {i+1}. File: {pair['file']}")
                print(f"      Q: {pair['question'][:100]}...")
                print(f"      A: {pair['answer'][:100]}...")
                print(f"      Issues: {len(pair['issues'])}")
                for issue in pair['issues']:
                    print(f"        - {issue['severity'].upper()}: {issue['description']}")
            
            if len(flagged) > 5:
                print(f"      ... and {len(flagged) - 5} more flagged pairs")
        
        # Overall assessment
        print(f"\n🏁 OVERALL ASSESSMENT:")
        validity_rate = summary['validity_rate']
        avg_quality = summary['avg_quality_score']
        
        if validity_rate >= 0.95 and avg_quality >= 0.9:
            print("   ✅ EXCELLENT: Dataset meets high quality standards")
        elif validity_rate >= 0.9 and avg_quality >= 0.8:
            print("   ✅ GOOD: Dataset meets acceptable quality standards")
        elif validity_rate >= 0.8 and avg_quality >= 0.7:
            print("   ⚠️  FAIR: Dataset needs some improvement")
        else:
            print("   ❌ POOR: Dataset requires significant quality improvements")
        
        print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description='SetForge QA Quality Checker - Comprehensive quality analysis for QA datasets',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        'dataset_file',
        help='Path to the JSONL dataset file to analyze'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file for detailed report (JSON format)'
    )
    
    parser.add_argument(
        '--threshold', '-t',
        type=float,
        default=0.8,
        help='Quality score threshold for flagging pairs'
    )
    
    parser.add_argument(
        '--min-question-length',
        type=int,
        default=8,
        help='Minimum question length in characters'
    )
    
    parser.add_argument(
        '--min-answer-length',
        type=int,
        default=3,
        help='Minimum answer length in characters'
    )
    
    parser.add_argument(
        '--semantic-threshold',
        type=float,
        default=0.6,
        help='Semantic similarity threshold (requires sentence-transformers)'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.dataset_file).exists():
        print(f"❌ Dataset file not found: {args.dataset_file}")
        sys.exit(1)
    
    # Initialize checker
    checker = QAQualityChecker(
        min_question_length=args.min_question_length,
        min_answer_length=args.min_answer_length,
        quality_threshold=args.threshold,
        semantic_threshold=args.semantic_threshold
    )
    
    # Analyze dataset
    analysis = checker.analyze_dataset(args.dataset_file)
    
    if not analysis:
        print("❌ Analysis failed")
        sys.exit(1)
    
    # Print report
    checker.print_report(analysis)
    
    # Save detailed report if requested
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Detailed report saved to: {args.output}")
        except Exception as e:
            print(f"⚠️  Failed to save report: {e}")


if __name__ == '__main__':
    main()
