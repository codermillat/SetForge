"""
QA Generator module for SetForge.

Handles LLM-based question-answer generation with strict extractive constraints
and hallucination prevention.
"""

import asyncio
import json
import logging
import re
import time
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass

import aiohttp
from config import Config
from text_processor import TextChunk


@dataclass
class QAPair:
    """Represents a generated question-answer pair."""
    question: str
    answer: str
    chunk_id: str
    source_text: str
    question_type: str
    confidence_score: float = 0.0
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class QAGenerator:
    """LLM-based QA generator with hallucination prevention."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        self.total_cost = 0.0
        
        # Initialize prompt templates
        self._init_prompts()
        
        # Token counting patterns
        self._token_pattern = re.compile(r'\b\w+\b')
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the QA Generator.
        
        Returns:
            Dict with health status information
        """
        status = {
            "status": "healthy",
            "api_base_url": self.config.llm.base_url,
            "api_configured": bool(self.config.llm.api_key),
            "session_initialized": self.session is not None
        }
        
        # Test API connectivity using internal method
        try:
            # Use the existing _make_api_call method which handles session initialization
            test_result = await self._make_api_call(
                system_prompt="You are a test assistant.",
                user_prompt="Hello",
                max_tokens=10
            )
            
            if test_result and 'choices' in test_result:
                status["api_test"] = "passed"
            else:
                status["api_test"] = "failed_no_response"
                status["status"] = "degraded"
                    
        except Exception as e:
            status["api_test"] = f"failed_error_{type(e).__name__}"
            status["status"] = "degraded"
            self.logger.warning(f"Health check API test failed: {e}")
        
        return status
    
    def _init_prompts(self):
        """Initialize prompt templates for different question types."""
        
        self.base_system_prompt = """You are an expert educational content analyzer. Your task is to generate high-quality question-answer pairs from the provided text.

CRITICAL REQUIREMENTS:
1. EXTRACTIVE ONLY: All answers must be DIRECTLY extracted from the source text with NO additions, interpretations, or inferences.
2. EXACT WORDING: Use the exact wording from the source text whenever possible.
3. NO HALLUCINATION: Do not add any information not explicitly stated in the source.
4. FACTUAL FOCUS: Generate questions about concrete facts, definitions, processes, and explicit comparisons.
5. TRACEABILITY: Ensure every answer can be directly traced to specific sentences in the source.

FORBIDDEN:
- Any opinion, interpretation, or inference
- Information not explicitly stated in the source
- Creative explanations or elaborations
- Assumptions about context not provided
- Phrases like "probably", "might", "could be", "in general"

REQUIRED FORMAT:
Return a JSON array of question-answer pairs, each with:
- "question": The generated question
- "answer": The exact extractive answer from the source
- "type": Question type (factual, definition, process, comparison, list)
- "confidence": Confidence score (0.0-1.0) based on how directly extractive the answer is
"""

        self.extraction_prompt = """Generate {num_questions} diverse, high-quality question-answer pairs from the following text.

SOURCE TEXT:
```
{source_text}
```

Generate questions of these types: {question_types}

CRITICAL REQUIREMENTS:
1. Each answer must be DIRECTLY extracted from the source text above
2. Use exact wording from the source when possible  
3. Generate diverse question types: factual, definition, process, comparison, list, why, how, what, when, where
4. Ensure questions are unique and non-redundant
5. Create questions at different levels of detail (specific facts, broader concepts)
6. Include both simple and complex questions when possible

Each answer must:
- Be DIRECTLY extracted from the source text above
- Use exact wording from the source when possible
- Be factually verifiable within the provided text
- NOT include any interpretation or additional context

Return as JSON array only, no other text:"""

        self.paraphrasing_prompt = """Generate {num_paraphrases} paraphrased versions of this question while keeping the same answer.

ORIGINAL QUESTION: {original_question}
ANSWER: {answer}
SOURCE TEXT: 
```
{source_text}
```

Generate paraphrased questions that:
1. Ask for the same information in different ways
2. Use different wording and sentence structure
3. Maintain the same level of specificity
4. Still have the exact same extractive answer
5. Are natural and educational

Return as JSON array of strings (just the paraphrased questions):"""

        self.validation_prompt = """Validate that this answer is completely extractive from the source text.

SOURCE TEXT:
```
{source_text}
```

QUESTION: {question}
ANSWER: {answer}

Check if the answer is ENTIRELY extracted from the source text with no additions or interpretations.
Return JSON: {{"is_extractive": true/false, "confidence": 0.0-1.0, "issues": ["list of problems if any"]}}"""
    
    async def generate_qa_pairs(self, chunk: TextChunk) -> List[QAPair]:
        """
        Generate QA pairs for a text chunk.
        
        Args:
            chunk: TextChunk to process
            
        Returns:
            List of validated QAPair objects
        """
        if not chunk.content.strip():
            return []
        
        self.logger.debug(f"Generating QA pairs for chunk: {chunk.id}")
        
        try:
            # Check cost limits
            if self.total_cost >= self.config.cost.max_total_cost_usd:
                self.logger.warning("Cost limit reached, skipping QA generation")
                return []
            
            # Estimate cost for this chunk
            estimated_cost = self._estimate_cost(chunk.content)
            if self.total_cost + estimated_cost > self.config.cost.max_total_cost_usd:
                self.logger.warning(f"Skipping chunk {chunk.id} to stay within cost limit")
                return []
            
            # Generate QA pairs
            raw_qa_pairs = await self._call_llm_for_qa_generation(chunk)
            
            # Convert to QAPair objects and validate
            qa_pairs = []
            for raw_qa in raw_qa_pairs:
                qa_pair = QAPair(
                    question=raw_qa.get('question', '').strip(),
                    answer=raw_qa.get('answer', '').strip(),
                    chunk_id=chunk.id,
                    source_text=chunk.content,
                    question_type=raw_qa.get('type', 'factual'),
                    confidence_score=raw_qa.get('confidence', 0.0),
                    metadata={
                        'file_path': chunk.file_path,
                        'section_title': chunk.section_title,
                        'generation_timestamp': time.time(),
                        'model_used': self.config.llm.model_name
                    }
                )
                
                # Basic validation
                if self._basic_validate_qa_pair(qa_pair):
                    qa_pairs.append(qa_pair)
                else:
                    self.logger.debug(f"Basic validation failed for QA pair from chunk {chunk.id}")
            
            self.logger.info(f"Generated {len(qa_pairs)} valid QA pairs for chunk {chunk.id}")
            return qa_pairs
            
        except Exception as e:
            self.logger.error(f"Failed to generate QA pairs for chunk {chunk.id}: {e}")
            return []
    
    async def _call_llm_for_qa_generation(self, chunk: TextChunk) -> List[Dict]:
        """Call LLM API to generate QA pairs."""
        if self.config.dry_run:
            return self._generate_mock_qa_pairs(chunk)
        
        # Prepare prompt
        question_types = ", ".join(self.config.qa.question_types)
        user_prompt = self.extraction_prompt.format(
            num_questions=self.config.qa.questions_per_chunk,
            source_text=chunk.content,
            question_types=question_types
        )
        
        # Make API call
        response = await self._make_api_call(
            system_prompt=self.base_system_prompt,
            user_prompt=user_prompt,
            max_tokens=self.config.llm.max_tokens
        )
        
        # Update cost tracking
        self.total_cost += self._calculate_actual_cost(response.get('usage', {}))
        
        # Parse response
        try:
            qa_pairs = json.loads(response['content'])
            if isinstance(qa_pairs, dict):
                qa_pairs = [qa_pairs]
            return qa_pairs
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse LLM response as JSON: {e}")
            self.logger.debug(f"Raw response: {response['content']}")
            return []
    
    async def _make_api_call(self, system_prompt: str, user_prompt: str, 
                           max_tokens: int = None) -> Dict:
        """Make authenticated API call to DigitalOcean LLM service with enhanced error handling."""
        if self.session is None:
            connector = aiohttp.TCPConnector(
                limit=100,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=self.config.llm.timeout)
            )
        
        max_tokens = max_tokens or self.config.llm.max_tokens
        
        payload = {
            "model": self.config.llm.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": self.config.llm.temperature,
        }
        
        headers = {
            "Authorization": f"Bearer {self.config.llm.api_key}",
            "Content-Type": "application/json"
        }
        
        last_exception = None
        for attempt in range(self.config.llm.max_retries):
            try:
                async with self.session.post(
                    f"{self.config.llm.base_url}/v1/chat/completions",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        # Enhanced response parsing with fallbacks
                        try:
                            result = await response.json()
                        except aiohttp.ContentTypeError:
                            # Handle text/plain responses
                            response_text = await response.text()
                            try:
                                import json
                                result = json.loads(response_text)
                            except json.JSONDecodeError as e:
                                self.logger.error(f"Failed to parse response as JSON: {response_text[:200]}...")
                                raise Exception(f"Invalid JSON response: {str(e)}")
                        
                        # Validate response structure
                        if not result.get('choices') or not result['choices']:
                            raise Exception(f"Invalid response structure: missing choices")
                        
                        if not result['choices'][0].get('message', {}).get('content'):
                            raise Exception(f"Invalid response structure: missing content")
                        
                        return {
                            'content': result['choices'][0]['message']['content'],
                            'usage': result.get('usage', {}),
                            'status': 'success',
                            'attempt': attempt + 1
                        }
                    
                    elif response.status == 429:  # Rate limit
                        wait_time = min(2 ** attempt, 60)  # Cap at 60 seconds
                        self.logger.warning(f"Rate limit hit on attempt {attempt + 1}, waiting {wait_time}s")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    elif response.status in [502, 503, 504]:  # Server errors
                        wait_time = min(2 ** attempt, 30)  # Exponential backoff for server errors
                        error_text = await response.text()
                        self.logger.warning(f"Server error {response.status} on attempt {attempt + 1}, retrying in {wait_time}s: {error_text[:100]}")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    else:
                        error_text = await response.text()
                        raise Exception(f"API call failed with status {response.status}: {error_text}")
                        
            except asyncio.TimeoutError as e:
                last_exception = e
                wait_time = min(self.config.llm.retry_delay * (2 ** attempt), 30)
                self.logger.warning(f"API call timeout on attempt {attempt + 1}/{self.config.llm.max_retries}, retrying in {wait_time}s")
                if attempt < self.config.llm.max_retries - 1:
                    await asyncio.sleep(wait_time)
                    continue
                    
            except aiohttp.ClientError as e:
                last_exception = e
                wait_time = min(self.config.llm.retry_delay * (2 ** attempt), 30)
                self.logger.warning(f"Client error on attempt {attempt + 1}/{self.config.llm.max_retries}: {str(e)}")
                if attempt < self.config.llm.max_retries - 1:
                    await asyncio.sleep(wait_time)
                    continue
                    
            except Exception as e:
                last_exception = e
                self.logger.error(f"Unexpected error on attempt {attempt + 1}/{self.config.llm.max_retries}: {str(e)}")
                if attempt < self.config.llm.max_retries - 1:
                    wait_time = min(self.config.llm.retry_delay * (2 ** attempt), 30)
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    break
        
        # All retries exhausted
        raise Exception(f"All {self.config.llm.max_retries} API call attempts failed. Last error: {str(last_exception)}")
    
    def _estimate_cost(self, text: str) -> float:
        """Estimate API cost for processing text."""
        # Rough token estimation (1 token ≈ 4 characters for English)
        estimated_tokens = len(text) // 4
        
        # Add tokens for system prompt and response
        system_tokens = len(self.base_system_prompt) // 4
        response_tokens = self.config.llm.max_tokens
        
        total_tokens = estimated_tokens + system_tokens + response_tokens
        
        return (total_tokens / 1000) * self.config.cost.cost_per_1k_tokens
    
    def _calculate_actual_cost(self, usage: Dict) -> float:
        """Calculate actual cost from API usage statistics."""
        if not usage:
            return 0.0
        
        total_tokens = usage.get('total_tokens', 0)
        return (total_tokens / 1000) * self.config.cost.cost_per_1k_tokens
    
    def _basic_validate_qa_pair(self, qa_pair: QAPair) -> bool:
        """Perform basic validation on a QA pair."""
        # Check minimum lengths
        if len(qa_pair.question) < self.config.qa.min_question_length:
            return False
        if len(qa_pair.answer) < self.config.qa.min_answer_length:
            return False
        
        # Check maximum lengths
        if len(qa_pair.question) > self.config.qa.max_question_length:
            return False
        if len(qa_pair.answer) > self.config.qa.max_answer_length:
            return False
        
        # Check for forbidden patterns
        answer_lower = qa_pair.answer.lower()
        for pattern in self.config.qa.forbidden_patterns:
            if pattern.lower() in answer_lower:
                self.logger.debug(f"Forbidden pattern '{pattern}' found in answer")
                return False
        
        # Check if answer exists in source text (basic check)
        if not self._check_answer_in_source(qa_pair.answer, qa_pair.source_text):
            self.logger.debug("Answer not found in source text")
            return False
        
        return True
    
    def _check_answer_in_source(self, answer: str, source_text: str) -> bool:
        """Check if answer content exists in source text."""
        # Normalize texts for comparison
        answer_norm = re.sub(r'\s+', ' ', answer.lower().strip())
        source_norm = re.sub(r'\s+', ' ', source_text.lower().strip())
        
        # Check for exact match first
        if answer_norm in source_norm:
            return True
        
        # Check for substantial overlap (80% of answer words should be in source)
        answer_words = set(answer_norm.split())
        source_words = set(source_norm.split())
        
        if not answer_words:
            return False
        
        overlap = len(answer_words.intersection(source_words))
        overlap_ratio = overlap / len(answer_words)
        
        return overlap_ratio >= 0.8
    
    def _generate_mock_qa_pairs(self, chunk: TextChunk) -> List[Dict]:
        """Generate mock QA pairs for dry run mode."""
        return [
            {
                "question": f"What is mentioned in the text about {chunk.section_title or 'this topic'}?",
                "answer": chunk.content[:100] + "..." if len(chunk.content) > 100 else chunk.content,
                "type": "factual",
                "confidence": 0.9
            }
        ]
    
    async def close(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
    
    def get_total_cost(self) -> float:
        """Get total cost incurred so far."""
        return self.total_cost

    async def generate_enhanced_qa_pairs(self, chunk: TextChunk) -> List[QAPair]:
        """Generate enhanced QA pairs with paraphrasing and data augmentation."""
        if not chunk.content.strip():
            return []

        self.logger.debug(f"Generating enhanced QA pairs for chunk: {chunk.id}")
        
        try:
            # Check cost limits
            if self.total_cost >= self.config.cost.max_total_cost_usd:
                self.logger.warning("Cost limit reached, skipping QA generation")
                return []

            # Generate base QA pairs with increased count
            base_qa_pairs = await self._call_llm_for_qa_generation(chunk)
            
            all_qa_pairs = []
            
            # Convert base pairs and add paraphrases if enabled
            for raw_qa in base_qa_pairs:
                # Create main QA pair
                main_qa_pair = QAPair(
                    question=raw_qa.get('question', '').strip(),
                    answer=raw_qa.get('answer', '').strip(),
                    chunk_id=chunk.id,
                    source_text=chunk.content,
                    question_type=raw_qa.get('type', 'factual'),
                    confidence_score=raw_qa.get('confidence', 0.0),
                    metadata={
                        'file_path': chunk.file_path,
                        'section_title': chunk.section_title,
                        'generation_timestamp': time.time(),
                        'model_used': self.config.llm.model_name,
                        'is_paraphrase': False,
                        'original_question_id': None
                    }
                )
                
                if self._basic_validate_qa_pair(main_qa_pair):
                    all_qa_pairs.append(main_qa_pair)
                    
                    # Generate paraphrases if enabled
                    if getattr(self.config.qa, 'enable_paraphrasing', False):
                        paraphrases = await self._generate_paraphrases(main_qa_pair, chunk)
                        all_qa_pairs.extend(paraphrases)

            # Limit total questions per chunk if configured
            max_total = getattr(self.config.qa, 'max_total_questions', 15)
            if len(all_qa_pairs) > max_total:
                # Sort by confidence and keep the best ones
                all_qa_pairs.sort(key=lambda x: x.confidence_score, reverse=True)
                all_qa_pairs = all_qa_pairs[:max_total]

            self.logger.info(f"Generated {len(all_qa_pairs)} enhanced QA pairs for chunk {chunk.id}")
            return all_qa_pairs
            
        except Exception as e:
            self.logger.error(f"Failed to generate enhanced QA pairs for chunk {chunk.id}: {e}")
            return []

    async def _generate_paraphrases(self, original_qa: QAPair, chunk: TextChunk) -> List[QAPair]:
        """Generate paraphrased versions of a question."""
        paraphrases = []
        
        try:
            num_paraphrases = getattr(self.config.qa, 'paraphrases_per_question', 2)
            
            if self.config.dry_run:
                # Mock paraphrases for dry run
                for i in range(num_paraphrases):
                    paraphrase_qa = QAPair(
                        question=f"[Paraphrase {i+1}] {original_qa.question}",
                        answer=original_qa.answer,
                        chunk_id=original_qa.chunk_id,
                        source_text=original_qa.source_text,
                        question_type=original_qa.question_type,
                        confidence_score=original_qa.confidence_score * 0.9,  # Slightly lower confidence
                        metadata={
                            **original_qa.metadata,
                            'is_paraphrase': True,
                            'original_question': original_qa.question,
                            'paraphrase_index': i + 1
                        }
                    )
                    paraphrases.append(paraphrase_qa)
                return paraphrases

            # Prepare paraphrasing prompt
            user_prompt = self.paraphrasing_prompt.format(
                num_paraphrases=num_paraphrases,
                original_question=original_qa.question,
                answer=original_qa.answer,
                source_text=chunk.content
            )
            
            # Make API call for paraphrases
            response = await self._make_api_call(
                system_prompt="You are an expert at paraphrasing educational questions while maintaining their meaning and answers.",
                user_prompt=user_prompt,
                max_tokens=300
            )
            
            # Update cost tracking
            self.total_cost += self._calculate_actual_cost(response.get('usage', {}))
            
            # Parse paraphrased questions
            try:
                paraphrased_questions = json.loads(response['content'])
                if isinstance(paraphrased_questions, str):
                    paraphrased_questions = [paraphrased_questions]
                
                for i, paraphrased_question in enumerate(paraphrased_questions):
                    if isinstance(paraphrased_question, str) and paraphrased_question.strip():
                        paraphrase_qa = QAPair(
                            question=paraphrased_question.strip(),
                            answer=original_qa.answer,
                            chunk_id=original_qa.chunk_id,
                            source_text=original_qa.source_text,
                            question_type=original_qa.question_type,
                            confidence_score=original_qa.confidence_score * 0.9,  # Slightly lower confidence
                            metadata={
                                **original_qa.metadata,
                                'is_paraphrase': True,
                                'original_question': original_qa.question,
                                'paraphrase_index': i + 1
                            }
                        )
                        
                        if self._basic_validate_qa_pair(paraphrase_qa):
                            paraphrases.append(paraphrase_qa)
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse paraphrasing response: {e}")
                
        except Exception as e:
            self.logger.error(f"Failed to generate paraphrases: {e}")
        
        return paraphrases

    def _generate_multiple_questions_for_answer(self, answer: str, chunk: TextChunk) -> List[str]:
        """Generate multiple questions that have the same answer."""
        # This is a future enhancement - for now, return empty list
        # Could be implemented with additional LLM calls to generate
        # different question formulations for the same extractive answer
        return []
