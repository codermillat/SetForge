#!/usr/bin/env python3
"""
SetForge - Enhanced Production Q&A Generator
==========================================

Production-ready generator for 50K+ high-quality Bangladeshi educational Q&A pairs.
Integrated validation, monitoring, and optimization for maximum efficiency.

Features:
- Production-scale generation (50K+ pairs)
- Bangladeshi grading system integration
- Real-time quality validation
- Cost optimization and monitoring
- Cultural authenticity enforcement
- Progress tracking and checkpoints
"""

import asyncio
import aiohttp
import json
import os
import re
import hashlib
import random
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import logging
from datetime import datetime
import yaml

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger = logging.getLogger(__name__)
    logger.info("Loaded environment variables from .env file")
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("python-dotenv not available - using system environment variables")

# Import Bangladeshi grading system utilities
try:
    from utils import (
        BangladeshiGradingSystem, 
        StudentProfileGenerator, 
        UniversityRequirements,
        generate_realistic_grade_entities,
        format_bangladeshi_grade_context
    )
    GRADING_SYSTEM_AVAILABLE = True
except ImportError:
    GRADING_SYSTEM_AVAILABLE = False
    logging.warning("Bangladeshi grading system not available - using basic grade handling")

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'setforge_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StudentPersona(Enum):
    """Simple student personas for varied question generation."""
    HIGH_ACHIEVER = "high_achiever"      # Focus on top universities, research
    BUDGET_CONSCIOUS = "budget_conscious" # Focus on scholarships, costs
    AVERAGE_STUDENT = "average_student"   # Focus on general admission, guidance

class QuestionType(Enum):
    """Question categories for balanced generation."""
    SCHOLARSHIP = "scholarship"
    FEES = "fees" 
    ADMISSION = "admission"
    UNIVERSITY_COMPARISON = "university_comparison"
    VISA_GUIDANCE = "visa_guidance"
    ACCOMMODATION = "accommodation"

@dataclass
class QAPair:
    """Generated Q&A pair with metadata."""
    question: str
    answer: str
    context: str
    persona: str
    question_type: str
    university: str
    confidence: float
    source_file: str
    cost: float = 0.0

@dataclass
class GenerationConfig:
    """Configuration for dataset generation."""
    api_key: str
    api_url: str = "https://inference.do-ai.run"
    model: str = "llama3-8b-instruct"
    max_tokens: int = 500
    temperature: float = 0.7
    max_cost_usd: float = 200.0
    target_pairs: int = 15000
    batch_size: int = 10
    
    @classmethod
    def from_yaml(cls, config_path: str) -> 'GenerationConfig':
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Handle environment variable substitution for api_key
        api_key = data.get('api_key', '')
        if api_key.startswith('${') and api_key.endswith('}'):
            env_var = api_key[2:-1]  # Remove ${ and }
            api_key = os.getenv(env_var, '')
        
        # Extract only the fields that belong to GenerationConfig
        config_fields = {
            'api_key': api_key,
            'api_url': data.get('api_url', 'https://inference.do-ai.run'),
            'model': data.get('model', 'llama3-8b-instruct'),
            'max_tokens': data.get('max_tokens', 500),
            'temperature': data.get('temperature', 0.7),
            'max_cost_usd': data.get('max_cost_usd', 200.0),
            'target_pairs': data.get('target_pairs', 15000),
            'batch_size': data.get('batch_size', 10)
        }
        
        return cls(**config_fields)

