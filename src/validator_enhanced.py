"""
Production-grade QA Pair validation with comprehensive quality assurance.
"""

import logging
import re
import time
from typing import Dict, List, Optional, Any, Set, Tuple
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


class ProductionQAValidator:
    """Production-grade QA pair validator with comprehensive quality checks."""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._semantic_model = None
        self._validation_cache = {}
        self._quality_patterns = self._load_quality_patterns()
        self._question_types = self._load_question_types()
        
        # Statistics tracking
        self.validation_stats = {
            'total_validations': 0,
            'passed_validations': 0,
            'failed_by_reason': Counter(),
            'avg_processing_time': 0.0,
            'cache_hits': 0
        }
        
        if SEMANTIC_VALIDATION_AVAILABLE and getattr(self.config.validation, 'enable_semantic', False):
            try:
                self._load_semantic_model()
            except Exception as e:
                self.logger.warning(f"Failed to load semantic model: {e}")
                self.config.validation.enable_semantic = False
    
    def _load_quality_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for quality assessment."""
        return {
            'good_questions': [
                r'\bwhat\s+is\b',
                r'\bhow\s+does\b',
                r'\bwhy\s+is\b',
                r'\bwhen\s+did\b',
                r'\bwhere\s+is\b',
                r'\bwhich\s+of\b',
                r'\bwho\s+was\b'
            ],
            'poor_questions': [
                r'\bis\s+it\s+true\b',
                r'\byes\s+or\s+no\b',
                r'\bdo\s+you\s+think\b',
                r'\bin\s+your\s+opinion\b'
            ],
            'quality_indicators': [
                r'\bspecifically\b',
                r'\baccording\s+to\b',
                r'\bas\s+stated\b',
                r'\bthe\s+text\s+mentions\b',
                r'\bas\s+described\b'
            ],
            'hallucination_indicators': [
                r'\bmight\s+be\b',
                r'\bprobably\b',
                r'\blikely\b',
                r'\bi\s+think\b',
                r'\bin\s+general\b',
                r'\btypically\b'
            ]
        }
    
    def _load_question_types(self) -> Dict[str, Dict[str, Any]]:
        """Load question type definitions with scoring weights."""
        return {
            'factual': {
                'patterns': [r'\bwhat\s+is\b', r'\bwho\s+is\b', r'\bwhen\s+did\b'],
                'weight': 1.0,
                'min_answer_length': 5,
                'extractive_requirement': 0.8
            },
            'explanatory': {
                'patterns': [r'\bhow\s+does\b', r'\bwhy\s+is\b', r'\bexplain\b'],
                'weight': 0.9,
                'min_answer_length': 15,
                'extractive_requirement': 0.7
            },
            'comparative': {
                'patterns': [r'\bcompare\b', r'\bdifference\s+between\b', r'\bvs\b'],
                'weight': 0.8,
                'min_answer_length': 20,
                'extractive_requirement': 0.6
            },
            'procedural': {
                'patterns': [r'\bhow\s+to\b', r'\bsteps\s+to\b', r'\bprocess\s+of\b'],
                'weight': 0.9,
                'min_answer_length': 25,
                'extractive_requirement': 0.7
            }
        }
    
    def _load_semantic_model(self):
        """Load semantic similarity model with error handling."""
        try:
            model_name = getattr(self.config.validation, 'semantic_model', 'all-MiniLM-L6-v2')
            self._semantic_model = SentenceTransformer(model_name)
            self.logger.info(f"Loaded semantic model: {model_name}")
        except Exception as e:
            self.logger.error(f"Failed to load semantic model: {e}")
            self.config.validation.enable_semantic = False
            raise
    
    async def validate_qa_pair(self, qa_pair) -> ValidationResult:
        """Comprehensive QA pair validation with detailed diagnostics."""
        start_time = time.time()
        self.validation_stats['total_validations'] += 1
        
        # Check cache first
        cache_key = self._generate_cache_key(qa_pair)
        if cache_key in self._validation_cache:
            self.validation_stats['cache_hits'] += 1
            cached_result = self._validation_cache[cache_key]
            cached_result.processing_time = time.time() - start_time
            return cached_result
        
        try:
            result = await self._perform_validation(qa_pair, start_time)
            
            # Cache successful validations
            if len(self._validation_cache) < 1000:  # Limit cache size
                self._validation_cache[cache_key] = result
            
            # Update statistics
            if result.is_valid:
                self.validation_stats['passed_validations'] += 1
            else:
                for issue in result.issues:
                    self.validation_stats['failed_by_reason'][issue] += 1
            
            # Update average processing time
            current_avg = self.validation_stats['avg_processing_time']
            total_validations = self.validation_stats['total_validations']
            self.validation_stats['avg_processing_time'] = (
                (current_avg * (total_validations - 1) + result.processing_time) / total_validations
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Validation failed for QA pair: {e}")
            return ValidationResult(
                is_valid=False,
                overall_score=0.0,
                scores={},
                issues=[f"Validation error: {str(e)}"],
                recommendations=["Review input data quality"],
                confidence_level="low",
                processing_time=time.time() - start_time
            )
    
    async def _perform_validation(self, qa_pair, start_time: float) -> ValidationResult:
        """Perform the actual validation with all checks."""
        scores = {}
        issues = []
        recommendations = []
        
        # 1. Basic format validation
        format_score, format_issues = self._validate_format(qa_pair)
        scores['format'] = format_score
        issues.extend(format_issues)
        
        # 2. Extractive validation (most important)
        extractive_score, extractive_issues, extractive_recs = self._validate_extractive(qa_pair)
        scores['extractive'] = extractive_score
        issues.extend(extractive_issues)
        recommendations.extend(extractive_recs)
        
        # 3. Hallucination detection
        hallucination_score, hallucination_issues = self._detect_hallucination(qa_pair)
        scores['non_hallucination'] = hallucination_score
        issues.extend(hallucination_issues)
        
        # 4. Question quality assessment
        quality_score, quality_issues, quality_recs = self._assess_question_quality(qa_pair)
        scores['question_quality'] = quality_score
        issues.extend(quality_issues)
        recommendations.extend(quality_recs)
        
        # 5. Answer quality assessment
        answer_quality_score, answer_issues, answer_recs = self._assess_answer_quality(qa_pair)
        scores['answer_quality'] = answer_quality_score
        issues.extend(answer_issues)
        recommendations.extend(answer_recs)
        
        # 6. Semantic validation (if available)
        if SEMANTIC_VALIDATION_AVAILABLE and getattr(self.config.validation, 'enable_semantic', False):
            semantic_score, semantic_issues = await self._validate_semantic_similarity(qa_pair)
            scores['semantic_relevancy'] = semantic_score
            issues.extend(semantic_issues)
        else:
            scores['semantic_relevancy'] = 0.8  # Default score when semantic validation unavailable
        
        # 7. Calculate overall score with production weights
        overall_score = self._calculate_weighted_score(scores, qa_pair)
        
        # 8. Determine validation result
        is_valid = self._determine_validity(scores, overall_score, qa_pair)
        
        # 9. Assess confidence level
        confidence_level = self._assess_confidence(scores, issues)
        
        # 10. Add general recommendations
        recommendations.extend(self._generate_recommendations(scores, qa_pair))
        
        processing_time = time.time() - start_time
        
        return ValidationResult(
            is_valid=is_valid,
            overall_score=overall_score,
            scores=scores,
            issues=issues,
            recommendations=list(set(recommendations)),  # Remove duplicates
            confidence_level=confidence_level,
            processing_time=processing_time
        )
    
    def _generate_cache_key(self, qa_pair) -> str:
        """Generate cache key for validation results."""
        return f"{hash(qa_pair.question)}_{hash(qa_pair.answer)}_{hash(qa_pair.source_text[:100])}"
    
    def _validate_format(self, qa_pair) -> Tuple[float, List[str]]:
        """Validate basic format requirements."""
        issues = []
        score = 1.0
        
        # Check question format
        if not qa_pair.question or len(qa_pair.question.strip()) < 10:
            issues.append("Question too short (minimum 10 characters)")
            score -= 0.3
        
        if not qa_pair.question.strip().endswith('?'):
            issues.append("Question should end with a question mark")
            score -= 0.1
        
        # Check answer format
        if not qa_pair.answer or len(qa_pair.answer.strip()) < 5:
            issues.append("Answer too short (minimum 5 characters)")
            score -= 0.3
        
        # Check source text
        if not qa_pair.source_text or len(qa_pair.source_text.strip()) < 10:
            issues.append("Source text too short or missing")
            score -= 0.3
        
        return max(0.0, score), issues
    
    def _validate_extractive(self, qa_pair) -> Tuple[float, List[str], List[str]]:
        """Enhanced extractive validation with multiple methods."""
        issues = []
        recommendations = []
        
        source_text = qa_pair.source_text.lower().strip()
        answer_text = qa_pair.answer.lower().strip()
        
        # Method 1: Direct substring matching
        if answer_text in source_text:
            return 1.0, [], ["Perfect extractive match found"]
        
        # Method 2: Word overlap analysis
        source_words = set(self._tokenize_text(source_text))
        answer_words = set(self._tokenize_text(answer_text))
        
        if not answer_words:
            return 0.0, ["Empty answer after tokenization"], ["Provide non-empty answer"]
        
        overlap_ratio = len(answer_words.intersection(source_words)) / len(answer_words)
        
        # Method 3: Phrase matching
        answer_phrases = self._extract_phrases(answer_text)
        source_phrases = self._extract_phrases(source_text)
        phrase_matches = sum(1 for phrase in answer_phrases if any(phrase in sp for sp in source_phrases))
        phrase_score = phrase_matches / max(len(answer_phrases), 1) if answer_phrases else 0
        
        # Combined score
        final_score = (overlap_ratio * 0.7) + (phrase_score * 0.3)
        
        # Generate issues and recommendations
        min_overlap = getattr(self.config.validation, 'min_source_overlap', 0.6)
        if final_score < min_overlap:
            issues.append(f"Low extractive score: {final_score:.2f} (minimum: {min_overlap})")
            recommendations.append("Ensure answer content is extracted directly from source text")
            
            if overlap_ratio < 0.5:
                recommendations.append("Increase word-level overlap with source text")
            if phrase_score < 0.3:
                recommendations.append("Use phrases that appear in the source text")
        
        return final_score, issues, recommendations
    
    def _detect_hallucination(self, qa_pair) -> Tuple[float, List[str]]:
        """Detect potential hallucinations in the answer."""
        answer = qa_pair.answer.lower()
        issues = []
        
        hallucination_count = 0
        total_patterns = len(self._quality_patterns['hallucination_indicators'])
        
        for pattern in self._quality_patterns['hallucination_indicators']:
            if re.search(pattern, answer):
                hallucination_count += 1
                issues.append(f"Potential hallucination detected: matches pattern '{pattern}'")
        
        # Score based on absence of hallucination indicators
        hallucination_score = 1.0 - (hallucination_count / max(total_patterns, 1))
        
        # Additional checks for specific hallucination types
        if any(phrase in answer for phrase in ['in my opinion', 'i think', 'probably', 'likely']):
            hallucination_score *= 0.5
            issues.append("Subjective language detected")
        
        return max(0.0, hallucination_score), issues
    
    def _assess_question_quality(self, qa_pair) -> Tuple[float, List[str], List[str]]:
        """Assess the quality of the question."""
        question = qa_pair.question.lower()
        issues = []
        recommendations = []
        score = 0.5  # Base score
        
        # Check for good question patterns
        good_pattern_matches = sum(1 for pattern in self._quality_patterns['good_questions'] 
                                  if re.search(pattern, question))
        if good_pattern_matches > 0:
            score += 0.3
        else:
            recommendations.append("Use more specific question words (what, how, why, etc.)")
        
        # Check for poor question patterns
        poor_pattern_matches = sum(1 for pattern in self._quality_patterns['poor_questions'] 
                                  if re.search(pattern, question))
        if poor_pattern_matches > 0:
            score -= 0.2
            issues.append("Question uses poor patterns (yes/no, opinion-based)")
            recommendations.append("Ask more specific, factual questions")
        
        # Check question length
        if len(question.split()) < 5:
            score -= 0.1
            issues.append("Question is too short")
            recommendations.append("Make questions more descriptive")
        elif len(question.split()) > 25:
            score -= 0.1
            issues.append("Question is too long")
            recommendations.append("Make questions more concise")
        
        # Check for question type
        question_type = self._identify_question_type(question)
        if question_type:
            score += 0.2
        else:
            recommendations.append("Structure question more clearly")
        
        return max(0.0, min(1.0, score)), issues, recommendations
    
    def _assess_answer_quality(self, qa_pair) -> Tuple[float, List[str], List[str]]:
        """Assess the quality of the answer."""
        answer = qa_pair.answer.strip()
        issues = []
        recommendations = []
        score = 0.5  # Base score
        
        # Check answer length appropriateness
        question_type = self._identify_question_type(qa_pair.question.lower())
        if question_type:
            type_info = self._question_types.get(question_type, {})
            min_length = type_info.get('min_answer_length', 5)
            
            if len(answer) < min_length:
                score -= 0.2
                issues.append(f"Answer too short for {question_type} question")
                recommendations.append(f"Provide more detailed answer (minimum {min_length} characters)")
        
        # Check for completeness
        if answer.endswith('...') or 'incomplete' in answer.lower():
            score -= 0.3
            issues.append("Answer appears incomplete")
            recommendations.append("Provide complete answers")
        
        # Check for quality indicators
        quality_indicators = sum(1 for pattern in self._quality_patterns['quality_indicators'] 
                               if re.search(pattern, answer.lower()))
        if quality_indicators > 0:
            score += 0.2
        
        # Check sentence structure
        sentences = re.split(r'[.!?]+', answer)
        complete_sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
        if len(complete_sentences) == 0:
            score -= 0.2
            issues.append("Answer lacks proper sentence structure")
            recommendations.append("Structure answer in complete sentences")
        
        return max(0.0, min(1.0, score)), issues, recommendations
    
    async def _validate_semantic_similarity(self, qa_pair) -> Tuple[float, List[str]]:
        """Validate semantic similarity between question, answer, and source."""
        if not self._semantic_model:
            return 0.8, ["Semantic validation skipped - model not available"]
        
        try:
            # Encode texts
            question_embedding = self._semantic_model.encode(qa_pair.question)
            answer_embedding = self._semantic_model.encode(qa_pair.answer)
            source_embedding = self._semantic_model.encode(qa_pair.source_text[:500])  # Limit source length
            
            # Calculate similarities
            import numpy as np
            qa_similarity = np.dot(question_embedding, answer_embedding) / (
                np.linalg.norm(question_embedding) * np.linalg.norm(answer_embedding)
            )
            
            answer_source_similarity = np.dot(answer_embedding, source_embedding) / (
                np.linalg.norm(answer_embedding) * np.linalg.norm(source_embedding)
            )
            
            # Combined semantic score
            semantic_score = (answer_source_similarity * 0.7) + (qa_similarity * 0.3)
            
            issues = []
            min_relevancy = getattr(self.config.validation, 'min_relevancy_score', 0.75)
            if semantic_score < min_relevancy:
                issues.append(f"Low semantic relevancy: {semantic_score:.2f}")
            
            return float(semantic_score), issues
            
        except Exception as e:
            self.logger.error(f"Semantic validation failed: {e}")
            return 0.5, [f"Semantic validation error: {str(e)}"]
    
    def _calculate_weighted_score(self, scores: Dict[str, float], qa_pair) -> float:
        """Calculate weighted overall score based on question type and requirements."""
        question_type = self._identify_question_type(qa_pair.question.lower())
        type_weight = self._question_types.get(question_type, {}).get('weight', 0.8) if question_type else 0.8
        
        # Base weights
        base_weights = {
            'extractive': 0.35,
            'non_hallucination': 0.25,
            'semantic_relevancy': 0.20,
            'question_quality': 0.10,
            'answer_quality': 0.10
        }
        
        # Adjust weights based on question type
        if question_type in ['factual', 'procedural']:
            base_weights['extractive'] = 0.4  # Higher extractive requirement
            base_weights['non_hallucination'] = 0.3
        elif question_type == 'explanatory':
            base_weights['semantic_relevancy'] = 0.25  # Higher semantic requirement
        
        # Calculate weighted score
        weighted_score = sum(scores.get(metric, 0.5) * weight for metric, weight in base_weights.items())
        
        # Apply question type weight
        return weighted_score * type_weight
    
    def _determine_validity(self, scores: Dict[str, float], overall_score: float, qa_pair) -> bool:
        """Determine if QA pair is valid based on comprehensive criteria."""
        # Get minimum thresholds
        min_overall = getattr(self.config.validation, 'min_overall_score', 0.7)
        min_extractive = getattr(self.config.validation, 'min_source_overlap', 0.6)
        min_relevancy = getattr(self.config.validation, 'min_relevancy_score', 0.75)
        
        # Question type specific requirements
        question_type = self._identify_question_type(qa_pair.question.lower())
        if question_type:
            type_info = self._question_types.get(question_type, {})
            min_extractive_for_type = type_info.get('extractive_requirement', min_extractive)
            min_extractive = max(min_extractive, min_extractive_for_type)
        
        # Core validity checks
        is_valid = (
            overall_score >= min_overall and
            scores.get('extractive', 0) >= min_extractive and
            scores.get('non_hallucination', 0) >= 0.7 and
            scores.get('semantic_relevancy', 0) >= min_relevancy and
            scores.get('format', 0) >= 0.8
        )
        
        return is_valid
    
    def _assess_confidence(self, scores: Dict[str, float], issues: List[str]) -> str:
        """Assess confidence level in the validation result."""
        avg_score = sum(scores.values()) / len(scores) if scores else 0
        issue_count = len(issues)
        
        if avg_score >= 0.9 and issue_count == 0:
            return "high"
        elif avg_score >= 0.7 and issue_count <= 2:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, scores: Dict[str, float], qa_pair) -> List[str]:
        """Generate general recommendations based on scores."""
        recommendations = []
        
        if scores.get('extractive', 0) < 0.7:
            recommendations.append("Improve extractive quality by using more direct quotes from source")
        
        if scores.get('semantic_relevancy', 0) < 0.7:
            recommendations.append("Ensure question and answer are semantically related to source content")
        
        if scores.get('question_quality', 0) < 0.6:
            recommendations.append("Improve question clarity and specificity")
        
        if scores.get('answer_quality', 0) < 0.6:
            recommendations.append("Provide more complete and well-structured answers")
        
        return recommendations
    
    def _tokenize_text(self, text: str) -> List[str]:
        """Simple tokenization for word overlap analysis."""
        return re.findall(r'\b\w+\b', text.lower())
    
    def _extract_phrases(self, text: str, min_length: int = 2) -> List[str]:
        """Extract meaningful phrases from text."""
        words = self._tokenize_text(text)
        phrases = []
        
        for i in range(len(words) - min_length + 1):
            phrase = ' '.join(words[i:i + min_length])
            phrases.append(phrase)
        
        return phrases
    
    def _identify_question_type(self, question: str) -> Optional[str]:
        """Identify the type of question based on patterns."""
        question_lower = question.lower()
        
        for q_type, info in self._question_types.items():
            for pattern in info['patterns']:
                if re.search(pattern, question_lower):
                    return q_type
        
        return None
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive validation statistics."""
        total = self.validation_stats['total_validations']
        passed = self.validation_stats['passed_validations']
        
        return {
            'total_validations': total,
            'passed_validations': passed,
            'pass_rate': passed / total if total > 0 else 0,
            'failed_by_reason': dict(self.validation_stats['failed_by_reason']),
            'average_processing_time': self.validation_stats['avg_processing_time'],
            'cache_hit_rate': self.validation_stats['cache_hits'] / total if total > 0 else 0,
            'cache_size': len(self._validation_cache)
        }

    def deduplicate_qa_pairs(self, qa_pairs: List, similarity_threshold: float = None) -> List:
        """Remove near-duplicate QA pairs using semantic similarity."""
        if not qa_pairs:
            return qa_pairs
        
        if similarity_threshold is None:
            similarity_threshold = getattr(self.config.validation, 'similarity_threshold', 0.85)
        
        self.logger.info(f"Deduplicating {len(qa_pairs)} QA pairs with threshold {similarity_threshold}")
        
        # Track duplicates by different criteria
        duplicates_removed = {
            'exact_question': 0,
            'exact_answer': 0,
            'semantic_question': 0,
            'semantic_answer': 0
        }
        
        # Stage 1: Remove exact duplicates
        unique_qa_pairs = self._remove_exact_duplicates(qa_pairs, duplicates_removed)
        
        # Stage 2: Remove semantic duplicates if enabled
        if getattr(self.config.validation, 'enable_deduplication', False) and SEMANTIC_VALIDATION_AVAILABLE:
            unique_qa_pairs = self._remove_semantic_duplicates(unique_qa_pairs, similarity_threshold, duplicates_removed)
        
        self.logger.info(f"Deduplication complete: {len(qa_pairs)} -> {len(unique_qa_pairs)} QA pairs")
        self.logger.info(f"Removed duplicates: {duplicates_removed}")
        
        return unique_qa_pairs

    def _remove_exact_duplicates(self, qa_pairs: List, duplicates_removed: Dict) -> List:
        """Remove QA pairs with identical questions or answers."""
        seen_questions = set()
        seen_answers = set()
        unique_pairs = []
        
        for qa_pair in qa_pairs:
            question_norm = self._normalize_text_for_comparison(qa_pair.question)
            answer_norm = self._normalize_text_for_comparison(qa_pair.answer)
            
            # Check for duplicate questions
            if question_norm in seen_questions:
                duplicates_removed['exact_question'] += 1
                continue
            
            # Check for duplicate answers (optional based on config)
            if (getattr(self.config.validation, 'enable_answer_deduplication', False) and 
                answer_norm in seen_answers):
                duplicates_removed['exact_answer'] += 1
                continue
            
            seen_questions.add(question_norm)
            seen_answers.add(answer_norm)
            unique_pairs.append(qa_pair)
        
        return unique_pairs

    def _remove_semantic_duplicates(self, qa_pairs: List, similarity_threshold: float, duplicates_removed: Dict) -> List:
        """Remove semantically similar QA pairs."""
        if not self._semantic_model:
            try:
                self._semantic_model = SentenceTransformer(
                    getattr(self.config.validation, 'embedding_model', 'sentence-transformers/all-MiniLM-L6-v2')
                )
            except Exception as e:
                self.logger.warning(f"Could not load semantic model for deduplication: {e}")
                return qa_pairs
        
        unique_pairs = []
        question_embeddings = []
        answer_embeddings = []
        
        max_similar = getattr(self.config.validation, 'max_similar_questions', 2)
        
        for qa_pair in qa_pairs:
            question_embedding = self._semantic_model.encode([qa_pair.question])[0]
            answer_embedding = self._semantic_model.encode([qa_pair.answer])[0]
            
            # Check for similar questions
            is_duplicate = False
            similar_question_count = 0
            
            for i, existing_q_emb in enumerate(question_embeddings):
                similarity = self._cosine_similarity(question_embedding, existing_q_emb)
                if similarity > similarity_threshold:
                    similar_question_count += 1
                    if similar_question_count >= max_similar:
                        duplicates_removed['semantic_question'] += 1
                        is_duplicate = True
                        break
            
            # Check for similar answers if enabled
            if not is_duplicate and getattr(self.config.validation, 'enable_answer_deduplication', False):
                for existing_a_emb in answer_embeddings:
                    similarity = self._cosine_similarity(answer_embedding, existing_a_emb)
                    if similarity > similarity_threshold:
                        duplicates_removed['semantic_answer'] += 1
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                unique_pairs.append(qa_pair)
                question_embeddings.append(question_embedding)
                answer_embeddings.append(answer_embedding)
        
        return unique_pairs

    def _normalize_text_for_comparison(self, text: str) -> str:
        """Normalize text for comparison purposes."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation for comparison
        text = re.sub(r'[^\w\s]', '', text)
        
        return text.strip()

    def _cosine_similarity(self, vec1, vec2) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            import numpy as np
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            return dot_product / (norm1 * norm2)
        except ImportError:
            # Fallback without numpy
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(b * b for b in vec2) ** 0.5
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
                
            return dot_product / (magnitude1 * magnitude2)
