#!/usr/bin/env python3
"""
SetForge Enhanced Quality Checker
=================================

Production-ready quality validation with integrated Bangladeshi grading system,
cultural authenticity checking, and comprehensive quality optimization.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import logging
from collections import Counter
import yaml

from datetime import datetime
import argparse

# Use centralized logging
logger = logging.getLogger("SetForge")

# Import Bangladeshi grading system for validation
GRADING_VALIDATION_AVAILABLE = False

@dataclass
class QualityMetrics:
    """Comprehensive quality metrics for Q&A pairs"""

    extractive_score: float
    relevance_score: float
    answer_length: int
    has_specific_details: bool
    bangladeshi_focus: bool
    linguistic_quality: float
    content_specificity: float
    overall_score: float
    grade_accuracy: float
    cultural_authenticity: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class QualityChecker:
    """Enhanced quality checker with Bangladeshi grading integration"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_default_config()

        # Initialize grading system with fallback
        self.grading_validation_available = False
        
        # Quality thresholds from config
        self.min_extractive_score = self.config.get("quality_thresholds", {}).get(
            "min_extractive_score", 0.6
        )
        self.min_relevance_score = self.config.get("quality_thresholds", {}).get(
            "min_relevance_score", 0.7
        )
        self.min_overall_score = self.config.get("quality_thresholds", {}).get(
            "min_overall_score", 0.7
        )

        # Bangladeshi cultural indicators
        self.bangladeshi_keywords = [
            "bangladeshi students",
            "from bangladesh",
            "ssc",
            "hsc",
            "dakhil",
            "alim",
            "taka",
            "bdt",
            "dhaka",
            "chittagong",
            "sylhet",
            "rajshahi",
            "honours",
            "diploma",
            "cgpa",
            "gpa",
            "bangladesh",
            "bangladeshi",
        ]

        # Specific detail patterns
        self.specific_details = [
            r"₹[\d,]+",
            r"\d+%",
            r"\d+\.\d+\s*cgpa",
            r"\d+\.\d+\s*gpa",
            r"\d{4}-\d{2}",
            r"semester \d+",
            r"year \d+",
            r"ssc\s+\d+\.\d+",
            r"hsc\s+\d+\.\d+",
            r"diploma\s+\d+\.\d+",
        ]

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        try:
            with open("config.yaml", "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning("config.yaml not found, using minimal defaults")
            return {
                "quality_thresholds": {
                    "min_extractive_score": 0.6,
                    "min_relevance_score": 0.7,
                    "min_overall_score": 0.7,
                }
            }

    def calculate_extractive_score(self, answer: str, context: str) -> float:
        """Calculate how much of the answer is extracted from context."""
        if not context or not answer:
            return 0.0

        # Ensure both are strings and not None
        answer = str(answer) if answer is not None else ""
        context = str(context) if context is not None else ""
        
        if not answer or not context:
            return 0.0

        answer_words = set(answer.lower().split())
        context_words = set(context.lower().split())

        if not answer_words:
            return 0.0

        overlap = len(answer_words & context_words)
        return min(overlap / len(answer_words), 1.0)

    def calculate_relevance_score(self, question: str, answer: str) -> float:
        """Calculate semantic relevance between question and answer."""
        # Ensure both are strings and not None
        question = str(question) if question is not None else ""
        answer = str(answer) if answer is not None else ""
        
        if not question or not answer:
            return 0.0

        question_words = set(question.lower().split())
        answer_words = set(answer.lower().split())

        if not question_words or not answer_words:
            return 0.0

        overlap = len(question_words & answer_words)
        return min(overlap / min(len(question_words), len(answer_words)), 1.0)

    def has_specific_details(self, text: str) -> bool:
        """Check if text contains specific details like numbers, dates, etc."""
        for pattern in self.specific_details:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def is_bangladeshi_focused(self, text: str) -> bool:
        """Check if content is focused on Bangladeshi students."""
        if not text:
            return False
            
        text = str(text) if text is not None else ""
        if not text:
            return False
            
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.bangladeshi_keywords)

    def validate_grade_accuracy(self, text: str) -> float:
        """Validate accuracy of grade information using Bangladeshi system."""
        if not self.grading_validation_available:
            return self._basic_grade_validation(text)

        grade_accuracy = 1.0

        # Check for grade patterns and validate them
        grade_patterns = [
            (r"ssc\s+(?:gpa\s+)?(\d+\.?\d*)", 5.0, "SSC"),
            (r"hsc\s+(?:gpa\s+)?(\d+\.?\d*)", 5.0, "HSC"),
            (r"diploma\s+(?:cgpa\s+)?(\d+\.?\d*)", 4.0, "Diploma"),
            (r"bachelor\s+(?:cgpa\s+)?(\d+\.?\d*)", 4.0, "Bachelor"),
            (r"honours\s+(?:cgpa\s+)?(\d+\.?\d*)", 4.0, "Honours"),
        ]

        for pattern, max_scale, qual_name in grade_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                try:
                    grade_value = float(match.group(1))

                    # Validate grade range based on qualification
                    if grade_value > max_scale:
                        grade_accuracy -= 0.4  # Heavy penalty for impossible grades
                    elif grade_value == 0:
                        grade_accuracy -= 0.2  # Penalty for zero grades

                except ValueError:
                    grade_accuracy -= 0.1  # Minor penalty for parsing errors

        return max(0.0, grade_accuracy)

    def _basic_grade_validation(self, text: str) -> float:
        """Basic grade validation when grading system unavailable."""
        # Check for unrealistic grades
        unrealistic_patterns = [
            r"ssc\s+(?:gpa\s+)?([6-9]\.\d+)",  # SSC GPA > 5
            r"hsc\s+(?:gpa\s+)?([6-9]\.\d+)",  # HSC GPA > 5
            r"cgpa\s+([5-9]\.\d+)",  # CGPA > 4
            r"(\d{3,})%",  # Percentage > 100
        ]

        penalty = 0.0
        for pattern in unrealistic_patterns:
            if re.search(pattern, text.lower()):
                penalty += 0.3

        return max(0.0, 1.0 - penalty)

    def assess_cultural_authenticity(self, question: str, answer: str) -> float:
        """Assess cultural authenticity for Bangladeshi context."""
        combined_text = (question + " " + answer).lower()
        authenticity_score = 0.5  # Base score

        # Positive indicators
        bangladeshi_indicators = [
            "bangladeshi students",
            "from bangladesh",
            "ssc",
            "hsc",
            "dhaka",
            "chittagong",
            "sylhet",
            "embassy of india",
            "taka",
            "bdt",
            "honours degree",
            "diploma",
        ]

        for indicator in bangladeshi_indicators:
            if indicator in combined_text:
                authenticity_score += 0.1

        # Check for appropriate grade system references
        if "gpa" in combined_text and (
            "ssc" in combined_text or "hsc" in combined_text
        ):
            authenticity_score += 0.15  # Correct GPA usage for SSC/HSC

        if "cgpa" in combined_text and (
            "diploma" in combined_text or "bachelor" in combined_text
        ):
            authenticity_score += 0.15  # Correct CGPA usage for higher education

        # Negative indicators (reduce authenticity)
        non_bangladeshi_indicators = [
            "american students",
            "british students",
            "sat scores",
            "ap courses",
            "gcse",
            "a-levels",
            "us dollars",
        ]

        for indicator in non_bangladeshi_indicators:
            if indicator in combined_text:
                authenticity_score -= 0.2

        return min(1.0, max(0.0, authenticity_score))

    def _calculate_linguistic_quality(self, text: str) -> float:
        """Calculate linguistic quality score"""
        if not text:
            return 0.0
        
        # Simple linguistic quality assessment
        # Check for proper sentence structure, punctuation, etc.
        sentences = text.split('.')
        if len(sentences) < 2:
            return 0.5
        
        # Check for proper capitalization
        proper_caps = sum(1 for s in sentences if s.strip() and s.strip()[0].isupper())
        cap_score = proper_caps / len(sentences) if sentences else 0.0
        
        # Check for reasonable sentence length
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        length_score = min(1.0, avg_sentence_length / 20.0)  # Normalize to 20 words
        
        return (cap_score + length_score) / 2.0
    
    def _calculate_content_specificity(self, answer: str, context: str) -> float:
        """Calculate content specificity score"""
        if not answer or not context:
            return 0.0
        
        # Count specific terms (numbers, proper nouns, etc.)
        specific_terms = []
        words = answer.split()
        
        for word in words:
            # Check for numbers, currency, percentages
            if any(char.isdigit() for char in word):
                specific_terms.append(word)
            # Check for proper nouns (capitalized)
            elif word and word[0].isupper() and len(word) > 2:
                specific_terms.append(word)
            # Check for currency symbols
            elif any(symbol in word for symbol in ['₹', '$', '€', '£']):
                specific_terms.append(word)
        
        # Calculate specificity as ratio of specific terms to total words
        specificity = len(specific_terms) / len(words) if words else 0.0
        
        return min(1.0, specificity * 5.0)  # Scale up for better scoring

    def evaluate_qa_pair(self, qa_pair: Dict[str, Any]) -> QualityMetrics:
        """Evaluate quality metrics for a Q&A pair"""
        
        # Extract components with None checks
        question = qa_pair.get("question", "") or ""
        answer = qa_pair.get("answer", "") or ""
        context = qa_pair.get("context", "") or ""
        
        # Ensure all are strings
        question = str(question) if question is not None else ""
        answer = str(answer) if answer is not None else ""
        context = str(context) if context is not None else ""
        
        # Calculate individual metrics
        extractive_score = self.calculate_extractive_score(answer, context)
        relevance_score = self.calculate_relevance_score(question, answer)
        answer_length = len(answer)
        has_specific_details = self.has_specific_details(answer)
        is_bangladeshi = self.is_bangladeshi_focused(question + " " + answer)
        linguistic_quality = self._calculate_linguistic_quality(answer)
        content_specificity = self._calculate_content_specificity(answer, context)
        grade_accuracy = self.validate_grade_accuracy(answer)
        cultural_authenticity = self.assess_cultural_authenticity(question, answer)
        
        # Calculate overall score
        overall_score = (
            extractive_score * 0.25 +
            relevance_score * 0.20 +
            (1.0 if has_specific_details else 0.5) * 0.15 +
            (1.0 if is_bangladeshi else 0.3) * 0.10 +
            linguistic_quality * 0.10 +
            content_specificity * 0.10 +
            grade_accuracy * 0.05 +
            cultural_authenticity * 0.05
        )
        
        return QualityMetrics(
            extractive_score=extractive_score,
            relevance_score=relevance_score,
            answer_length=answer_length,
            has_specific_details=has_specific_details,
            bangladeshi_focus=is_bangladeshi,
            linguistic_quality=linguistic_quality,
            content_specificity=content_specificity,
            overall_score=overall_score,
            grade_accuracy=grade_accuracy,
            cultural_authenticity=cultural_authenticity
        )

    def analyze_dataset(self, dataset_path: Path) -> Dict[str, Any]:
        """Analyze complete dataset and return quality report."""
        logger.info(f"Analyzing dataset: {dataset_path}")

        # Load dataset
        qa_pairs = []
        with open(dataset_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    qa_pairs.append(json.loads(line))

        logger.info(f"Loaded {len(qa_pairs)} Q&A pairs")

        # Evaluate each pair
        metrics = []
        for qa_pair in qa_pairs:
            metric = self.evaluate_qa_pair(qa_pair)
            metrics.append(metric)

        # Calculate aggregate statistics
        # Calculate averages including new metrics
        avg_extractive = sum(m.extractive_score for m in metrics) / len(metrics)
        avg_relevance = sum(m.relevance_score for m in metrics) / len(metrics)
        avg_overall = sum(m.overall_score for m in metrics) / len(metrics)
        avg_length = sum(m.answer_length for m in metrics) / len(metrics)
        avg_grade_accuracy = sum(m.grade_accuracy for m in metrics) / len(metrics)
        avg_cultural_authenticity = sum(m.cultural_authenticity for m in metrics) / len(
            metrics
        )

        with_details = sum(1 for m in metrics if m.has_specific_details)
        bangladeshi_focused = sum(1 for m in metrics if m.bangladeshi_focus)

        high_quality = sum(1 for m in metrics if m.overall_score >= 0.7)
        medium_quality = sum(1 for m in metrics if 0.5 <= m.overall_score < 0.7)
        low_quality = sum(1 for m in metrics if m.overall_score < 0.5)

        return {
            "total_pairs": len(qa_pairs),
            "average_scores": {
                "extractive": round(avg_extractive, 3),
                "relevance": round(avg_relevance, 3),
                "grade_accuracy": round(avg_grade_accuracy, 3),
                "cultural_authenticity": round(avg_cultural_authenticity, 3),
                "overall": round(avg_overall, 3),
            },
            "content_analysis": {
                "avg_answer_length": round(avg_length, 1),
                "with_specific_details": with_details,
                "bangladeshi_focused": bangladeshi_focused,
                "details_percentage": round(with_details / len(metrics) * 100, 1),
                "bangladeshi_percentage": round(
                    bangladeshi_focused / len(metrics) * 100, 1
                ),
            },
            "quality_distribution": {
                "high_quality": high_quality,
                "medium_quality": medium_quality,
                "low_quality": low_quality,
                "high_percentage": round(high_quality / len(metrics) * 100, 1),
                "medium_percentage": round(medium_quality / len(metrics) * 100, 1),
                "low_percentage": round(low_quality / len(metrics) * 100, 1),
            },
            "bangladeshi_grading_analysis": {
                "grade_accuracy_avg": round(avg_grade_accuracy, 3),
                "cultural_authenticity_avg": round(avg_cultural_authenticity, 3),
                "accurate_grades": sum(1 for m in metrics if m.grade_accuracy >= 0.8),
                "culturally_authentic": sum(
                    1 for m in metrics if m.cultural_authenticity >= 0.7
                ),
            },
        }
