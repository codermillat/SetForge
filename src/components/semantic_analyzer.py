#!/usr/bin/env python3
"""
SetForge - Advanced Semantic Analyzer
====================================

Advanced semantic analysis for deep context understanding and quality assessment.
Provides semantic similarity, context grounding, and cultural relevance analysis.
"""

import re
import math
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import Counter
import logging

logger = logging.getLogger("SetForge")

# Try to import SentenceTransformer, but make it optional
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMER_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMER_AVAILABLE = False
    logger.warning("SentenceTransformer not available. Semantic analysis will use basic methods.")


@dataclass
class SemanticMetrics:
    """Comprehensive semantic analysis metrics."""

    context_similarity: float = 0.0
    semantic_overlap: float = 0.0
    cultural_relevance: float = 0.0
    topic_alignment: float = 0.0
    contextual_coherence: float = 0.0
    overall_semantic_score: float = 0.0


class SemanticAnalyzer:
    """
    Advanced semantic analyzer for deep context understanding.

    Provides semantic similarity analysis, context grounding assessment,
    and cultural relevance evaluation for Q&A pairs.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the semantic analyzer with necessary components."""
        self.config = config or {}
        
        self.stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by",
            "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
            "will", "would", "could", "should", "may", "might", "can", "this", "that", "these", "those",
        }
        
        # Initialize sentence transformer model for semantic similarity
        if SENTENCE_TRANSFORMER_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.model_available = True
            except Exception as e:
                print(f"Warning: SentenceTransformer not available: {e}")
                self.model_available = False
        else:
            self.model_available = False

        # Semantic analysis weights
        self.weights = {
            "context_similarity": 0.30,
            "semantic_overlap": 0.25,
            "cultural_relevance": 0.20,
            "topic_alignment": 0.15,
            "contextual_coherence": 0.10,
        }

        # Update weights from config if provided
        if "semantic_weights" in self.config:
            self.weights.update(self.config["semantic_weights"])

        # Bangladeshi cultural indicators for semantic analysis
        self.bangladeshi_cultural_indicators = [
            "bangladeshi students",
            "bangladesh",
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
            "bangladeshi",
            "bengali",
            "বাংলাদেশ",
            "বাংলা",
            "এসএসসি",
            "এইচএসসি",
            "ডিপ্লোমা",
            "সিজিপিএ",
        ]

        # Indian educational indicators
        self.indian_educational_indicators = [
            "india",
            "indian",
            "university",
            "college",
            "b.tech",
            "bsc",
            "bba",
            "mba",
            "admission",
            "scholarship",
            "visa",
            "accommodation",
            "rupee",
            "₹",
            "ncr",
            "delhi",
            "noida",
            "greater noida",
        ]

        # Topic keywords for alignment analysis
        self.topic_keywords = {
            "scholarship": [
                "scholarship",
                "financial aid",
                "merit",
                "discount",
                "free",
                "waiver",
            ],
            "fees": [
                "cost",
                "fee",
                "price",
                "rupee",
                "₹",
                "taka",
                "budget",
                "expensive",
            ],
            "admission": [
                "admission",
                "apply",
                "requirement",
                "document",
                "process",
                "eligible",
            ],
            "visa_guidance": [
                "visa",
                "embassy",
                "documentation",
                "permit",
                "immigration",
            ],
            "accommodation": [
                "hostel",
                "accommodation",
                "housing",
                "room",
                "stay",
                "live",
            ],
            "university_comparison": [
                "compare",
                "difference",
                "better",
                "versus",
                "vs",
                "which",
            ],
            "degree_equivalency": [
                "degree",
                "equivalency",
                "recognition",
                "valid",
                "bsc",
                "b.tech",
            ],
        }

    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts using word overlap and TF-IDF.

        Args:
            text1: First text for comparison
            text2: Second text for comparison

        Returns:
            float: Semantic similarity score (0.0-1.0)
        """
        # Tokenize and normalize texts
        words1 = self._tokenize_and_normalize(text1)
        words2 = self._tokenize_and_normalize(text2)

        if not words1 or not words2:
            return 0.0

        # Calculate word overlap
        common_words = set(words1) & set(words2)
        total_unique_words = len(set(words1) | set(words2))

        if total_unique_words == 0:
            return 0.0

        # Jaccard similarity
        jaccard_similarity = len(common_words) / total_unique_words

        # TF-IDF weighted similarity
        tfidf_similarity = self._calculate_tfidf_similarity(words1, words2)

        # Combine similarities
        semantic_similarity = (jaccard_similarity * 0.4) + (tfidf_similarity * 0.6)

        return min(semantic_similarity, 1.0)

    def _tokenize_and_normalize(self, text: str) -> List[str]:
        """Tokenize and normalize text for semantic analysis."""
        if not text or not isinstance(text, str):
            return []
            
        # Remove special characters and convert to lowercase
        text = re.sub(r"[^\w\s]", " ", text.lower())
        
        # Tokenize and filter out stop words
        tokens = text.split()
        tokens = [token for token in tokens if token not in self.stop_words and len(token) > 2]
        
        return tokens

    def _calculate_tfidf_similarity(
        self, words1: List[str], words2: List[str]
    ) -> float:
        """Calculate TF-IDF weighted similarity between word lists."""
        # Calculate term frequencies
        tf1 = Counter(words1)
        tf2 = Counter(words2)

        # Calculate document frequencies
        all_words = set(words1) | set(words2)

        # Simple TF-IDF calculation
        similarity_score = 0.0
        total_weight = 0.0

        for word in all_words:
            tf1_val = tf1.get(word, 0) / len(words1) if words1 else 0
            tf2_val = tf2.get(word, 0) / len(words2) if words2 else 0

            # IDF calculation (simplified)
            df = 1 if word in words1 else 0
            df += 1 if word in words2 else 0
            idf = math.log(2 / df) if df > 0 else 0

            # TF-IDF values
            tfidf1 = tf1_val * idf
            tfidf2 = tf2_val * idf

            # Cosine similarity component
            similarity_score += tfidf1 * tfidf2
            total_weight += (tfidf1**2) * (tfidf2**2)

        if total_weight == 0:
            return 0.0

        return similarity_score / math.sqrt(total_weight)

    def calculate_context_grounding(self, answer: str, context: str) -> float:
        """
        Calculate how well an answer is grounded in the provided context.

        Args:
            answer: Generated answer text
            context: Source context text

        Returns:
            float: Context grounding score (0.0-1.0)
        """
        # Calculate semantic similarity
        semantic_sim = self.calculate_semantic_similarity(answer, context)

        # Extract key entities from context
        context_entities = self.extract_key_entities(context)
        answer_entities = self.extract_key_entities(answer)

        # Calculate entity overlap
        entity_overlap = 0.0
        if context_entities:
            common_entities = context_entities & answer_entities
            entity_overlap = len(common_entities) / len(context_entities)

        # Calculate factual consistency
        factual_consistency = self._calculate_factual_consistency(answer, context)

        # Combine scores
        context_grounding = (
            semantic_sim * 0.4 + entity_overlap * 0.3 + factual_consistency * 0.3
        )

        return min(context_grounding, 1.0)

    def extract_key_entities(self, text: str) -> set[str]:
        """Extract key entities (universities, programs, numbers, etc.) from text."""
        entities = set()

        # Extract university names
        universities = [
            "sharda university",
            "amity university",
            "galgotias university",
            "noida international university",
            "g.l. bajaj institute",
        ]
        for uni in universities:
            if uni in text.lower():
                entities.add(uni)

        # Extract program names
        programs = ["b.tech", "bsc", "bba", "b.com", "mba", "m.tech", "diploma"]
        for program in programs:
            if program in text.lower():
                entities.add(program)

        # Extract numbers (fees, grades, etc.)
        numbers = re.findall(r"\d+(?:\.\d+)?", text)
        entities.update(numbers)

        # Extract currency symbols
        currencies = re.findall(r"[₹$৳]", text)
        entities.update(currencies)

        return entities

    def _calculate_factual_consistency(self, answer: str, context: str) -> float:
        """Calculate factual consistency between answer and context."""
        # Extract factual statements (numbers, dates, specific details)
        context_facts = self._extract_facts(context)
        answer_facts = self._extract_facts(answer)

        if not context_facts:
            return 1.0  # No facts to check against

        # Calculate fact consistency
        consistent_facts = 0
        for fact in answer_facts:
            if fact in context_facts:
                consistent_facts += 1

        return consistent_facts / len(answer_facts) if answer_facts else 1.0

    def _extract_facts(self, text: str) -> set[str]:
        """Extract factual information from text."""
        facts = set()

        # Extract numbers with context
        number_patterns = [
            r"\d+(?:\.\d+)?\s*(?:lakh|lac|thousand|k|rupee|₹|taka|৳)",
            r"(?:fee|cost|price|tuition)\s*[:\-]?\s*[₹$৳]?\s*\d+(?:\.\d+)?",
            r"(?:cgpa|gpa|grade)\s*[:\-]?\s*\d+(?:\.\d+)?",
            r"\d{4}(?:-\d{2})?",  # Years and dates
        ]

        for pattern in number_patterns:
            matches = re.findall(pattern, text.lower())
            facts.update(matches)

        return facts

    def calculate_cultural_relevance(self, text: str) -> float:
        """
        Calculate cultural relevance for Bangladeshi students.

        Args:
            text: Text to analyze for cultural relevance

        Returns:
            float: Cultural relevance score (0.0-1.0)
        """
        text_lower = text.lower()

        # Count Bangladeshi cultural indicators
        bangladeshi_count = sum(
            1
            for indicator in self.bangladeshi_cultural_indicators
            if indicator in text_lower
        )

        # Count Indian educational indicators
        indian_count = sum(
            1
            for indicator in self.indian_educational_indicators
            if indicator in text_lower
        )

        # Calculate relevance scores
        bangladeshi_relevance = min(bangladeshi_count / 5, 1.0)  # Normalize to 0-1
        indian_relevance = min(indian_count / 5, 1.0)  # Normalize to 0-1

        # Combined cultural relevance
        cultural_relevance = (bangladeshi_relevance * 0.6) + (indian_relevance * 0.4)

        return min(cultural_relevance, 1.0)

    def calculate_topic_alignment(
        self, question: str, answer: str, question_type: str
    ) -> float:
        """
        Calculate how well the answer aligns with the question topic.

        Args:
            question: Generated question
            answer: Generated answer
            question_type: Type of question (scholarship, fees, etc.)

        Returns:
            float: Topic alignment score (0.0-1.0)
        """
        if question_type not in self.topic_keywords:
            return 0.5  # Default score for unknown types

        # Get topic keywords
        topic_keywords = self.topic_keywords[question_type]

        # Count topic keywords in question and answer
        question_lower = question.lower()
        answer_lower = answer.lower()

        question_topic_count = sum(
            1 for keyword in topic_keywords if keyword in question_lower
        )

        answer_topic_count = sum(
            1 for keyword in topic_keywords if keyword in answer_lower
        )

        # Calculate alignment scores
        question_alignment = min(question_topic_count / 3, 1.0)
        answer_alignment = min(answer_topic_count / 3, 1.0)

        # Combined topic alignment
        topic_alignment = (question_alignment * 0.4) + (answer_alignment * 0.6)

        return min(topic_alignment, 1.0)

    def calculate_contextual_coherence(self, text: str) -> float:
        """
        Calculate contextual coherence of the text.

        Args:
            text: Text to analyze for coherence

        Returns:
            float: Contextual coherence score (0.0-1.0)
        """
        # Simple coherence metrics
        sentences = text.split(".")
        if len(sentences) < 2:
            return 0.5

        # Calculate average sentence length (reasonable range: 10-50 words)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        length_coherence = (
            1.0 - abs(avg_sentence_length - 25) / 25
        )  # Optimal around 25 words

        # Check for logical connectors
        connectors = [
            "because",
            "therefore",
            "however",
            "although",
            "furthermore",
            "additionally",
        ]
        connector_count = sum(
            1 for connector in connectors if connector in text.lower()
        )
        connector_coherence = min(connector_count / 3, 1.0)

        # Check for repetition (penalty for excessive repetition)
        words = text.lower().split()
        word_counts = Counter(words)
        max_repetition = max(word_counts.values()) if word_counts else 0
        repetition_penalty = max(
            0, (max_repetition - 5) / 10
        )  # Penalty for >5 repetitions

        # Combined coherence score
        coherence = (
            length_coherence * 0.4
            + connector_coherence * 0.4
            + (1.0 - repetition_penalty) * 0.2
        )

        return max(0.0, min(coherence, 1.0))

    def analyze_semantics(
        self, answer: str, context: str, question: str, question_type: str = ""
    ) -> SemanticMetrics:
        """
        Perform comprehensive semantic analysis.

        Args:
            answer: Generated answer
            context: Source context
            question: Generated question
            question_type: Type of question

        Returns:
            SemanticMetrics: Comprehensive semantic analysis results
        """
        # Calculate individual metrics
        context_similarity = self.calculate_semantic_similarity(answer, context)
        semantic_overlap = self.calculate_context_grounding(answer, context)
        cultural_relevance = self.calculate_cultural_relevance(answer)
        topic_alignment = self.calculate_topic_alignment(
            question, answer, question_type
        )
        contextual_coherence = self.calculate_contextual_coherence(answer)

        # Calculate weighted overall score
        overall_semantic_score = (
            context_similarity * self.weights["context_similarity"]
            + semantic_overlap * self.weights["semantic_overlap"]
            + cultural_relevance * self.weights["cultural_relevance"]
            + topic_alignment * self.weights["topic_alignment"]
            + contextual_coherence * self.weights["contextual_coherence"]
        )

        return SemanticMetrics(
            context_similarity=context_similarity,
            semantic_overlap=semantic_overlap,
            cultural_relevance=cultural_relevance,
            topic_alignment=topic_alignment,
            contextual_coherence=contextual_coherence,
            overall_semantic_score=overall_semantic_score,
        )

    def is_semantically_acceptable(
        self, metrics: SemanticMetrics, thresholds: Dict[str, float] = None
    ) -> bool:
        """
        Check if semantic metrics meet minimum thresholds.

        Args:
            metrics: SemanticMetrics object
            thresholds: Custom thresholds (optional)

        Returns:
            bool: True if semantically acceptable
        """
        default_thresholds = {
            "context_similarity": 0.3,
            "semantic_overlap": 0.4,
            "cultural_relevance": 0.2,
            "topic_alignment": 0.3,
            "contextual_coherence": 0.4,
            "overall_semantic_score": 0.5,
        }

        thresholds = thresholds or default_thresholds

        return (
            metrics.context_similarity >= thresholds["context_similarity"]
            and metrics.semantic_overlap >= thresholds["semantic_overlap"]
            and metrics.cultural_relevance >= thresholds["cultural_relevance"]
            and metrics.topic_alignment >= thresholds["topic_alignment"]
            and metrics.contextual_coherence >= thresholds["contextual_coherence"]
            and metrics.overall_semantic_score >= thresholds["overall_semantic_score"]
        )
