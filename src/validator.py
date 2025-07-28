"""
Production-grade QA Pair validation with comprehensive quality assurance.
"""

import logging
import re
import time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from collections import Counter

try:
    from sentence_transformers import SentenceTransformer
    import torch
    SEMANTIC_VALIDATION_AVAILABLE = True
except ImportError:
    SEMANTIC_VALIDATION_AVAILABLE = False


@dataclass
class ValidationResult:
    """Enhanced validation results with detailed diagnostics."""
    is_valid: bool
    overall_score: float
    scores: Dict[str, float]
    issues: List[str]
    recommendations: List[str] = field(default_factory=list)
    confidence_level: str = "medium"  # low, medium, high
    processing_time: float = 0.0
    validator_version: str = "2.0"

import logging
import re
import string
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import asyncio

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logging.warning("sentence-transformers not available, semantic validation disabled")

from config import Config
from qa_generator import QAPair


@dataclass
class ValidationResult:
    """Results from QA pair validation."""
    is_valid: bool
    relevancy_score: float
    extractive_score: float
    hallucination_score: float
    overall_score: float
    validation_details: Dict
    issues: List[str]


class QAValidator:
    """Multi-stage QA validation pipeline."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize embedding model if available
        self.embedding_model = None
        if EMBEDDINGS_AVAILABLE and self.config.validation.enable_semantic_validation:
            try:
                self.embedding_model = SentenceTransformer(
                    self.config.validation.embedding_model
                )
                self.logger.info(f"Loaded embedding model: {self.config.validation.embedding_model}")
            except Exception as e:
                self.logger.warning(f"Failed to load embedding model: {e}")
                self.embedding_model = None
        
        # Compile regex patterns for efficiency
        self._hallucination_patterns = [
            re.compile(r'\b(probably|likely|possibly|might|could|may|perhaps)\b', re.IGNORECASE),
            re.compile(r'\b(in general|typically|usually|often|sometimes)\b', re.IGNORECASE),
            re.compile(r'\b(i think|i believe|in my opinion|it seems)\b', re.IGNORECASE),
            re.compile(r'\b(according to|based on|suggests that)\b', re.IGNORECASE),
        ]
        
        self._extractive_indicators = [
            re.compile(r'^(yes|no)\b', re.IGNORECASE),
            re.compile(r'^\d+(\.\d+)?$'),  # Pure numbers
            re.compile(r'^[A-Z][a-z]+ \d+, \d{4}$'),  # Dates
        ]
    
    async def validate_qa_pair(self, qa_pair: QAPair) -> ValidationResult:
        """
        Comprehensive validation of a QA pair.
        
        Args:
            qa_pair: QAPair to validate
            
        Returns:
            ValidationResult with detailed validation metrics
        """
        self.logger.debug(f"Validating QA pair from chunk: {qa_pair.chunk_id}")
        
        validation_details = {}
        issues = []
        
        # 1. Extractive validation (required)
        extractive_score, extractive_details = self._validate_extractive(qa_pair)
        validation_details['extractive'] = extractive_details
        
        if extractive_score < self.config.validation.min_source_overlap:
            issues.append(f"Low extractive score: {extractive_score:.2f}")
        
        # 2. Hallucination detection (required)
        hallucination_score, hallucination_details = self._detect_hallucinations(qa_pair)
        validation_details['hallucination'] = hallucination_details
        
        if hallucination_score > self.config.validation.max_inference_ratio:
            issues.append(f"High hallucination risk: {hallucination_score:.2f}")
        
        # 3. Semantic validation (optional, if embeddings available)
        relevancy_score = 0.8  # Default fallback
        if (self.embedding_model and 
            self.config.validation.enable_semantic_validation):
            relevancy_score, semantic_details = await self._validate_semantic_relevancy(qa_pair)
            validation_details['semantic'] = semantic_details
            
            if relevancy_score < self.config.validation.min_relevancy_score:
                issues.append(f"Low relevancy score: {relevancy_score:.2f}")
        else:
            validation_details['semantic'] = {'method': 'skipped', 'reason': 'embeddings not available'}
        
        # 4. Content quality checks
        quality_score, quality_details = self._validate_content_quality(qa_pair)
        validation_details['quality'] = quality_details
        
        if quality_score < 0.6:  # Lowered from 0.7
            issues.append(f"Low content quality: {quality_score:.2f}")
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            extractive_score, 
            1.0 - hallucination_score,  # Invert hallucination score
            relevancy_score, 
            quality_score
        )
        
        # Determine if valid
        is_valid = (
            extractive_score >= self.config.validation.min_source_overlap and
            hallucination_score <= self.config.validation.max_inference_ratio and
            relevancy_score >= self.config.validation.min_relevancy_score and
            quality_score >= 0.6  # Lowered from 0.7
        )
        
        result = ValidationResult(
            is_valid=is_valid,
            relevancy_score=relevancy_score,
            extractive_score=extractive_score,
            hallucination_score=hallucination_score,
            overall_score=overall_score,
            validation_details=validation_details,
            issues=issues
        )
        
        self.logger.debug(f"Validation result for {qa_pair.chunk_id}: {overall_score:.2f} ({'PASS' if is_valid else 'FAIL'})")
        
        return result
    
    def _validate_extractive(self, qa_pair: QAPair) -> Tuple[float, Dict]:
        """Validate that the answer is extractive from the source text."""
        source_text = qa_pair.source_text.lower()
        answer_text = qa_pair.answer.lower()
        
        # Normalize texts
        source_normalized = self._normalize_text(source_text)
        answer_normalized = self._normalize_text(answer_text)
        
        # Method 1: Direct substring match
        direct_match = answer_normalized in source_normalized
        
        # Method 2: Word overlap analysis
        source_words = set(source_normalized.split())
        answer_words = set(answer_normalized.split())
        
        if not answer_words:
            return 0.0, {'method': 'word_overlap', 'error': 'empty_answer'}
        
        word_overlap = len(answer_words.intersection(source_words)) / len(answer_words)
        
        # Method 3: Sentence-level extraction check
        source_sentences = [s.strip() for s in re.split(r'[.!?]+', source_text) if s.strip()]
        sentence_overlap = 0.0
        
        for sentence in source_sentences:
            sentence_norm = self._normalize_text(sentence.lower())
            if sentence_norm and answer_normalized in sentence_norm:
                sentence_overlap = 1.0
                break
            
            # Check partial sentence overlap
            sentence_words = set(sentence_norm.split())
            if sentence_words and answer_words:
                overlap_ratio = len(answer_words.intersection(sentence_words)) / len(answer_words)
                sentence_overlap = max(sentence_overlap, overlap_ratio)
        
        # Calculate final extractive score
        extractive_score = max(word_overlap, sentence_overlap)
        if direct_match:
            extractive_score = max(extractive_score, 0.95)
        
        details = {
            'method': 'multi_method',
            'direct_match': direct_match,
            'word_overlap': word_overlap,
            'sentence_overlap': sentence_overlap,
            'final_score': extractive_score,
            'answer_words': len(answer_words),
            'source_words': len(source_words)
        }
        
        return extractive_score, details
    
    def _detect_hallucinations(self, qa_pair: QAPair) -> Tuple[float, Dict]:
        """Detect potential hallucinations in the answer."""
        answer_text = qa_pair.answer.lower()
        
        # Check for hallucination patterns
        hallucination_indicators = 0
        total_patterns = len(self._hallucination_patterns)
        matched_patterns = []
        
        for pattern in self._hallucination_patterns:
            if pattern.search(answer_text):
                hallucination_indicators += 1
                matched_patterns.append(pattern.pattern)
        
        # Check for non-extractive language
        inference_words = [
            'therefore', 'thus', 'consequently', 'implies', 'suggests',
            'indicates', 'appears', 'seems', 'likely', 'probably'
        ]
        
        inference_count = sum(1 for word in inference_words if word in answer_text)
        
        # Check for creative additions
        creative_indicators = [
            'furthermore', 'additionally', 'moreover', 'in conclusion',
            'overall', 'in summary', 'it is important', 'should be noted'
        ]
        
        creative_count = sum(1 for phrase in creative_indicators if phrase in answer_text)
        
        # Calculate hallucination score
        pattern_score = hallucination_indicators / max(total_patterns, 1)
        inference_score = min(inference_count / 10, 1.0)  # Normalize to 0-1
        creative_score = min(creative_count / 5, 1.0)  # Normalize to 0-1
        
        hallucination_score = (pattern_score + inference_score + creative_score) / 3
        
        details = {
            'method': 'pattern_analysis',
            'pattern_matches': matched_patterns,
            'inference_words': inference_count,
            'creative_indicators': creative_count,
            'pattern_score': pattern_score,
            'inference_score': inference_score,
            'creative_score': creative_score,
            'final_score': hallucination_score
        }
        
        return hallucination_score, details
    
    async def _validate_semantic_relevancy(self, qa_pair: QAPair) -> Tuple[float, Dict]:
        """Validate semantic relevancy using embeddings."""
        if not self.embedding_model:
            return 0.8, {'method': 'skipped', 'reason': 'no_embedding_model'}
        
        try:
            # Generate embeddings
            question_embedding = self.embedding_model.encode([qa_pair.question])
            answer_embedding = self.embedding_model.encode([qa_pair.answer])
            source_embedding = self.embedding_model.encode([qa_pair.source_text])
            
            # Calculate similarities
            qa_similarity = self._cosine_similarity(question_embedding[0], answer_embedding[0])
            answer_source_similarity = self._cosine_similarity(answer_embedding[0], source_embedding[0])
            question_source_similarity = self._cosine_similarity(question_embedding[0], source_embedding[0])
            
            # Weight the similarities
            # Answer-source similarity is most important for extractive validation
            relevancy_score = (
                answer_source_similarity * 0.6 +
                qa_similarity * 0.3 +
                question_source_similarity * 0.1
            )
            
            details = {
                'method': 'embedding_similarity',
                'qa_similarity': float(qa_similarity),
                'answer_source_similarity': float(answer_source_similarity),
                'question_source_similarity': float(question_source_similarity),
                'weighted_score': float(relevancy_score),
                'embedding_model': self.config.validation.embedding_model
            }
            
            return relevancy_score, details
            
        except Exception as e:
            self.logger.error(f"Semantic validation failed: {e}")
            return 0.5, {'method': 'failed', 'error': str(e)}
    
    def _validate_content_quality(self, qa_pair: QAPair) -> Tuple[float, Dict]:
        """Validate overall content quality."""
        quality_metrics = {}
        
        # Question quality
        question = qa_pair.question.strip()
        
        # Check if question is well-formed
        has_question_mark = question.endswith('?')
        starts_with_question_word = any(question.lower().startswith(word) for word in 
                                      ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'is', 'are', 'do', 'does', 'can', 'will'])
        
        question_quality = 0.0
        if has_question_mark:
            question_quality += 0.5
        if starts_with_question_word:
            question_quality += 0.5
        
        quality_metrics['question_quality'] = question_quality
        
        # Answer quality
        answer = qa_pair.answer.strip()
        
        # Check answer completeness
        answer_complete = len(answer) >= self.config.qa.min_answer_length and not answer.endswith('...')
        answer_punctuation = answer.endswith('.') or answer.endswith('!') or answer.endswith('?')
        
        answer_quality = 0.0
        if answer_complete:
            answer_quality += 0.6
        if answer_punctuation:
            answer_quality += 0.4
        
        quality_metrics['answer_quality'] = answer_quality
        
        # Specificity check
        generic_answers = ['yes', 'no', 'it depends', 'varies', 'multiple', 'several', 'many']
        is_specific = answer.lower() not in generic_answers and len(answer.split()) > 2
        specificity_score = 1.0 if is_specific else 0.3
        
        quality_metrics['specificity'] = specificity_score
        
        # Calculate overall quality
        overall_quality = (
            question_quality * 0.3 +
            answer_quality * 0.5 +
            specificity_score * 0.2
        )
        
        details = {
            'method': 'content_analysis',
            'metrics': quality_metrics,
            'final_score': overall_quality
        }
        
        return overall_quality, details
    
    def _calculate_overall_score(self, extractive: float, non_hallucination: float, 
                               relevancy: float, quality: float) -> float:
        """Calculate weighted overall score."""
        return (
            extractive * 0.4 +          # Most important: must be extractive
            non_hallucination * 0.3 +   # Critical: no hallucinations
            relevancy * 0.2 +           # Important: semantic relevancy
            quality * 0.1               # Nice to have: content quality
        )
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        # Remove punctuation and extra whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _cosine_similarity(self, a, b):
        """Calculate cosine similarity between two vectors."""
        if EMBEDDINGS_AVAILABLE:
            import numpy as np
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        return 0.5  # Fallback
    
    async def validate_batch(self, qa_pairs: List[QAPair]) -> List[ValidationResult]:
        """Validate a batch of QA pairs efficiently."""
        tasks = [self.validate_qa_pair(qa_pair) for qa_pair in qa_pairs]
        return await asyncio.gather(*tasks)
