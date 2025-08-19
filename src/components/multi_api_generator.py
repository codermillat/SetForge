"""
Multi-API Key Generator for SetForge Research Project
MIT License - Open Source Research Project
"""

import asyncio
import aiohttp
import json
import time
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuotaExceededException(Exception):
    """Exception raised when API quota is exceeded"""
    pass

class ModelType(Enum):
    GEMINI = "gemini"
    LLAMA = "llama"
    GPT = "gpt"

@dataclass
class APIConfig:
    api_key: str
    model: str
    endpoint: str
    rate_limit: Dict[str, int]
    purpose: str

@dataclass
class QAPair:
    question: str
    answer: str
    context: str
    model_used: str
    quality_score: float
    generation_time: float
    api_account: str

class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, rpm_limit: int, tpm_limit: int, rpd_limit: int):
        self.rpm_limit = rpm_limit
        self.tpm_limit = tpm_limit
        self.rpd_limit = rpd_limit
        self.requests_this_minute = 0
        self.tokens_this_minute = 0
        self.requests_today = 0
        self.last_reset = time.time()
        self.minute_reset = time.time()
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        current_time = time.time()
        
        # Reset minute counter if needed
        if current_time - self.minute_reset >= 60:
            self.requests_this_minute = 0
            self.tokens_this_minute = 0
            self.minute_reset = current_time
        
        # Reset daily counter if needed
        if current_time - self.last_reset >= 86400:  # 24 hours
            self.requests_today = 0
            self.last_reset = current_time
        
        # Check if we need to wait
        if self.requests_this_minute >= self.rpm_limit:
            wait_time = 60 - (current_time - self.minute_reset)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                self.requests_this_minute = 0
                self.minute_reset = time.time()
    
    async def can_make_request(self) -> bool:
        """Check if we can make a request"""
        current_time = time.time()
        
        # Reset counters if needed
        if current_time - self.minute_reset >= 60:
            self.requests_this_minute = 0
            self.tokens_this_minute = 0
            self.minute_reset = current_time
        
        if current_time - self.last_reset >= 86400:
            self.requests_today = 0
            self.last_reset = current_time
        
        return (self.requests_this_minute < self.rpm_limit and 
                self.requests_today < self.rpd_limit)

class LoadBalancer:
    """Load balancer for multiple API accounts"""
    
    def __init__(self, api_configs: Dict[str, APIConfig]):
        self.api_configs = api_configs
        self.weights = self._calculate_weights()
    
    def _calculate_weights(self) -> Dict[str, float]:
        """Calculate weights for load balancing"""
        total_weight = 0
        weights = {}
        
        for account_id, config in self.api_configs.items():
            if "gemini" in account_id.lower():
                weight = 0.33  # Equal distribution for Gemini accounts
            elif "llama" in account_id.lower():
                weight = 0.0   # Backup only
            else:
                weight = 0.0   # Emergency only
            weights[account_id] = weight
            total_weight += weight
        
        # Normalize weights
        if total_weight > 0:
            for account_id in weights:
                weights[account_id] /= total_weight
        
        return weights
    
    async def get_available_account(self) -> Optional[str]:
        """Get an available account for API calls"""
        available_accounts = []
        
        for account_id, config in self.api_configs.items():
            if self.weights.get(account_id, 0) > 0:
                available_accounts.append(account_id)
        
        if available_accounts:
            return random.choice(available_accounts)
        return None

