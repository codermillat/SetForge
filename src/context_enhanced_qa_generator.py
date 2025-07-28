"""
Context-Enhanced QA Generator for Educational Data Analysis
Implements context-rich prompt engineering for creating high-quality Q&A datasets
for Bangladeshi students seeking university admission guidance in India.
"""

import asyncio
import json
import logging
import re
import time
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

import aiohttp
from config import Config
from text_processor import TextChunk
from qa_generator import QAGenerator, QAPair


class ContextType(Enum):
    """Types of context to be preserved in Q&A generation."""
    UNIVERSITY = "university"
    ACADEMIC_LEVEL = "academic_level"
    PROGRAM = "program"
    STUDENT_BACKGROUND = "student_background"
    TIMELINE = "timeline"
    AUDIENCE = "audience"
    URGENCY = "urgency"
    COMPLEXITY = "complexity"


@dataclass
class ContextMetadata:
    """Metadata for context-rich Q&A generation."""
    universities: List[str] = field(default_factory=list)
    academic_levels: List[str] = field(default_factory=list)
    programs: List[str] = field(default_factory=list)
    student_background: str = "bangladeshi_students"
    timeline: str = "2025-26"
    audience: List[str] = field(default_factory=lambda: ["students", "parents"])
    urgency_level: str = "important"
    complexity_level: str = "moderate"
    content_type: str = "general"
    source_file: str = ""


@dataclass
class ContextualQAPair(QAPair):
    """Extended QA pair with comprehensive context information."""
    university_context: List[str] = field(default_factory=list)
    academic_level_context: List[str] = field(default_factory=list)
    program_context: List[str] = field(default_factory=list)
    student_background_context: str = "bangladeshi_students"
    timeline_context: str = "2025-26"
    audience_context: List[str] = field(default_factory=lambda: ["students", "parents"])
    urgency_context: str = "important"
    complexity_context: str = "moderate"
    multilingual_keywords: List[str] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)
    context_completeness_score: float = 0.0