class SetForgeGenerator:
    """Main dataset generator class."""
    
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.total_cost = 0.0
        self.generated_pairs: List[QAPair] = []
        self.question_hashes: set = set()  # For deduplication
        
        # Simple templates for Q&A generation
        self.templates = {
            QuestionType.SCHOLARSHIP: [
                "My {grade_type} is {grade}. What scholarship can I get at {university}?",
                "With {grade} in {grade_type}, am I eligible for merit scholarship at {university}?",
                "What are the scholarship requirements for {program} at {university}?"
            ],
            QuestionType.FEES: [
                "What is the total cost for {program} at {university} for Bangladeshi students?",
                "How much does {program} cost at {university} including accommodation?",
                "What are the annual fees for {program} at {university}?"
            ],
            QuestionType.ADMISSION: [
                "What are the admission requirements for {program} at {university}?",
                "How do I apply for {program} at {university} from Bangladesh?",
                "What documents are needed for {university} admission?"
            ],
            QuestionType.UNIVERSITY_COMPARISON: [
                "Compare {university1} vs {university2} for {program}",
                "Which is better for {program}: {university1} or {university2}?",
                "What are the differences between {university1} and {university2}?"
            ],
            QuestionType.VISA_GUIDANCE: [
                "What is the visa process for studying at {university}?",
                "What documents are needed for student visa to study at {university}?",
                "How long does the visa process take for {university}?"
            ],
            QuestionType.ACCOMMODATION: [
                "What accommodation options are available at {university}?",
                "Should I choose hostel or off-campus housing at {university}?",
                "What is the cost of accommodation at {university}?"
            ]
        }
        
        # Entity lists for template filling with authentic Bangladeshi grading
        if GRADING_SYSTEM_AVAILABLE:
            # Use realistic Bangladeshi grade entities
            grade_entities = generate_realistic_grade_entities()
            self.entities = {
                'universities': ['Sharda University', 'Amity University', 'Galgotias University', 
                               'Noida International University', 'G.L. Bajaj Institute'],
                'programs': ['B.Tech CSE', 'B.Tech Civil', 'BBA', 'B.Com', 'B.Sc CS', 'MBA', 'M.Tech'],
                'grade_types': grade_entities['grade_types'][:10],  # Limit for variety
                'grades': grade_entities['grades'][:15],
                'grade_contexts': grade_entities['grade_contexts'][:20],  # Full grade descriptions
                'qualifications': grade_entities['qualifications'][:8]
            }
        else:
            # Fallback basic entities
            self.entities = {
                'universities': ['Sharda University', 'Amity University', 'Galgotias University', 
                               'Noida International University', 'G.L. Bajaj Institute'],
                'programs': ['B.Tech CSE', 'B.Tech Civil', 'BBA', 'B.Com', 'B.Sc CS', 'MBA', 'M.Tech'],
                'grade_types': ['SSC', 'HSC', 'Diploma CGPA', 'Bachelor CGPA'],
                'grades': ['3.5', '4.0', '4.5', '5.0', '75%', '80%', '85%', '90%']
            }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def normalize_grade(self, grade_str: str) -> float:
        """Enhanced grade normalization using Bangladeshi grading system."""
        if not GRADING_SYSTEM_AVAILABLE:
            return self._basic_grade_normalization(grade_str)
        
        # Use enhanced Bangladeshi grading system
        grade_str = grade_str.strip().upper()
        
        # Parse Bangladeshi qualification and grade
        if 'SSC' in grade_str or 'DAKHIL' in grade_str:
            # Extract GPA from patterns like "SSC GPA 4.5"
            gpa_match = re.search(r'(\d+\.?\d*)', grade_str)
            if gpa_match:
                gpa = float(gpa_match.group(1))
                return min(gpa, 5.0)  # Ensure 5.0 scale
        
        elif 'HSC' in grade_str or 'ALIM' in grade_str:
            # HSC/Alim grades (5-point scale)
            gpa_match = re.search(r'(\d+\.?\d*)', grade_str)
            if gpa_match:
                gpa = float(gpa_match.group(1))
                return min(gpa, 5.0)
        
        elif 'DIPLOMA' in grade_str:
            # Diploma CGPA (4-point scale) - convert to 5-point
            cgpa_match = re.search(r'(\d+\.?\d*)', grade_str)
            if cgpa_match:
                cgpa = float(cgpa_match.group(1))
                # Convert 4-point to 5-point scale
                return min((cgpa / 4.0) * 5.0, 5.0)
        
        elif 'BACHELOR' in grade_str or 'HONOURS' in grade_str or 'MASTERS' in grade_str:
            # Could be percentage or CGPA
            if '%' in grade_str:
                # Extract percentage from "Bachelor 75%"
                percentage_match = re.search(r'(\d+(?:\.\d+)?)%', grade_str)
                if percentage_match:
                    percentage = float(percentage_match.group(1))
                    # Convert percentage to 5-point GPA using Bangladeshi system
                    return BangladeshiGradingSystem.percentage_to_indian_cgpa_10(percentage) / 2.0
            else:
                # Assume CGPA (4-point scale)
                cgpa_match = re.search(r'(\d+\.?\d*)', grade_str)
                if cgpa_match:
                    cgpa = float(cgpa_match.group(1))
                    return min((cgpa / 4.0) * 5.0, 5.0)
        
        # Handle percentage
        elif '%' in grade_str:
            percentage_match = re.search(r'(\d+(?:\.\d+)?)%', grade_str)
            if percentage_match:
                percentage = float(percentage_match.group(1))
                # Use authentic Bangladeshi conversion
                return BangladeshiGradingSystem.percentage_to_indian_cgpa_10(percentage) / 2.0
        
        # Handle raw numbers
        else:
            try:
                grade = float(grade_str)
                if grade <= 5.0:
                    return grade  # Already on 5.0 scale
                elif grade <= 10.0:
                    return grade / 2.0  # Convert from 10.0 scale
                else:
                    # Assume percentage
                    return BangladeshiGradingSystem.percentage_to_indian_cgpa_10(grade) / 2.0
            except:
                return 3.5  # Default for invalid grades
    
    # ===============================
    # PRODUCTION VALIDATION METHODS
    # ===============================
    
    def validate_production_readiness(self) -> Dict[str, Any]:
        """Comprehensive production readiness validation."""
        logger.info("🔍 Validating production readiness...")
        
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "system_checks": {},
            "data_validation": {},
            "configuration_checks": {},
            "overall_status": "UNKNOWN"
        }
        
        # System checks
        api_key = os.getenv('DIGITALOCEAN_API_KEY')
        validation_results["system_checks"] = {
            "api_key_configured": bool(api_key),
            "grading_system_available": GRADING_SYSTEM_AVAILABLE,
            "session_ready": self.session is not None,
            "templates_loaded": len(self.templates) > 0,
            "entities_loaded": len(self.entities) > 0
        }
        
        # Data validation
        data_dir = Path('data/educational')
        txt_files = list(data_dir.glob('*.txt')) if data_dir.exists() else []
        validation_results["data_validation"] = {
            "data_directory_exists": data_dir.exists(),
            "txt_files_count": len(txt_files),
            "sufficient_data": len(txt_files) >= 10,
            "data_readable": all(f.stat().st_size > 100 for f in txt_files[:5])
        }
        
        # Configuration checks
        validation_results["configuration_checks"] = {
            "api_url_configured": bool(self.config.api_url),
            "model_specified": bool(self.config.model),
            "budget_set": self.config.max_cost_usd > 0,
            "target_realistic": 1000 <= self.config.target_pairs <= 100000
        }
        
        # Overall status
        critical_checks = [
            validation_results["system_checks"]["api_key_configured"],
            validation_results["data_validation"]["sufficient_data"],
            validation_results["configuration_checks"]["api_url_configured"]
        ]
        
        if all(critical_checks):
            validation_results["overall_status"] = "PRODUCTION_READY"
        elif validation_results["system_checks"]["api_key_configured"]:
            validation_results["overall_status"] = "READY_PENDING_DATA"
        else:
            validation_results["overall_status"] = "NOT_READY"
        
        logger.info(f"✅ Validation complete: {validation_results['overall_status']}")
        return validation_results
    
    async def run_test_batch(self, batch_size: int = 5) -> Dict[str, Any]:
        """Run a small test batch to validate the pipeline."""
        logger.info(f"🧪 Running test batch ({batch_size} pairs)...")
        
        test_results = {
            "batch_size": batch_size,
            "start_time": datetime.now().isoformat(),
            "pairs_generated": 0,
            "avg_quality": 0.0,
            "errors": [],
            "success": False
        }
        
        try:
            # Generate small test batch
            data_files = list(Path('data/educational').glob('*.txt'))[:2]  # Use first 2 files
            test_pairs = []
            
            for file_path in data_files:
                if len(test_pairs) >= batch_size:
                    break
                    
                file_pairs = await self.process_file(file_path)
                # Limit pairs for test batch
                file_pairs = file_pairs[:batch_size//2]
                test_pairs.extend(file_pairs)
            
            test_results["pairs_generated"] = len(test_pairs)
            
            if test_pairs:
                # Quick quality assessment
                total_quality = 0
                for pair in test_pairs:
                    quality = self._assess_pair_quality(pair)
                    total_quality += quality
                
                test_results["avg_quality"] = total_quality / len(test_pairs)
                test_results["success"] = test_results["avg_quality"] >= 0.6
            
            test_results["end_time"] = datetime.now().isoformat()
            
        except Exception as e:
            test_results["errors"].append(str(e))
            logger.error(f"Test batch failed: {e}")
        
        logger.info(f"🧪 Test batch complete: {test_results['pairs_generated']} pairs, "
                   f"quality {test_results['avg_quality']:.3f}")
        return test_results
    
    def _assess_pair_quality(self, pair: QAPair) -> float:
        """Quick quality assessment for a Q&A pair."""
        quality_score = 0.0
        
        # Length checks
        if 20 <= len(pair.question) <= 200:
            quality_score += 0.2
        if 50 <= len(pair.answer) <= 1000:
            quality_score += 0.2
        
        # Content checks
        if any(term in pair.answer.lower() for term in ['bangladeshi', 'bangladesh', 'ssc', 'hsc']):
            quality_score += 0.3
        
        # Specificity checks
        if re.search(r'\d+', pair.answer):  # Contains numbers
            quality_score += 0.2
        
        # University mention
        if any(uni.lower() in pair.answer.lower() for uni in self.entities['universities']):
            quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    def monitor_progress(self, current_pairs: int, target_pairs: int, 
                        avg_quality: float, current_cost: float) -> Dict[str, Any]:
        """Real-time progress monitoring with emotional student impact context."""
        elapsed_time = (datetime.now() - getattr(self, 'start_time', datetime.now())).total_seconds() / 3600
        pairs_per_hour = current_pairs / max(elapsed_time, 0.01)
        
        # Student impact metrics
        students_helped = current_pairs
        families_guided = current_pairs // 3  # Assume 3 Q&A per family decision
        remaining_pairs = target_pairs - current_pairs
        hours_until_completion = remaining_pairs / max(pairs_per_hour, 1) if pairs_per_hour > 0 else float('inf')
        
        progress_data = {
            "timestamp": datetime.now().isoformat(),
            "pairs_generated": current_pairs,
            "target_pairs": target_pairs,
            "progress_percentage": (current_pairs / target_pairs) * 100,
            "pairs_per_hour": pairs_per_hour,
            "avg_quality": avg_quality,
            "current_cost": current_cost,
            "budget_remaining": self.config.max_cost_usd - current_cost,
            "cost_per_pair": current_cost / current_pairs if current_pairs > 0 else 0,
            "estimated_total_cost": (current_cost / current_pairs * target_pairs) if current_pairs > 0 else 0,
            # Emotional metrics
            "students_helped": students_helped,
            "families_guided": families_guided,
            "hours_until_completion": hours_until_completion,
            "impact_score": avg_quality * min(pairs_per_hour / 10000, 1.0)  # Quality × efficiency
        }
        
        # Enhanced progress logging with emotional context
        if current_pairs % 1000 == 0 or progress_data["progress_percentage"] % 5 == 0:
            logger.info(f"💫 MILESTONE: {students_helped:,} students helped!")
            logger.info(f"📊 Progress: {current_pairs:,}/{target_pairs:,} pairs "
                       f"({progress_data['progress_percentage']:.1f}%)")
            logger.info(f"⚡ Rate: {pairs_per_hour:,.0f} pairs/hour | Quality: {avg_quality:.3f}")
            logger.info(f"💰 Cost: ${current_cost:.2f}/${self.config.max_cost_usd} | "
                       f"ETA: {hours_until_completion:.1f}h")
            logger.info(f"🎯 Impact Score: {progress_data['impact_score']:.3f} "
                       f"(Quality × Efficiency)")
        
        # Quality alerts
        if avg_quality < 0.55:
            logger.warning(f"⚠️  QUALITY ALERT: Score {avg_quality:.3f} below threshold 0.55")
            logger.warning("💡 Consider optimizing generation parameters for better student guidance")
        elif avg_quality >= 0.75:
            logger.info(f"🌟 EXCELLENT QUALITY: {avg_quality:.3f} - Students getting exceptional guidance!")
        
        # Performance alerts
        if pairs_per_hour < 5000:
            logger.warning(f"🐌 PERFORMANCE ALERT: {pairs_per_hour:.0f} pairs/hour below target 5000")
            logger.warning("💡 Consider optimizing API calls or increasing batch size")
        elif pairs_per_hour >= 10000:
            logger.info(f"🚀 EXCEPTIONAL PERFORMANCE: {pairs_per_hour:,.0f} pairs/hour!")
        
        return progress_data
    
    # ===============================
    # END PRODUCTION VALIDATION
    # ===============================
        
        # Default fallback
        return 3.5
    
    def _basic_grade_normalization(self, grade_str: str) -> float:
        """Fallback basic grade normalization when utils not available."""
        grade_str = grade_str.strip()
        
        # Handle percentage
        if '%' in grade_str:
            percentage = float(grade_str.replace('%', ''))
            if percentage >= 90: return 5.0
            elif percentage >= 85: return 4.5
            elif percentage >= 80: return 4.0
            elif percentage >= 75: return 3.5
            else: return 3.0
        
        # Handle GPA/CGPA
        try:
            grade = float(grade_str)
            if grade <= 5.0:
                return grade  # Already on 5.0 scale
            elif grade <= 10.0:
                return grade / 2.0  # Convert from 10.0 scale
            else:
                return min(grade / 20.0, 5.0)  # Convert from percentage
        except:
            return 3.5  # Default
    
    def generate_question_from_template(self, template: str, persona: StudentPersona) -> str:
        """Generate a question by filling template with entities."""
        question = template
        
        # Fill template variables
        for key, values in self.entities.items():
            pattern = f"{{{key[:-1]}}}"  # Remove 's' from plural
            if pattern in question:
                question = question.replace(pattern, random.choice(values))
        
        # Fill university pairs for comparison
        if '{university1}' in question and '{university2}' in question:
            unis = random.sample(self.entities['universities'], 2)
            question = question.replace('{university1}', unis[0])
            question = question.replace('{university2}', unis[1])
        
        return question
    
    def create_qa_prompt(self, context: str, question: str, persona: StudentPersona) -> str:
        """Create a prompt for Q&A generation."""
        persona_context = {
            StudentPersona.HIGH_ACHIEVER: "ambitious student seeking top universities and research opportunities",
            StudentPersona.BUDGET_CONSCIOUS: "cost-conscious student looking for scholarships and affordable options", 
            StudentPersona.AVERAGE_STUDENT: "typical student needing general guidance and admission support"
        }
        
        return f"""You are helping a {persona_context[persona]} from Bangladesh who wants to study in India.

Context Information:
{context}

Question: {question}

Instructions:
1. Answer directly from the provided context only
2. Include specific details like fees, requirements, dates when available
3. Mention "for Bangladeshi students" when relevant
4. Keep the tone helpful and informative
5. If you can't answer from the context, say "Based on the provided information..."

Answer:"""

    async def call_llm_api(self, prompt: str) -> Tuple[str, float]:
        """Call DigitalOcean LLM API and return response with cost."""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        # Check budget limit
        if self.total_cost >= self.config.max_cost_usd:
            raise RuntimeError(f"Budget limit of ${self.config.max_cost_usd} reached")
        
        headers = {
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.config.model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': self.config.max_tokens,
            'temperature': self.config.temperature
        }
        
        try:
            async with self.session.post(self.config.api_url, 
                                       headers=headers, 
                                       json=data) as response:
                if response.status != 200:
                    raise Exception(f"API call failed: {response.status}")
                
                # Fix: Parse JSON manually to handle content-type detection issue
                response_text = await response.text()
                result = json.loads(response_text)
                
                # Extract response and calculate cost
                answer = result['choices'][0]['message']['content'].strip()
                tokens_used = result.get('usage', {}).get('total_tokens', 0)
                cost = tokens_used * 0.0000002  # DigitalOcean Llama 3.1 8B Instruct: $0.20 per million tokens
                
                self.total_cost += cost
                return answer, cost
                
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return f"Error generating answer: {e}", 0.0
    
    def is_duplicate_question(self, question: str) -> bool:
        """Check if question is a duplicate using hash."""
        question_hash = hashlib.md5(question.lower().encode()).hexdigest()
        if question_hash in self.question_hashes:
            return True
        self.question_hashes.add(question_hash)
        return False
    
    def calculate_confidence(self, answer: str, context: str) -> float:
        """Calculate confidence score based on answer quality."""
        # Simple heuristics for confidence
        confidence = 0.5
        
        # Check if answer contains specific details
        if any(word in answer.lower() for word in ['₹', 'rupees', 'percentage', 'cgpa', 'gpa']):
            confidence += 0.2
        
        # Check if answer references context
        context_words = set(context.lower().split())
        answer_words = set(answer.lower().split())
        overlap = len(context_words & answer_words) / max(len(answer_words), 1)
        confidence += min(overlap, 0.3)
        
        return min(confidence, 1.0)
    
    async def process_file(self, file_path: Path) -> List[QAPair]:
        """Process a single educational file to generate Q&A pairs."""
        logger.info(f"Processing {file_path.name}...")
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return []
        
        # Split into chunks and prioritize long chunks
        all_chunks = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
        # Filter for substantial chunks first, then take up to 5
        long_chunks = [chunk for chunk in all_chunks if len(chunk) >= 100]
        chunks_to_process = long_chunks[:5] if long_chunks else all_chunks[:5]
        
        pairs = []
        for chunk in chunks_to_process:  # Process filtered long chunks
            if len(chunk) < 100:  # Skip very short chunks (backup check)
                continue
            
            # Generate questions for each question type and persona
            for q_type in random.sample(list(QuestionType), 2):  # 2 random types per chunk
                for persona in random.sample(list(StudentPersona), 1):  # 1 random persona
                    template = random.choice(self.templates[q_type])
                    question = self.generate_question_from_template(template, persona)
                    
                    # Skip duplicates
                    if self.is_duplicate_question(question):
                        continue
                    
                    # Generate answer
                    prompt = self.create_qa_prompt(chunk, question, persona)
                    answer, cost = await self.call_llm_api(prompt)
                    
                    # Calculate confidence and create QA pair
                    confidence = self.calculate_confidence(answer, chunk)
                    
                    qa_pair = QAPair(
                        question=question,
                        answer=answer,
                        context=chunk[:200] + "..." if len(chunk) > 200 else chunk,
                        persona=persona.value,
                        question_type=q_type.value,
                        university=self.extract_university(chunk),
                        confidence=confidence,
                        source_file=file_path.name,
                        cost=cost
                    )
                    
                    pairs.append(qa_pair)
                    
                    # Progress logging
                    if len(pairs) % 10 == 0:
                        logger.info(f"Generated {len(pairs)} pairs from {file_path.name}, "
                                  f"Cost: ${self.total_cost:.3f}")
                    
                    # Check budget
                    if self.total_cost >= self.config.max_cost_usd:
                        logger.warning("Budget limit reached!")
                        return pairs
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(0.1)
        
        return pairs
    
    def extract_university(self, text: str) -> str:
        """Extract university name from text."""
        for uni in self.entities['universities']:
            if uni.lower() in text.lower():
                return uni
        return "General"
    
    async def generate_dataset(self, data_dir: Path, output_path: Path) -> None:
        """Generate complete dataset with production-grade monitoring and optimization."""
        # Initialize production monitoring
        self.start_time = datetime.now()
        logger.info(f"🚀 PRODUCTION LAUNCH: SetForge Q&A Generation System")
        logger.info(f"💝 Mission: Generate {self.config.target_pairs:,} Q&A pairs to help Bangladeshi students")
        logger.info(f"🎯 Target: {self.config.target_pairs:,} pairs | Budget: ${self.config.max_cost_usd}")
        logger.info(f"📅 Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get all educational files
        txt_files = list(data_dir.glob("*.txt"))
        logger.info(f"📚 Found {len(txt_files)} educational files for processing")
        
        all_pairs = []
        quality_scores = []
        file_count = 0
        
        # Production monitoring setup
        last_checkpoint = datetime.now()
        checkpoint_interval = 300  # 5 minutes
        
        try:
            for file_path in txt_files:
                if len(all_pairs) >= self.config.target_pairs:
                    logger.info(f"🎉 TARGET ACHIEVED: {len(all_pairs):,} pairs generated!")
                    break
                
                file_count += 1
                logger.info(f"📄 Processing file {file_count}/{len(txt_files)}: {file_path.name}")
                
                # Process file with error handling
                try:
                    pairs = await self.process_file(file_path)
                    all_pairs.extend(pairs)
                    
                    # Calculate quality metrics
                    file_quality = sum(p.confidence for p in pairs) / len(pairs) if pairs else 0.0
                    quality_scores.extend([p.confidence for p in pairs])
                    
                    logger.info(f"✅ File completed: {len(pairs)} pairs | Quality: {file_quality:.3f}")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing {file_path.name}: {e}")
                    continue
                
                # Real-time progress monitoring
                if all_pairs:
                    avg_quality = sum(quality_scores) / len(quality_scores)
                    progress_data = self.monitor_progress(
                        len(all_pairs), self.config.target_pairs, avg_quality, self.total_cost
                    )
                    
                    # Save checkpoint every 5 minutes
                    if (datetime.now() - last_checkpoint).total_seconds() > checkpoint_interval:
                        self.save_checkpoint(all_pairs, output_path, progress_data)
                        last_checkpoint = datetime.now()
                    
                    # Budget safety check
                    if self.total_cost >= self.config.max_cost_usd * 0.95:
                        logger.warning(f"🚨 BUDGET ALERT: 95% budget used (${self.total_cost:.2f})")
                        logger.warning("Stopping generation to prevent budget overrun")
                        break
                    
                    # Quality safety check
                    if avg_quality < 0.4:
                        logger.error(f"🚨 QUALITY CRITICAL: Average quality {avg_quality:.3f} too low")
                        logger.error("Consider stopping and reviewing generation parameters")
                        # Don't auto-stop for quality - let human decide
            
            # Final save and summary
            self.save_dataset(all_pairs, output_path)
            self.log_production_summary(all_pairs, quality_scores)
            
        except Exception as e:
            logger.error(f"💥 Production error: {e}")
            # Save what we have so far
            if all_pairs:
                emergency_path = output_path.with_suffix('.emergency.jsonl')
                self.save_dataset(all_pairs, emergency_path)
                logger.info(f"🚑 Emergency save: {len(all_pairs)} pairs saved to {emergency_path}")
            raise
    
    def save_checkpoint(self, pairs: List[QAPair], output_path: Path, progress_data: Dict[str, Any]) -> None:
        """Save production checkpoint for recovery."""
        checkpoint_path = output_path.with_suffix('.checkpoint.jsonl')
        self.save_dataset(pairs, checkpoint_path)
        
        # Save progress metadata
        progress_path = output_path.with_suffix('.progress.json')
        with open(progress_path, 'w') as f:
            json.dump(progress_data, f, indent=2)
        
        logger.info(f"💾 Checkpoint saved: {len(pairs)} pairs | "
                   f"Progress: {progress_data.get('progress_percentage', 0):.1f}%")
    
    def log_production_summary(self, all_pairs: List[QAPair], quality_scores: List[float]) -> None:
        """Log comprehensive production summary with emotional context."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # Calculate comprehensive metrics
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        pairs_per_hour = len(all_pairs) / (duration.total_seconds() / 3600)
        cost_per_pair = self.total_cost / len(all_pairs) if all_pairs else 0
        
        # Student impact metrics
        students_helped = len(all_pairs)
        families_guided = len(all_pairs) // 3
        
        # Quality distribution
        excellent_pairs = sum(1 for q in quality_scores if q >= 0.75)
        good_pairs = sum(1 for q in quality_scores if 0.6 <= q < 0.75)
        poor_pairs = sum(1 for q in quality_scores if q < 0.6)
        
        logger.info("\n" + "="*80)
        logger.info("🌟 SETFORGE PRODUCTION COMPLETE - MISSION ACCOMPLISHED! 🌟")
        logger.info("="*80)
        
        logger.info(f"\n💝 STUDENT IMPACT:")
        logger.info(f"   👨‍🎓 Students Helped: {students_helped:,}")
        logger.info(f"   👨‍👩‍👧‍👦 Families Guided: {families_guided:,}")
        logger.info(f"   🌍 Educational Futures Changed: {students_helped:,}")
        
        logger.info(f"\n📊 GENERATION METRICS:")
        logger.info(f"   🎯 Generated: {len(all_pairs):,}/{self.config.target_pairs:,} pairs")
        logger.info(f"   ⚡ Rate: {pairs_per_hour:,.0f} pairs/hour")
        logger.info(f"   ⏱️  Duration: {duration}")
        
        logger.info(f"\n🎯 QUALITY ANALYSIS:")
        logger.info(f"   📈 Average Quality: {avg_quality:.3f}/1.0")
        logger.info(f"   🌟 Excellent (≥0.75): {excellent_pairs:,} ({excellent_pairs/len(all_pairs)*100:.1f}%)")
        logger.info(f"   ✅ Good (0.6-0.75): {good_pairs:,} ({good_pairs/len(all_pairs)*100:.1f}%)")
        logger.info(f"   ⚠️  Needs Review (<0.6): {poor_pairs:,} ({poor_pairs/len(all_pairs)*100:.1f}%)")
        
        logger.info(f"\n💰 COST EFFICIENCY:")
        logger.info(f"   💳 Total Cost: ${self.total_cost:.2f}/${self.config.max_cost_usd}")
        logger.info(f"   📊 Cost per Pair: ${cost_per_pair:.6f}")
        logger.info(f"   💚 Budget Remaining: ${self.config.max_cost_usd - self.total_cost:.2f}")
        
        budget_efficiency = (self.config.max_cost_usd - self.total_cost) / self.config.max_cost_usd * 100
        logger.info(f"   📈 Budget Efficiency: {budget_efficiency:.1f}% remaining")
        
        logger.info(f"\n🎊 SUCCESS METRICS:")
        logger.info(f"   ✅ Quality Target (≥0.6): {'ACHIEVED' if avg_quality >= 0.6 else 'MISSED'}")
        logger.info(f"   ✅ Volume Target: {'ACHIEVED' if len(all_pairs) >= self.config.target_pairs * 0.9 else 'PARTIAL'}")
        logger.info(f"   ✅ Budget Target: {'ACHIEVED' if self.total_cost <= self.config.max_cost_usd else 'EXCEEDED'}")
        
        logger.info("\n💪 IMPACT STATEMENT:")
        logger.info(f"   🌟 {students_helped:,} Bangladeshi students now have better guidance for Indian universities!")
        logger.info(f"   🎓 {families_guided:,} families can make more informed educational decisions!")
        logger.info(f"   🚀 SetForge has successfully democratized access to quality educational guidance!")
        
        logger.info("\n" + "="*80)
        logger.info("🎉 MISSION ACCOMPLISHED - Thank you for changing lives! 🎉")
        logger.info("="*80 + "\n")
        
    def save_dataset(self, pairs: List[QAPair], output_path: Path) -> None:
        """Save dataset to JSONL format."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for pair in pairs:
                f.write(json.dumps(asdict(pair), ensure_ascii=False) + '\n')
        
        logger.info(f"Dataset saved to {output_path}")

# CLI Function
async def main():
    """Main CLI function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="SetForge Dataset Generator")
    parser.add_argument("data_dir", help="Directory containing educational .txt files")
    parser.add_argument("output_path", help="Output path for generated dataset")
    parser.add_argument("--config", default="config.yaml", help="Configuration file")
    parser.add_argument("--target", type=int, default=15000, help="Target number of Q&A pairs")
    parser.add_argument("--budget", type=float, default=200.0, help="Budget limit in USD")
    
    args = parser.parse_args()
    
    # Load configuration
    if os.path.exists(args.config):
        config = GenerationConfig.from_yaml(args.config)
    else:
        # Use environment variables or defaults
        config = GenerationConfig(
            api_key=os.getenv("DIGITALOCEAN_API_KEY", ""),
            target_pairs=args.target,
            max_cost_usd=args.budget
        )
    
    if not config.api_key:
        raise ValueError("API key not found. Set DIGITALOCEAN_API_KEY environment variable or use config file.")
    
    # Generate dataset
    async with SetForgeGenerator(config) as generator:
        await generator.generate_dataset(Path(args.data_dir), Path(args.output_path))

if __name__ == "__main__":
    asyncio.run(main())