class QualityMonitor:
    """Monitor and calculate quality metrics"""
    
    def calculate_quality(self, qa_pair: QAPair) -> float:
        """Calculate overall quality score"""
        scores = []
        
        # Information density
        info_density = self._calculate_info_density(qa_pair.answer)
        scores.append(info_density * 0.25)
        
        # Conciseness
        conciseness = self._calculate_conciseness(qa_pair.answer)
        scores.append(conciseness * 0.20)
        
        # Cultural relevance
        cultural_relevance = self._calculate_cultural_relevance(qa_pair)
        scores.append(cultural_relevance * 0.25)
        
        # Domain expertise
        domain_expertise = self._calculate_domain_expertise(qa_pair)
        scores.append(domain_expertise * 0.20)
        
        # Practical value
        practical_value = self._calculate_practical_value(qa_pair.answer)
        scores.append(practical_value * 0.10)
        
        return sum(scores)
    
    def _calculate_info_density(self, text: str) -> float:
        """Calculate information density score"""
        words = text.split()
        if not words:
            return 0.0
        
        # Count meaningful words (exclude common words)
        meaningful_words = [w for w in words if len(w) > 3]
        density = len(meaningful_words) / len(words)
        
        return min(density * 2, 1.0)  # Scale to 0-1
    
    def _calculate_conciseness(self, text: str) -> float:
        """Calculate conciseness score"""
        words = text.split()
        if not words:
            return 0.0
        
        # Prefer answers between 50-200 words
        if 50 <= len(words) <= 200:
            return 1.0
        elif len(words) < 50:
            return len(words) / 50
        else:
            return max(0.0, 1.0 - (len(words) - 200) / 100)
    
    def _calculate_cultural_relevance(self, qa_pair: QAPair) -> float:
        """Calculate cultural relevance score"""
        text = (qa_pair.question + " " + qa_pair.answer).lower()
        
        cultural_keywords = [
            "bangladesh", "bengali", "hsc", "ssc", "india", "indian",
            "university", "admission", "visa", "scholarship"
        ]
        
        matches = sum(1 for keyword in cultural_keywords if keyword in text)
        return min(matches / len(cultural_keywords), 1.0)
    
    def _calculate_domain_expertise(self, qa_pair: QAPair) -> float:
        """Calculate domain expertise score"""
        text = (qa_pair.question + " " + qa_pair.answer).lower()
        
        expertise_keywords = [
            "university", "program", "course", "degree", "admission",
            "requirements", "fees", "scholarship", "visa", "accommodation"
        ]
        
        matches = sum(1 for keyword in expertise_keywords if keyword in text)
        return min(matches / len(expertise_keywords), 1.0)
    
    def _calculate_practical_value(self, text: str) -> float:
        """Calculate practical value score"""
        practical_indicators = [
            "step", "process", "procedure", "requirement", "document",
            "form", "application", "deadline", "cost", "fee"
        ]
        
        text_lower = text.lower()
        matches = sum(1 for indicator in practical_indicators if indicator in text_lower)
        return min(matches / len(practical_indicators), 1.0)