class ContextEnhancedQAGenerator(QAGenerator):
    """Enhanced QA Generator with context-rich prompt engineering."""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.context_patterns = self._init_context_patterns()
        self.multilingual_terms = self._init_multilingual_terms()
        self._init_context_aware_prompts()
    
    def _init_context_patterns(self) -> Dict[str, List[str]]:
        """Initialize context detection patterns."""
        return {
            "universities": [
                r"Sharda\s+University", r"Amity\s+University", r"Galgotias\s+University",
                r"G\.L\.\s+Bajaj", r"Noida\s+International\s+University", r"NIU"
            ],
            "academic_levels": [
                r"SSC", r"HSC", r"Class\s+10", r"Class\s+12", r"Diploma",
                r"Bachelor'?s?", r"Master'?s?", r"PhD", r"Undergraduate", r"Postgraduate"
            ],
            "programs": [
                r"B\.Tech\s+(?:CSE|IT|ECE|EEE|ME|Civil|Biotech)",
                r"BCA", r"BBA", r"B\.Com", r"B\.Sc", r"MBA", r"M\.Tech",
                r"Computer\s+Science", r"Information\s+Technology",
                r"Electronics", r"Mechanical", r"Civil\s+Engineering"
            ],
            "processes": [
                r"admission\s+process", r"visa\s+application", r"FRRO\s+registration",
                r"lateral\s+entry", r"scholarship\s+application", r"fee\s+payment"
            ],
            "financial_terms": [
                r"tuition\s+fee", r"scholarship", r"total\s+cost", r"₹[\d,]+",
                r"annual\s+fee", r"semester\s+fee", r"hostel\s+fee"
            ],
            "timeline_markers": [
                r"2025-26", r"academic\s+year", r"July\s+intake", r"January\s+intake",
                r"application\s+deadline", r"session"
            ]
        }
    
    def _init_multilingual_terms(self) -> Dict[str, str]:
        """Initialize Bengali-English term mappings."""
        return {
            "শিক্ষার্থী": "student",
            "বিশ্ববিদ্যালয়": "university",
            "ভর্তি": "admission",
            "বৃত্তি": "scholarship",
            "শিক্ষা": "education",
            "ডিগ্রি": "degree",
            "কোর্স": "course",
            "ফি": "fee",
            "খরচ": "cost",
            "ভিসা": "visa"
        }
    
    def _init_context_aware_prompts(self):
        """Initialize context-aware prompt templates."""
        
        self.context_aware_system_prompt = """You are an expert educational guidance specialist for Bangladeshi students seeking university admission in India. Your task is to generate comprehensive, context-rich question-answer pairs that provide complete guidance.

CRITICAL CONTEXT REQUIREMENTS:
1. UNIVERSITY CONTEXT: Always specify which university(s) the information applies to (Sharda, Amity, Galgotias, G.L. Bajaj, NIU)
2. ACADEMIC LEVEL CONTEXT: Always specify education level (SSC/HSC/Diploma/Bachelor's/Master's)
3. PROGRAM CONTEXT: Always specify exact program (B.Tech CSE, BCA, BBA, etc.)
4. STUDENT BACKGROUND: Always specify "for Bangladeshi students"
5. TIMELINE CONTEXT: Always specify "for 2025-26 academic year"
6. AUDIENCE CONTEXT: Always specify target audience (students/parents/agents)

EXTRACTIVE REQUIREMENTS:
1. All answers must be DIRECTLY extracted from source text with full context preservation
2. Use exact wording from source with proper context specification
3. NO additions, interpretations, or inferences beyond the source
4. Maintain context clarity throughout the answer
5. Ensure traceability to specific source sentences with context

FORBIDDEN:
- Generic answers without context specification
- Information not explicitly stated in source
- Context-ambiguous statements
- Assumptions about unstated context
- Phrases like "generally", "usually", "typically" without source context

REQUIRED CONTEXT ELEMENTS IN EVERY Q&A:
- University: Which specific university(s)
- Program: Which specific program/course
- Student Type: "Bangladeshi students" specification
- Academic Level: HSC/Diploma/Bachelor's level
- Timeline: "2025-26 academic year" specification
- Audience: Who the answer is for (students/parents)

MULTILINGUAL SUPPORT:
- Include Bengali terms where culturally relevant
- Explain Indian education system terms for Bangladeshi context
- Use "বাংলাদেশি শিক্ষার্থী" when appropriate
"""

        self.context_extraction_prompt = """Generate {num_questions} context-rich, comprehensive question-answer pairs from the educational guidance text below.

SOURCE TEXT:
```
{source_text}
```

CONTEXT METADATA:
- Universities: {universities}
- Academic Levels: {academic_levels}
- Programs: {programs}
- Student Background: {student_background}
- Timeline: {timeline}
- Content Type: {content_type}
- Source File: {source_file}

MANDATORY CONTEXT SPECIFICATIONS FOR ALL Q&A:
1. University Context: Specify which university(s) - {universities}
2. Academic Level: Specify education level (SSC/HSC/Diploma/Bachelor's/Master's)
3. Program Context: Specify exact program (B.Tech CSE, BCA, BBA, etc.)
4. Student Background: Always include "for Bangladeshi students"
5. Timeline: Always include "for 2025-26 academic year"
6. Audience: Specify who the answer is for (students/parents/agents)

QUESTION TYPES TO GENERATE WITH FULL CONTEXT:
1. Direct Information: "What is the annual tuition fee for B.Tech CSE at Sharda University for Bangladeshi students in 2025-26?"
2. Process Steps: "What is the complete admission process for Bangladeshi HSC graduates applying to B.Tech at Sharda University for 2025-26?"
3. Comparative: "Which university offers better B.Tech CSE programs for Bangladeshi students: Sharda or Amity for 2025-26?"
4. Eligibility: "What are the eligibility requirements for Bangladeshi diploma holders to apply for lateral entry to B.Tech at Sharda University?"
5. Financial: "What is the total 4-year cost for B.Tech CSE at Sharda University for Bangladeshi students including all expenses for 2025-26?"
6. Practical: "How do Bangladeshi students open a bank account while studying B.Tech at Sharda University in India?"

ANSWER STRUCTURE WITH CONTEXT:
1. Direct Answer: Start with specific answer including full context
2. Context Specification: Clearly state which university, program, student type
3. Supporting Details: Additional context-aware information from source
4. Practical Implications: What this means for Bangladeshi students specifically
5. Related Information: Connect to other relevant context-aware guidance

Each Q&A must include:
- University specification: "at [University Name]"
- Program specification: "for [Program Name]"
- Student specification: "for Bangladeshi students"
- Timeline specification: "for 2025-26 academic year"
- Audience specification: "students should know" or "parents should understand"

Return as JSON array with this structure:
```json
[
  {
    "question": "context-rich question with full specifications",
    "answer": "extractive answer with complete context preservation",
    "type": "question_type",
    "confidence": 0.0-1.0,
    "university_context": ["university_names"],
    "academic_level_context": ["levels"],
    "program_context": ["programs"],
    "student_background_context": "bangladeshi_students",
    "timeline_context": "2025-26",
    "audience_context": ["target_audience"],
    "multilingual_keywords": ["relevant_terms"],
    "context_completeness_score": 0.0-1.0
  }
]
```

Generate questions covering different context scenarios and ensure comprehensive coverage of the source material with full context preservation."""

        self.context_validation_prompt = """Validate that this Q&A pair includes complete context and is fully extractive.

SOURCE TEXT:
```
{source_text}
```

QUESTION: {question}
ANSWER: {answer}
CONTEXT METADATA: {context_metadata}

VALIDATION CRITERIA:
1. EXTRACTIVE VALIDATION: Is the answer completely extracted from source text?
2. CONTEXT COMPLETENESS: Does the Q&A include all required context elements?
3. UNIVERSITY CONTEXT: Is university context clearly specified?
4. PROGRAM CONTEXT: Is program/course context clearly specified?
5. STUDENT CONTEXT: Is "Bangladeshi students" context included?
6. TIMELINE CONTEXT: Is "2025-26 academic year" context included?
7. AUDIENCE CONTEXT: Is target audience clearly specified?

Return detailed validation:
```json
{
  "is_extractive": true/false,
  "context_completeness": 0.0-1.0,
  "university_context_clear": true/false,
  "program_context_clear": true/false,
  "student_context_clear": true/false,
  "timeline_context_clear": true/false,
  "audience_context_clear": true/false,
  "overall_quality_score": 0.0-1.0,
  "issues": ["list of specific problems"],
  "suggestions": ["improvement recommendations"]
}
```"""

        self.multilingual_enhancement_prompt = """Enhance this Q&A pair with multilingual support and cultural context for Bangladeshi students.

ORIGINAL Q&A:
Question: {question}
Answer: {answer}

ENHANCEMENT REQUIREMENTS:
1. Add Bengali terms where culturally relevant
2. Explain Indian education system terms for Bangladeshi context
3. Include cultural considerations for Bangladeshi students
4. Add transliteration for key terms
5. Maintain full context specification

Return enhanced version:
```json
{
  "enhanced_question": "question with multilingual elements",
  "enhanced_answer": "answer with cultural context and Bengali terms",
  "bengali_keywords": ["key terms in Bengali"],
  "cultural_notes": ["important cultural considerations"],
  "terminology_explanations": ["Indian system explanations for Bangladeshi context"]
}
```"""

    async def extract_context_metadata(self, chunk: TextChunk) -> ContextMetadata:
        """Extract context metadata from text chunk."""
        content = chunk.content.lower()
        
        # Extract universities
        universities = []
        for pattern in self.context_patterns["universities"]:
            matches = re.findall(pattern, content, re.IGNORECASE)
            universities.extend([match.strip() for match in matches])
        
        # Extract academic levels
        academic_levels = []
        for pattern in self.context_patterns["academic_levels"]:
            matches = re.findall(pattern, content, re.IGNORECASE)
            academic_levels.extend([match.strip() for match in matches])
        
        # Extract programs
        programs = []
        for pattern in self.context_patterns["programs"]:
            matches = re.findall(pattern, content, re.IGNORECASE)
            programs.extend([match.strip() for match in matches])
        
        # Determine content type from source file
        content_type = self._determine_content_type(chunk.source_file)
        
        # Extract timeline
        timeline = "2025-26"  # Default, but check for specific mentions
        for pattern in self.context_patterns["timeline_markers"]:
            if re.search(pattern, content, re.IGNORECASE):
                timeline = "2025-26"
                break
        
        return ContextMetadata(
            universities=list(set(universities)),
            academic_levels=list(set(academic_levels)),
            programs=list(set(programs)),
            student_background="bangladeshi_students",
            timeline=timeline,
            audience=["students", "parents"],
            content_type=content_type,
            source_file=chunk.source_file or ""
        )
    
    def _determine_content_type(self, filename: str) -> str:
        """Determine content type from filename."""
        if not filename:
            return "general"
        
        filename = filename.lower()
        
        if "fees" in filename or "scholarship" in filename:
            return "financial"
        elif "admission" in filename or "process" in filename:
            return "admission_process"
        elif "comparison" in filename or "comparative" in filename:
            return "comparative_analysis"
        elif "visa" in filename or "frro" in filename:
            return "legal_compliance"
        elif "hostel" in filename or "accommodation" in filename:
            return "accommodation"
        elif "campus" in filename or "life" in filename:
            return "campus_life"
        elif "career" in filename or "alumni" in filename:
            return "career_guidance"
        else:
            return "general"
    
    async def generate_context_rich_qa_pairs(self, chunk: TextChunk) -> List[ContextualQAPair]:
        """Generate context-rich QA pairs for a text chunk."""
        if not chunk.content.strip():
            return []
        
        self.logger.debug(f"Generating context-rich QA pairs for chunk: {chunk.id}")
        
        try:
            # Extract context metadata
            context_metadata = await self.extract_context_metadata(chunk)
            
            # Check cost limits
            if self.total_cost >= self.config.cost.max_total_cost_usd:
                self.logger.warning("Cost limit reached, skipping QA generation")
                return []
            
            # Generate context-rich QA pairs
            raw_qa_pairs = await self._call_context_aware_llm(chunk, context_metadata)
            
            # Convert to ContextualQAPair objects and validate
            validated_pairs = []
            for qa_data in raw_qa_pairs:
                if self._validate_context_rich_qa(qa_data, chunk.content, context_metadata):
                    contextual_pair = self._create_contextual_qa_pair(qa_data, chunk, context_metadata)
                    validated_pairs.append(contextual_pair)
            
            self.logger.info(f"Generated {len(validated_pairs)} context-rich QA pairs for chunk {chunk.id}")
            return validated_pairs
            
        except Exception as e:
            self.logger.error(f"Error generating context-rich QA pairs for chunk {chunk.id}: {e}")
            return []
    
    async def _call_context_aware_llm(self, chunk: TextChunk, context_metadata: ContextMetadata) -> List[Dict]:
        """Call LLM with context-aware prompts."""
        user_prompt = self.context_extraction_prompt.format(
            num_questions=self.config.qa.questions_per_chunk,
            source_text=chunk.content,
            universities=", ".join(context_metadata.universities) or "Various universities",
            academic_levels=", ".join(context_metadata.academic_levels) or "Multiple levels",
            programs=", ".join(context_metadata.programs) or "Various programs",
            student_background=context_metadata.student_background,
            timeline=context_metadata.timeline,
            content_type=context_metadata.content_type,
            source_file=context_metadata.source_file
        )
        
        response = await self._make_api_call(
            system_prompt=self.context_aware_system_prompt,
            user_prompt=user_prompt,
            max_tokens=self.config.llm.max_tokens
        )
        
        return self._parse_llm_response(response)
    
    def _validate_context_rich_qa(self, qa_data: Dict, source_text: str, context_metadata: ContextMetadata) -> bool:
        """Validate context-rich QA pair."""
        required_fields = ["question", "answer", "university_context", "program_context", 
                          "student_background_context", "timeline_context"]
        
        # Check required fields
        if not all(field in qa_data for field in required_fields):
            return False
        
        # Check context completeness
        question = qa_data.get("question", "").lower()
        answer = qa_data.get("answer", "").lower()
        
        # Validate university context
        if context_metadata.universities and not any(uni.lower() in question + answer for uni in context_metadata.universities):
            return False
        
        # Validate student background context
        if "bangladeshi" not in question + answer:
            return False
        
        # Validate timeline context
        if context_metadata.timeline not in question + answer:
            return False
        
        # Validate extractive nature
        answer_words = set(answer.split())
        source_words = set(source_text.lower().split())
        overlap_ratio = len(answer_words.intersection(source_words)) / len(answer_words)
        
        return overlap_ratio >= 0.7  # At least 70% word overlap
    
    def _create_contextual_qa_pair(self, qa_data: Dict, chunk: TextChunk, context_metadata: ContextMetadata) -> ContextualQAPair:
        """Create ContextualQAPair object from raw data."""
        return ContextualQAPair(
            question=qa_data.get("question", ""),
            answer=qa_data.get("answer", ""),
            chunk_id=chunk.id,
            source_text=chunk.content,
            question_type=qa_data.get("type", "contextual"),
            confidence_score=qa_data.get("confidence", 0.0),
            university_context=qa_data.get("university_context", []),
            academic_level_context=qa_data.get("academic_level_context", []),
            program_context=qa_data.get("program_context", []),
            student_background_context=qa_data.get("student_background_context", "bangladeshi_students"),
            timeline_context=qa_data.get("timeline_context", "2025-26"),
            audience_context=qa_data.get("audience_context", ["students", "parents"]),
            multilingual_keywords=qa_data.get("multilingual_keywords", []),
            related_concepts=qa_data.get("related_concepts", []),
            context_completeness_score=qa_data.get("context_completeness_score", 0.0),
            metadata={
                "source_file": chunk.source_file,
                "content_type": context_metadata.content_type,
                "universities": context_metadata.universities,
                "programs": context_metadata.programs,
                "academic_levels": context_metadata.academic_levels
            }
        )
    
    async def enhance_with_multilingual_support(self, qa_pair: ContextualQAPair) -> ContextualQAPair:
        """Enhance QA pair with multilingual support."""
        try:
            user_prompt = self.multilingual_enhancement_prompt.format(
                question=qa_pair.question,
                answer=qa_pair.answer
            )
            
            response = await self._make_api_call(
                system_prompt="You are a multilingual educational content specialist.",
                user_prompt=user_prompt,
                max_tokens=1024
            )
            
            enhancement_data = self._parse_llm_response(response)
            if enhancement_data and len(enhancement_data) > 0:
                enhancement = enhancement_data[0]
                
                # Update QA pair with multilingual enhancements
                qa_pair.question = enhancement.get("enhanced_question", qa_pair.question)
                qa_pair.answer = enhancement.get("enhanced_answer", qa_pair.answer)
                qa_pair.multilingual_keywords = enhancement.get("bengali_keywords", [])
                
                # Add cultural metadata
                qa_pair.metadata.update({
                    "cultural_notes": enhancement.get("cultural_notes", []),
                    "terminology_explanations": enhancement.get("terminology_explanations", [])
                })
            
            return qa_pair
            
        except Exception as e:
            self.logger.error(f"Error enhancing QA pair with multilingual support: {e}")
            return qa_pair
    
    async def generate_comparative_analysis_qa(self, chunks: List[TextChunk]) -> List[ContextualQAPair]:
        """Generate comparative analysis QA pairs across multiple chunks."""
        if len(chunks) < 2:
            return []
        
        comparative_qa_pairs = []
        
        try:
            # Extract context from all chunks
            all_contexts = []
            for chunk in chunks:
                context = await self.extract_context_metadata(chunk)
                all_contexts.append(context)
            
            # Combine universities and programs for comparison
            all_universities = set()
            all_programs = set()
            for context in all_contexts:
                all_universities.update(context.universities)
                all_programs.update(context.programs)
            
            # Generate comparative questions
            comparative_prompt = f"""Generate comparative question-answer pairs using the following educational content about different universities and programs for Bangladeshi students.

UNIVERSITIES TO COMPARE: {', '.join(all_universities)}
PROGRAMS TO COMPARE: {', '.join(all_programs)}

SOURCE CONTENT:
```
{' '.join([chunk.content for chunk in chunks[:3]])}  # Limit content for token efficiency
```

Generate {self.config.qa.questions_per_chunk} comparative questions such as:
1. "Which university offers better B.Tech CSE programs for Bangladeshi students: Sharda or Amity for 2025-26?"
2. "What are the fee differences between Sharda and Galgotias University for B.Tech programs for Bangladeshi students in 2025-26?"
3. "Which university provides better ROI for Bangladeshi B.Tech students: Sharda, Amity, or Galgotias?"

Each answer must be EXTRACTIVE from the source content and include full context specification.

Return as JSON array with the same structure as context-rich QA pairs."""

            response = await self._make_api_call(
                system_prompt=self.context_aware_system_prompt,
                user_prompt=comparative_prompt,
                max_tokens=self.config.llm.max_tokens
            )
            
            raw_qa_pairs = self._parse_llm_response(response)
            
            for qa_data in raw_qa_pairs:
                # Create comparative contextual QA pair
                contextual_pair = ContextualQAPair(
                    question=qa_data.get("question", ""),
                    answer=qa_data.get("answer", ""),
                    chunk_id="comparative_analysis",
                    source_text=" ".join([chunk.content for chunk in chunks]),
                    question_type="comparative",
                    confidence_score=qa_data.get("confidence", 0.0),
                    university_context=list(all_universities),
                    program_context=list(all_programs),
                    student_background_context="bangladeshi_students",
                    timeline_context="2025-26",
                    audience_context=["students", "parents"],
                    metadata={
                        "analysis_type": "comparative",
                        "source_chunks": len(chunks),
                        "universities_compared": list(all_universities),
                        "programs_compared": list(all_programs)
                    }
                )
                comparative_qa_pairs.append(contextual_pair)
            
            return comparative_qa_pairs
            
        except Exception as e:
            self.logger.error(f"Error generating comparative analysis QA: {e}")
            return []