class MultiAPIGenerator:
    """
    Multi-API Key Generator for Research Project
    Supports multiple Gemini accounts with load balancing and quality optimization
    """
    
    def __init__(self):
        self.api_configs = self._initialize_api_configs()
        self.rate_limiters = self._initialize_rate_limiters()
        self.quality_monitor = QualityMonitor()
        self.load_balancer = LoadBalancer(self.api_configs)
        
    def _initialize_api_configs(self) -> Dict[str, APIConfig]:
        """Initialize API configurations for multiple accounts"""
        import os
        
        return {
            "gemini_research_1": APIConfig(
                api_key=os.getenv("GEMINI_API_KEY_1", ""),
                model="gemini-2.5-pro",
                endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent",
                rate_limit={"rpm": 1000, "tpm": 4000000, "rpd": 14400},
                purpose="Primary Q&A generation"
            ),
            "gemini_research_2": APIConfig(
                api_key=os.getenv("GEMINI_API_KEY_2", ""),
                model="gemini-2.5-pro", 
                endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent",
                rate_limit={"rpm": 1000, "tpm": 4000000, "rpd": 14400},
                purpose="Secondary Q&A generation"
            ),
            "gemini_research_3": APIConfig(
                api_key=os.getenv("GEMINI_API_KEY_3", ""),
                model="gemini-2.5-pro",
                endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent", 
                rate_limit={"rpm": 1000, "tpm": 4000000, "rpd": 14400},
                purpose="Quality validation"
            ),
            "llama_backup_1": APIConfig(
                api_key=os.getenv("DIGITALOCEAN_API_KEY_1", ""),
                model="llama3.3-70b-instruct",
                endpoint="https://inference.do-ai.run/v1/chat/completions",
                rate_limit={"rpm": 100, "tpm": 1000000, "rpd": 10000},
                purpose="Backup generation"
            ),
            "llama_backup_2": APIConfig(
                api_key=os.getenv("DIGITALOCEAN_API_KEY_2", ""),
                model="llama3.3-70b-instruct",
                endpoint="https://inference.do-ai.run/v1/chat/completions",
                rate_limit={"rpm": 100, "tpm": 1000000, "rpd": 10000},
                purpose="Backup generation"
            ),
            "gpt_backup": APIConfig(
                api_key=os.getenv("OPENAI_API_KEY_1", ""),
                model="gpt-4o-mini",
                endpoint="https://api.openai.com/v1/chat/completions",
                rate_limit={"rpm": 500, "tpm": 2000000, "rpd": 12000},
                purpose="Speed optimization"
            )
        }
    
    def _initialize_rate_limiters(self) -> Dict[str, RateLimiter]:
        """Initialize rate limiters for each API account"""
        limiters = {}
        for account_id, config in self.api_configs.items():
            limiters[account_id] = RateLimiter(
                rpm_limit=config.rate_limit["rpm"],
                tpm_limit=config.rate_limit["tpm"],
                rpd_limit=config.rate_limit["rpd"]
            )
        return limiters
    
    async def generate_text(self, prompt: str, purpose: str) -> Optional[str]:
        """Generate text for a given prompt using the multi-API strategy."""
        start_time = time.time()
        
        # Get available account from load balancer
        account_id = await self.load_balancer.get_available_account()
        
        if not account_id:
            logger.warning("No available primary accounts, using backup strategy")
            account_id = await self._get_backup_account()
        
        if not account_id:
            logger.error("No available API accounts, including backups.")
            return None

        try:
            config = self.api_configs[account_id]
            
            # Check rate limits
            await self.rate_limiters[account_id].wait_if_needed()
            
            if config.model.startswith("gemini"):
                return await self._call_gemini_api(config, prompt)
            elif config.model.startswith("llama"):
                return await self._call_llama_api(config, prompt)
            elif config.model.startswith("gpt"):
                return await self._call_gpt_api(config, prompt)
            else:
                raise ValueError(f"Unsupported model: {config.model}")

        except Exception as e:
            logger.error(f"Error generating text with {account_id}: {e}")
            # Try backup account
            try:
                backup_account = await self._get_backup_account()
                if backup_account:
                    logger.info(f"Retrying with backup account: {backup_account}")
                    config = self.api_configs[backup_account]
                    if config.model.startswith("gemini"):
                        return await self._call_gemini_api(config, prompt)
                    elif config.model.startswith("llama"):
                        return await self._call_llama_api(config, prompt)
                    elif config.model.startswith("gpt"):
                        return await self._call_gpt_api(config, prompt)
            except Exception as backup_e:
                logger.error(f"Backup generation also failed: {backup_e}")

        return None

    async def generate_qa_pair(self, context: str, persona: str, question_type: str) -> QAPair:
        """Generate Q&A pair using multi-API strategy with load balancing"""
        start_time = time.time()
        
        # Get available account from load balancer
        account_id = await self.load_balancer.get_available_account()
        
        if not account_id:
            logger.warning("No available accounts, using backup strategy")
            account_id = await self._get_backup_account()
        
        # Generate Q&A pair
        try:
            qa_pair = await self._generate_with_account(account_id, context, persona, question_type)
            
            # Validate quality
            quality_score = self.quality_monitor.calculate_quality(qa_pair)
            
            # Regenerate with backup if quality is low
            if quality_score < 8.0:
                logger.info(f"Low quality ({quality_score}), regenerating with backup")
                backup_account = await self._get_backup_account()
                qa_pair = await self._generate_with_account(backup_account, context, persona, question_type)
                quality_score = self.quality_monitor.calculate_quality(qa_pair)
            
            qa_pair.quality_score = quality_score
            qa_pair.generation_time = time.time() - start_time
            qa_pair.api_account = account_id
            
            return qa_pair
            
        except Exception as e:
            logger.error(f"Error generating with {account_id}: {e}")
            # Try backup account
            backup_account = await self._get_backup_account()
            return await self._generate_with_account(backup_account, context, persona, question_type)
    
    async def _generate_with_account(self, account_id: str, context: str, persona: str, question_type: str) -> QAPair:
        """Generate Q&A pair with specific account"""
        config = self.api_configs[account_id]
        
        # Check rate limits
        await self.rate_limiters[account_id].wait_if_needed()
        
        # Generate question
        question = await self._generate_question(config, context, persona, question_type)
        
        # Generate answer
        answer = await self._generate_answer(config, context, question, persona)
        
        return QAPair(
            question=question,
            answer=answer,
            context=context,
            model_used=config.model,
            quality_score=0.0,  # Will be calculated later
            generation_time=0.0,  # Will be set later
            api_account=account_id
        )
    
    async def _generate_question(self, config: APIConfig, context: str, persona: str, question_type: str) -> str:
        """Generate question using specific API account"""
        prompt = self._create_question_prompt(context, persona, question_type)
        
        if config.model.startswith("gemini"):
            return await self._call_gemini_api(config, prompt)
        elif config.model.startswith("llama"):
            return await self._call_llama_api(config, prompt)
        elif config.model.startswith("gpt"):
            return await self._call_gpt_api(config, prompt)
        else:
            raise ValueError(f"Unsupported model: {config.model}")
    
    async def _generate_answer(self, config: APIConfig, context: str, question: str, persona: str) -> str:
        """Generate answer using specific API account"""
        prompt = self._create_answer_prompt(context, question, persona)
        
        if config.model.startswith("gemini"):
            return await self._call_gemini_api(config, prompt)
        elif config.model.startswith("llama"):
            return await self._call_llama_api(config, prompt)
        elif config.model.startswith("gpt"):
            return await self._call_gpt_api(config, prompt)
        else:
            raise ValueError(f"Unsupported model: {config.model}")
    
    async def _call_gemini_api(self, config: APIConfig, prompt: str) -> str:
        """Call Gemini API (Google AI) with retry logic and robust response validation"""
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": config.api_key
        }
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        timeout = aiohttp.ClientTimeout(total=60)  # 60 second timeout
        retries = 3
        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(config.endpoint, headers=headers, json=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            try:
                                if "candidates" in result and result["candidates"]:
                                    candidate = result["candidates"][0]
                                    if "content" in candidate and "parts" in candidate["content"]:
                                        answer = candidate["content"]["parts"][0]["text"]
                                    elif "content" in candidate:
                                        content = candidate["content"]
                                        answer = str(content) if isinstance(content, str) else str(content)
                                    else:
                                        answer = str(result)
                                elif "text" in result:
                                    answer = str(result["text"])
                                else:
                                    answer = str(result)
                            except (KeyError, IndexError):
                                answer = str(result)
                            # Robust response validation
                            if not answer or not isinstance(answer, str) or answer.strip() == "" or answer.strip().startswith("{'role': 'model'"):
                                raise ValueError(f"Malformed or empty Gemini API response: {answer}")
                            return answer
                        elif response.status == 429:
                            error_text = await response.text()
                            raise QuotaExceededException(f"Gemini API quota exceeded: {error_text}")
                        else:
                            error_text = await response.text()
                            raise Exception(f"Gemini API error: {response.status} - {error_text}")
            except Exception as e:
                logger.warning(f"Gemini API call failed (attempt {attempt+1}/{retries}): {e}")
                await asyncio.sleep(2 ** attempt)
        raise Exception("Gemini API failed after retries")

    async def _call_llama_api(self, config: APIConfig, prompt: str) -> str:
        """Call Llama API (DigitalOcean Gradient AI) with retry logic and robust response validation"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.api_key}"
        }
        data = {
            "model": config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 800
        }
        timeout = aiohttp.ClientTimeout(total=60)  # 60 second timeout
        retries = 3
        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(config.endpoint, headers=headers, json=data) as response:
                        if response.status == 200:
                            content_type = response.headers.get('content-type', '')
                            if 'application/json' in content_type:
                                result = await response.json()
                                answer = result["choices"][0]["message"]["content"]
                            else:
                                result = await response.text()
                                try:
                                    import json
                                    json_result = json.loads(result)
                                    answer = json_result["choices"][0]["message"]["content"]
                                except (json.JSONDecodeError, KeyError, IndexError):
                                    answer = result.strip()
                            # Robust response validation
                            if not answer or not isinstance(answer, str) or answer.strip() == "" or answer.strip().startswith("{'role': 'model'"):
                                raise ValueError(f"Malformed or empty Llama API response: {answer}")
                            return answer
                        else:
                            error_text = await response.text()
                            raise Exception(f"DigitalOcean Llama API error: {response.status} - {error_text}")
            except Exception as e:
                logger.warning(f"Llama API call failed (attempt {attempt+1}/{retries}): {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        raise Exception("Llama API failed after retries")
    
    async def _call_gpt_api(self, config: APIConfig, prompt: str) -> str:
        """Call GPT API with retry logic and robust response validation"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.api_key}"
        }
        data = {
            "model": config.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800
        }
        timeout = aiohttp.ClientTimeout(total=60)  # 60 second timeout
        retries = 3
        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(config.endpoint, headers=headers, json=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            answer = result["choices"][0]["message"]["content"]
                            # Robust response validation
                            if not answer or not isinstance(answer, str) or answer.strip() == "" or answer.strip().startswith("{'role': 'model'"):
                                raise ValueError(f"Malformed or empty GPT API response: {answer}")
                            return answer
                        else:
                            error_text = await response.text()
                            raise Exception(f"GPT API error: {response.status} - {error_text}")
            except Exception as e:
                logger.warning(f"GPT API call failed (attempt {attempt+1}/{retries}): {e}")
                await asyncio.sleep(2 ** attempt)
        raise Exception("GPT API failed after retries")
    
    def _create_question_prompt(self, context: str, persona: str, question_type: str) -> str:
        """Create optimized question generation prompt"""
        return f"""You are an expert educational consultant helping Bangladeshi students understand Indian universities.

Context Information:
{context}

Student Profile: {persona}
Question Type: {question_type}

Generate a creative, realistic question that:
1. Is specific to the provided context
2. Reflects real student concerns and scenarios
3. Requires detailed, actionable answers
4. Is culturally appropriate for Bangladeshi students
5. Is personalized to the student profile

Generate a single, high-quality question:"""

    def _create_answer_prompt(self, context: str, question: str, persona: str) -> str:
        """Create optimized answer generation prompt"""
        return f"""You are an expert educational consultant helping a {persona} from Bangladesh who wants to study in India.

Context Information:
{context}

Question: {question}

Provide a comprehensive, detailed answer that:
1. Uses ONLY information from the provided context
2. Is culturally sensitive and appropriate for Bangladeshi students
3. Includes specific details, numbers, and requirements
4. Provides actionable advice and next steps
5. Is comprehensive but concise (50-150 words)

Provide a detailed, comprehensive answer:"""

    async def _get_backup_account(self) -> str:
        """Get backup account for failover"""
        backup_accounts = ["llama_backup_1", "llama_backup_2", "gpt_backup"]
        for account in backup_accounts:
            if account in self.rate_limiters and await self.rate_limiters[account].can_make_request():
                return account
        raise Exception("No backup accounts available")
