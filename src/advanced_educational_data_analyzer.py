"""
Advanced Educational Data Analyzer for Context-Rich Q&A Generation
Implements comprehensive analysis of 48 educational source files with complete 
context extraction, source attribution, and advanced prompt engineering patterns.
"""

import asyncio
import json
import logging
import re
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter

try:
    from .config import Config
    from .text_processor import TextProcessor, TextChunk
except ImportError:
    # Alternative import approaches
    try:
        from config import Config
        from text_processor import TextProcessor, TextChunk
    except ImportError:
        import sys
        from pathlib import Path
        # Add src directory to path for standalone execution
        src_dir = Path(__file__).parent
        if str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))
        try:
            from src.config import Config
            from src.text_processor import TextProcessor, TextChunk
        except ImportError:
            # Create minimal fallback classes
            class Config:
                def __init__(self):
                    pass
            
            class TextProcessor:
                def __init__(self, config=None):
                    pass
                
                async def process_text(self, text, file_path=""):
                    return []
            
            class TextChunk:
                def __init__(self, content, chunk_id=0):
                    self.content = content
                    self.chunk_id = chunk_id


class ContentCategory(Enum):
    """Educational content categories for systematic analysis."""
    UNIVERSITY_PROFILES = "university_profiles"
    ADMISSION_PROCESSES = "admission_processes"
    FINANCIAL_INFORMATION = "financial_information"
    COMPARATIVE_ANALYSIS = "comparative_analysis"
    ACADEMIC_PROGRAMS = "academic_programs"
    CAMPUS_LIFE = "campus_life"
    LEGAL_VISA = "legal_visa"
    PRACTICAL_GUIDANCE = "practical_guidance"
    TROUBLESHOOTING = "troubleshooting"
    SUPPORT_RESOURCES = "support_resources"


class ContextPriority(Enum):
    """Context priority levels for Q&A generation."""
    CRITICAL = "critical"      # Visa, fees, admission deadlines
    IMPORTANT = "important"    # Academic requirements, scholarships
    USEFUL = "useful"         # Campus life, cultural information
    REFERENCE = "reference"   # Glossary, contact information


@dataclass
class SourceAttribution:
    """Complete source attribution with verification metadata."""
    data_source_file: str
    original_source: str
    source_url: str
    verification_date: str
    source_type: str
    source_reliability: float = 1.0  # 0.0-1.0 reliability score
    currency_status: str = "current"  # current, outdated, needs_verification
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "data_source_file": self.data_source_file,
            "original_source": self.original_source,
            "source_url": self.source_url,
            "verification_date": self.verification_date,
            "source_type": self.source_type,
            "source_reliability": self.source_reliability,
            "currency_status": self.currency_status
        }


@dataclass
class ContextMetadata:
    """Comprehensive context metadata with mandatory elements."""
    # Mandatory context elements (100% compliance required)
    universities: Set[str] = field(default_factory=set)
    programs: Set[str] = field(default_factory=set)
    student_background: str = "bangladeshi_students"
    timeline: str = "2025-26"
    academic_levels: Set[str] = field(default_factory=set)
    audiences: Set[str] = field(default_factory=set)
    
    # Additional context elements
    content_category: ContentCategory = ContentCategory.PRACTICAL_GUIDANCE
    priority_level: ContextPriority = ContextPriority.USEFUL
    multilingual_keywords: Dict[str, str] = field(default_factory=dict)
    related_concepts: Set[str] = field(default_factory=set)
    financial_amounts: List[str] = field(default_factory=list)
    process_steps: List[str] = field(default_factory=list)
    
    # Source attribution
    source_attribution: Optional[SourceAttribution] = None
    
    def context_completeness_score(self) -> float:
        """Calculate context completeness score (0.0-1.0)."""
        required_elements = [
            bool(self.universities),
            bool(self.programs),
            self.student_background == "bangladeshi_students",
            self.timeline == "2025-26",
            bool(self.academic_levels),
            bool(self.audiences)
        ]
        return sum(required_elements) / len(required_elements)


@dataclass
class ContentPattern:
    """Pattern for extracting structured content."""
    name: str
    regex_patterns: List[str]
    context_type: str
    priority: ContextPriority
    examples: List[str] = field(default_factory=list)


@dataclass
class AdvancedAnalysisResult:
    """Comprehensive analysis result for educational content."""
    file_path: str
    content_category: ContentCategory
    context_metadata: ContextMetadata
    extracted_patterns: Dict[str, List[str]]
    quality_metrics: Dict[str, float]
    prompt_engineering_insights: Dict[str, Any]
    source_verification: Dict[str, Any]
    content_gaps: List[str]
    optimization_recommendations: List[str]
    processing_metadata: Dict[str, Any]


class AdvancedEducationalDataAnalyzer:
    """Advanced analyzer for educational data with comprehensive context extraction."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.text_processor = TextProcessor(self.config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize pattern detection systems
        self._init_content_patterns()
        self._init_context_extractors()
        self._init_multilingual_mappings()
        self._init_source_attribution_patterns()
        
        # Analysis tracking
        self.analysis_results: List[AdvancedAnalysisResult] = []
        self.global_insights: Dict[str, Any] = {}
        
    def _init_content_patterns(self):
        """Initialize comprehensive content pattern detection."""
        self.content_patterns = {
            # University identification patterns
            "universities": ContentPattern(
                name="universities",
                regex_patterns=[
                    r"Sharda\s+University",
                    r"Amity\s+University",
                    r"Galgotias\s+University",
                    r"G\.L\.\s+Bajaj\s+(?:Institute|College)",
                    r"Noida\s+International\s+University",
                    r"NIU"
                ],
                context_type="university_context",
                priority=ContextPriority.CRITICAL
            ),
            
            # Academic program patterns
            "programs": ContentPattern(
                name="programs",
                regex_patterns=[
                    r"B\.Tech\s+(?:CSE|Computer\s+Science|IT|Information\s+Technology)",
                    r"B\.Tech\s+(?:ECE|Electronics|EEE|Electrical)",
                    r"B\.Tech\s+(?:ME|Mechanical|Civil|Biotech)",
                    r"BCA", r"BBA", r"B\.Com", r"B\.Sc",
                    r"MBA", r"M\.Tech", r"PhD"
                ],
                context_type="program_context",
                priority=ContextPriority.CRITICAL
            ),
            
            # Academic level patterns
            "academic_levels": ContentPattern(
                name="academic_levels",
                regex_patterns=[
                    r"SSC|Class\s+10|Dakhil",
                    r"HSC|Class\s+12|Alim",
                    r"Diploma\s+(?:holders?|students?)",
                    r"(?:Bachelor'?s?|Undergraduate)",
                    r"(?:Master'?s?|Postgraduate)",
                    r"PhD|Doctorate"
                ],
                context_type="academic_level_context",
                priority=ContextPriority.IMPORTANT
            ),
            
            # Financial information patterns
            "financial_info": ContentPattern(
                name="financial_info",
                regex_patterns=[
                    r"₹[\d,]+(?:\s+(?:Lakhs?|per\s+year|annually))?",
                    r"tuition\s+fee",
                    r"scholarship\s+(?:of\s+)?(?:\d+%|\d+\s+percent)",
                    r"total\s+cost",
                    r"hostel\s+fee",
                    r"examination\s+fee"
                ],
                context_type="financial_context",
                priority=ContextPriority.CRITICAL
            ),
            
            # Process documentation patterns
            "processes": ContentPattern(
                name="processes",
                regex_patterns=[
                    r"admission\s+process",
                    r"application\s+procedure",
                    r"visa\s+(?:application|process)",
                    r"FRRO\s+registration",
                    r"lateral\s+entry",
                    r"scholarship\s+application"
                ],
                context_type="process_context",
                priority=ContextPriority.IMPORTANT
            ),
            
            # Timeline and deadline patterns
            "timelines": ContentPattern(
                name="timelines",
                regex_patterns=[
                    r"2025-26\s+academic\s+year",
                    r"July\s+intake",
                    r"January\s+intake",
                    r"application\s+deadline",
                    r"session\s+(?:starts?|begins?)"
                ],
                context_type="timeline_context",
                priority=ContextPriority.CRITICAL
            ),
            
            # Student background patterns
            "student_background": ContentPattern(
                name="student_background",
                regex_patterns=[
                    r"Bangladeshi\s+students?",
                    r"international\s+students?",
                    r"SAARC\s+students?",
                    r"students?\s+from\s+Bangladesh"
                ],
                context_type="student_background_context",
                priority=ContextPriority.CRITICAL
            )
        }
    
    def _init_context_extractors(self):
        """Initialize context extraction utilities."""
        self.context_extractors = {
            "audience_detection": {
                "students": [r"students?\s+(?:should|need|must|can)",
                           r"(?:if\s+)?you\s+(?:are\s+a\s+)?student"],
                "parents": [r"parents?\s+(?:should|need|must|can)",
                          r"guardian", r"family"],
                "agents": [r"agents?", r"counselors?", r"advisors?"]
            },
            
            "urgency_detection": {
                "critical": [r"urgent", r"deadline", r"must\s+be\s+done",
                           r"immediately", r"before\s+\d+"],
                "important": [r"important", r"should", r"recommended",
                            r"advised", r"suggested"],
                "useful": [r"helpful", r"useful", r"good\s+to\s+know",
                         r"additionally", r"also"]
            },
            
            "complexity_detection": {
                "simple": [r"simply", r"just", r"only", r"basic"],
                "moderate": [r"process", r"steps", r"procedure", r"requirements"],
                "complex": [r"comprehensive", r"detailed", r"complex",
                          r"multiple\s+steps", r"various\s+factors"]
            }
        }
    
    def _init_multilingual_mappings(self):
        """Initialize Bengali-English multilingual mappings."""
        self.multilingual_mappings = {
            "শিক্ষার্থী": "student",
            "বিশ্ববিদ্যালয়": "university", 
            "ভর্তি": "admission",
            "বৃত্তি": "scholarship",
            "শিক্ষা": "education",
            "ডিগ্রি": "degree",
            "কোর্স": "course",
            "ফি": "fee",
            "খরচ": "cost",
            "ভিসা": "visa",
            "পরীক্ষা": "exam",
            "ফলাফল": "result",
            "আবেদন": "application",
            "নথি": "document",
            "সার্টিফিকেট": "certificate"
        }
    
    def _init_source_attribution_patterns(self):
        """Initialize source attribution extraction patterns."""
        self.source_patterns = {
            "source_markers": [
                r"—source:\s*(.+?)(?:\n|$)",
                r"Source:\s*(.+?)(?:\n|$)",
                r"\[Source:\s*(.+?)\]"
            ],
            "url_patterns": [
                r"https?://[^\s]+",
                r"www\.[^\s]+",
                r"[a-zA-Z0-9.-]+\.(?:ac\.in|edu|org|com)"
            ],
            "document_types": [
                r"brochure", r"guideline", r"policy", r"handbook",
                r"manual", r"document", r"circular", r"notification"
            ]
        }
    
    async def analyze_educational_directory(self, directory_path: str) -> Dict[str, Any]:
        """Analyze entire educational directory with comprehensive insights."""
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        self.logger.info(f"Starting comprehensive analysis of {directory_path}")
        start_time = time.time()
        
        # Get all educational files
        educational_files = list(directory.glob("*.txt"))
        self.logger.info(f"Found {len(educational_files)} educational files")
        
        # Analyze each file
        analysis_tasks = [
            self.analyze_educational_file(str(file_path))
            for file_path in educational_files
        ]
        
        file_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        successful_analyses = []
        failed_analyses = []
        
        for i, result in enumerate(file_results):
            if isinstance(result, Exception):
                failed_analyses.append({
                    "file": str(educational_files[i]),
                    "error": str(result)
                })
                self.logger.error(f"Failed to analyze {educational_files[i]}: {result}")
            else:
                successful_analyses.append(result)
                self.analysis_results.append(result)
        
        # Generate comprehensive global insights
        global_insights = await self._generate_global_insights(successful_analyses)
        
        processing_time = time.time() - start_time
        
        return {
            "analysis_summary": {
                "total_files": len(educational_files),
                "successful_analyses": len(successful_analyses),
                "failed_analyses": len(failed_analyses),
                "processing_time_seconds": processing_time
            },
            "file_analyses": successful_analyses,
            "failed_analyses": failed_analyses,
            "global_insights": global_insights,
            "prompt_engineering_recommendations": await self._generate_prompt_recommendations(successful_analyses),
            "data_quality_assessment": await self._assess_data_quality(successful_analyses),
            "context_completeness_analysis": await self._analyze_context_completeness(successful_analyses),
            "source_attribution_analysis": await self._analyze_source_attribution(successful_analyses)
        }
    
    async def analyze_educational_file(self, file_path: str) -> AdvancedAnalysisResult:
        """Analyze individual educational file with comprehensive context extraction."""
        self.logger.info(f"Analyzing educational file: {file_path}")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract basic metadata
        file_name = Path(file_path).name
        content_category = self._categorize_content(file_name, content)
        
        # Process content into chunks
        chunks = await self.text_processor.process_text(content, file_path)
        
        # Extract comprehensive context metadata
        context_metadata = await self._extract_comprehensive_context(content, file_path)
        
        # Extract patterns and insights
        extracted_patterns = await self._extract_content_patterns(content)
        
        # Calculate quality metrics
        quality_metrics = await self._calculate_quality_metrics(content, context_metadata)
        
        # Generate prompt engineering insights
        prompt_insights = await self._generate_prompt_insights(content, context_metadata)
        
        # Verify source attribution
        source_verification = await self._verify_source_attribution(content)
        
        # Identify content gaps
        content_gaps = await self._identify_content_gaps(content, context_metadata)
        
        # Generate optimization recommendations
        optimization_recommendations = await self._generate_optimization_recommendations(
            content, context_metadata, quality_metrics
        )
        
        # Processing metadata
        processing_metadata = {
            "file_size_bytes": len(content.encode('utf-8')),
            "chunk_count": len(chunks),
            "analysis_timestamp": time.time(),
            "analyzer_version": "2.0.0"
        }
        
        return AdvancedAnalysisResult(
            file_path=file_path,
            content_category=content_category,
            context_metadata=context_metadata,
            extracted_patterns=extracted_patterns,
            quality_metrics=quality_metrics,
            prompt_engineering_insights=prompt_insights,
            source_verification=source_verification,
            content_gaps=content_gaps,
            optimization_recommendations=optimization_recommendations,
            processing_metadata=processing_metadata
        )
    
    async def _extract_comprehensive_context(self, content: str, file_path: str) -> ContextMetadata:
        """Extract comprehensive context metadata from content."""
        context = ContextMetadata()
        content_lower = content.lower()
        
        # Extract universities
        for pattern in self.content_patterns["universities"].regex_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            context.universities.update(match.strip() for match in matches)
        
        # Extract programs
        for pattern in self.content_patterns["programs"].regex_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            context.programs.update(match.strip() for match in matches)
        
        # Extract academic levels
        for pattern in self.content_patterns["academic_levels"].regex_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            context.academic_levels.update(match.strip() for match in matches)
        
        # Extract audiences
        for audience, patterns in self.context_extractors["audience_detection"].items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    context.audiences.add(audience)
        
        # Extract multilingual keywords
        for bengali_term, english_term in self.multilingual_mappings.items():
            if bengali_term in content or english_term in content_lower:
                context.multilingual_keywords[bengali_term] = english_term
        
        # Extract financial amounts
        financial_matches = re.findall(r"₹[\d,]+(?:\s+(?:Lakhs?|per\s+year|annually))?", content)
        context.financial_amounts = financial_matches
        
        # Extract source attribution
        context.source_attribution = await self._extract_source_attribution(content, file_path)
        
        # Determine content category and priority
        context.content_category = self._categorize_content(Path(file_path).name, content)
        context.priority_level = self._determine_priority_level(content)
        
        return context
    
    async def _extract_source_attribution(self, content: str, file_path: str) -> SourceAttribution:
        """Extract source attribution information from content."""
        source_lines = []
        
        # Extract source markers
        for pattern in self.source_patterns["source_markers"]:
            matches = re.findall(pattern, content, re.MULTILINE)
            source_lines.extend(matches)
        
        # Extract URLs
        urls = []
        for pattern in self.source_patterns["url_patterns"]:
            urls.extend(re.findall(pattern, content))
        
        # Determine source type
        source_type = "educational_document"
        for doc_type in self.source_patterns["document_types"]:
            if re.search(doc_type, content, re.IGNORECASE):
                source_type = f"official_{doc_type}"
                break
        
        # Calculate reliability score
        reliability_score = self._calculate_source_reliability(source_lines, urls, content)
        
        return SourceAttribution(
            data_source_file=Path(file_path).name,
            original_source=source_lines[0] if source_lines else "Educational content database",
            source_url=urls[0] if urls else "Internal database",
            verification_date="January 2025",
            source_type=source_type,
            source_reliability=reliability_score,
            currency_status="current"
        )
    
    def _calculate_source_reliability(self, source_lines: List[str], urls: List[str], content: str) -> float:
        """Calculate source reliability score (0.0-1.0)."""
        score = 0.5  # Base score
        
        # Official sources boost reliability
        if any("university" in line.lower() for line in source_lines):
            score += 0.3
        if any("official" in line.lower() for line in source_lines):
            score += 0.2
        if any(".ac.in" in url for url in urls):
            score += 0.2
        if any("government" in content.lower() or "ministry" in content.lower()):
            score += 0.1
        
        # Recent dates boost reliability
        if "2025" in content:
            score += 0.1
        
        return min(score, 1.0)
    
    def _categorize_content(self, filename: str, content: str) -> ContentCategory:
        """Categorize content based on filename and content analysis."""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        if "fees" in filename_lower or "scholarship" in filename_lower:
            return ContentCategory.FINANCIAL_INFORMATION
        elif "comparison" in filename_lower or "comparative" in filename_lower:
            return ContentCategory.COMPARATIVE_ANALYSIS
        elif "admission" in filename_lower or "process" in filename_lower:
            return ContentCategory.ADMISSION_PROCESSES
        elif "visa" in filename_lower or "frro" in filename_lower or "bank" in filename_lower:
            return ContentCategory.LEGAL_VISA
        elif "hostel" in filename_lower or "campus" in filename_lower or "life" in filename_lower:
            return ContentCategory.CAMPUS_LIFE
        elif "university_profile" in filename_lower or "ranking" in filename_lower:
            return ContentCategory.UNIVERSITY_PROFILES
        elif any(term in filename_lower for term in ["challenge", "solution", "question", "concern"]):
            return ContentCategory.TROUBLESHOOTING
        elif "course" in filename_lower or "academic" in filename_lower or "program" in filename_lower:
            return ContentCategory.ACADEMIC_PROGRAMS
        else:
            return ContentCategory.PRACTICAL_GUIDANCE
    
    def _determine_priority_level(self, content: str) -> ContextPriority:
        """Determine priority level based on content analysis."""
        content_lower = content.lower()
        
        # Check for critical keywords
        critical_keywords = ["visa", "deadline", "fee", "admission", "urgent", "must"]
        if any(keyword in content_lower for keyword in critical_keywords):
            return ContextPriority.CRITICAL
        
        # Check for important keywords
        important_keywords = ["scholarship", "requirement", "process", "application"]
        if any(keyword in content_lower for keyword in important_keywords):
            return ContextPriority.IMPORTANT
        
        # Check for useful keywords
        useful_keywords = ["campus", "hostel", "culture", "festival"]
        if any(keyword in content_lower for keyword in useful_keywords):
            return ContextPriority.USEFUL
        
        return ContextPriority.REFERENCE
    
    async def _extract_content_patterns(self, content: str) -> Dict[str, List[str]]:
        """Extract structured content patterns."""
        patterns = {}
        
        for pattern_name, pattern_obj in self.content_patterns.items():
            matches = []
            for regex_pattern in pattern_obj.regex_patterns:
                found_matches = re.findall(regex_pattern, content, re.IGNORECASE)
                matches.extend(found_matches)
            patterns[pattern_name] = list(set(matches))  # Remove duplicates
        
        return patterns
    
    async def _calculate_quality_metrics(self, content: str, context_metadata: ContextMetadata) -> Dict[str, float]:
        """Calculate comprehensive quality metrics."""
        return {
            "context_completeness": context_metadata.context_completeness_score(),
            "content_length_score": min(len(content) / 10000, 1.0),  # Normalize to 10k chars
            "structure_score": self._calculate_structure_score(content),
            "source_reliability": context_metadata.source_attribution.source_reliability if context_metadata.source_attribution else 0.5,
            "multilingual_support": len(context_metadata.multilingual_keywords) / 10,  # Normalize to 10 terms
            "specificity_score": self._calculate_specificity_score(content, context_metadata),
            "actionability_score": self._calculate_actionability_score(content)
        }
    
    def _calculate_structure_score(self, content: str) -> float:
        """Calculate content structure quality score."""
        score = 0.0
        
        # Check for headers and sections
        if re.search(r"^#{1,6}\s+", content, re.MULTILINE):
            score += 0.3
        
        # Check for numbered lists
        if re.search(r"^\d+\.\s+", content, re.MULTILINE):
            score += 0.2
        
        # Check for bullet points
        if re.search(r"^[-*]\s+", content, re.MULTILINE):
            score += 0.2
        
        # Check for tables
        if "|" in content and "---" in content:
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_specificity_score(self, content: str, context_metadata: ContextMetadata) -> float:
        """Calculate content specificity score."""
        score = 0.0
        
        # University specificity
        if context_metadata.universities:
            score += 0.2
        
        # Program specificity
        if context_metadata.programs:
            score += 0.2
        
        # Timeline specificity
        if "2025-26" in content:
            score += 0.2
        
        # Financial specificity
        if context_metadata.financial_amounts:
            score += 0.2
        
        # Process specificity
        if any(term in content.lower() for term in ["step", "process", "procedure"]):
            score += 0.2
        
        return score
    
    def _calculate_actionability_score(self, content: str) -> float:
        """Calculate content actionability score."""
        score = 0.0
        content_lower = content.lower()
        
        # Action verbs
        action_verbs = ["apply", "submit", "contact", "visit", "call", "email", "register"]
        if any(verb in content_lower for verb in action_verbs):
            score += 0.3
        
        # Specific instructions
        if any(term in content_lower for term in ["how to", "steps to", "procedure to"]):
            score += 0.3
        
        # Contact information
        if re.search(r"[\w.-]+@[\w.-]+", content) or re.search(r"\+?\d{10,}", content):
            score += 0.2
        
        # Deadlines and timelines
        if any(term in content_lower for term in ["deadline", "before", "by", "until"]):
            score += 0.2
        
        return min(score, 1.0)
    
    async def _generate_prompt_insights(self, content: str, context_metadata: ContextMetadata) -> Dict[str, Any]:
        """Generate prompt engineering insights for Q&A generation."""
        return {
            "recommended_question_types": self._identify_question_types(content),
            "context_enhancement_opportunities": self._identify_context_opportunities(context_metadata),
            "multilingual_integration_points": list(context_metadata.multilingual_keywords.keys()),
            "complexity_assessment": self._assess_content_complexity(content),
            "audience_targeting_recommendations": list(context_metadata.audiences),
            "prompt_templates": self._generate_content_specific_prompts(content, context_metadata)
        }
    
    def _identify_question_types(self, content: str) -> List[str]:
        """Identify suitable question types for the content."""
        question_types = []
        content_lower = content.lower()
        
        if "fee" in content_lower or "cost" in content_lower:
            question_types.append("financial_calculation")
        if "process" in content_lower or "step" in content_lower:
            question_types.append("process_explanation")
        if any(uni in content_lower for uni in ["sharda", "amity", "galgotias"]):
            question_types.append("comparative_analysis")
        if "requirement" in content_lower or "eligibility" in content_lower:
            question_types.append("eligibility_clarification")
        if "scholarship" in content_lower:
            question_types.append("benefit_explanation")
        
        return question_types
    
    def _identify_context_opportunities(self, context_metadata: ContextMetadata) -> List[str]:
        """Identify opportunities for context enhancement."""
        opportunities = []
        
        if not context_metadata.universities:
            opportunities.append("add_university_specification")
        if not context_metadata.programs:
            opportunities.append("add_program_specification")
        if not context_metadata.academic_levels:
            opportunities.append("add_academic_level_context")
        if not context_metadata.audiences:
            opportunities.append("add_audience_targeting")
        if len(context_metadata.multilingual_keywords) < 3:
            opportunities.append("enhance_multilingual_support")
        
        return opportunities
    
    def _assess_content_complexity(self, content: str) -> str:
        """Assess content complexity level."""
        word_count = len(content.split())
        sentence_count = len(re.findall(r'[.!?]+', content))
        
        if sentence_count == 0:
            return "simple"
        
        avg_sentence_length = word_count / sentence_count
        
        if avg_sentence_length < 15:
            return "simple"
        elif avg_sentence_length < 25:
            return "moderate"
        else:
            return "complex"
    
    def _generate_content_specific_prompts(self, content: str, context_metadata: ContextMetadata) -> Dict[str, str]:
        """Generate content-specific prompt templates."""
        prompts = {}
        
        # Base prompt with context
        base_context = f"Universities: {', '.join(context_metadata.universities)}, Programs: {', '.join(context_metadata.programs)}"
        
        prompts["context_aware_extraction"] = f"""
        Extract Q&A pairs from this educational content with mandatory context specification:
        {base_context}
        Student Background: {context_metadata.student_background}
        Timeline: {context_metadata.timeline}
        """
        
        if context_metadata.financial_amounts:
            prompts["financial_analysis"] = f"""
            Generate financial planning Q&A with specific amounts: {', '.join(context_metadata.financial_amounts)}
            Include cost breakdowns and scholarship calculations with full context.
            """
        
        if "process" in content.lower():
            prompts["process_documentation"] = f"""
            Create step-by-step process Q&A with complete context for {context_metadata.student_background}.
            Include timeline: {context_metadata.timeline} and university context.
            """
        
        return prompts
    
    async def _verify_source_attribution(self, content: str) -> Dict[str, Any]:
        """Verify source attribution completeness and accuracy."""
        verification = {
            "source_markers_found": [],
            "urls_found": [],
            "attribution_completeness": 0.0,
            "reliability_indicators": [],
            "verification_recommendations": []
        }
        
        # Find source markers
        for pattern in self.source_patterns["source_markers"]:
            matches = re.findall(pattern, content, re.MULTILINE)
            verification["source_markers_found"].extend(matches)
        
        # Find URLs
        for pattern in self.source_patterns["url_patterns"]:
            matches = re.findall(pattern, content)
            verification["urls_found"].extend(matches)
        
        # Calculate completeness
        completeness_factors = [
            bool(verification["source_markers_found"]),
            bool(verification["urls_found"]),
            "2025" in content,  # Current year
            any(term in content.lower() for term in ["official", "university", "government"])
        ]
        verification["attribution_completeness"] = sum(completeness_factors) / len(completeness_factors)
        
        # Identify reliability indicators
        if any(".ac.in" in url for url in verification["urls_found"]):
            verification["reliability_indicators"].append("official_university_domain")
        if "official" in content.lower():
            verification["reliability_indicators"].append("official_document_claim")
        if "brochure" in content.lower():
            verification["reliability_indicators"].append("official_brochure")
        
        # Generate recommendations
        if verification["attribution_completeness"] < 0.8:
            verification["verification_recommendations"].append("enhance_source_attribution")
        if not verification["urls_found"]:
            verification["verification_recommendations"].append("add_source_urls")
        if "2024" in content and "2025" not in content:
            verification["verification_recommendations"].append("update_to_current_academic_year")
        
        return verification
    
    async def _identify_content_gaps(self, content: str, context_metadata: ContextMetadata) -> List[str]:
        """Identify gaps in content coverage."""
        gaps = []
        
        # Check for missing mandatory context elements
        if not context_metadata.universities:
            gaps.append("missing_university_specification")
        if not context_metadata.programs:
            gaps.append("missing_program_specification")
        if context_metadata.student_background != "bangladeshi_students":
            gaps.append("missing_student_background_context")
        if context_metadata.timeline != "2025-26":
            gaps.append("missing_current_timeline")
        
        # Check for missing practical information
        content_lower = content.lower()
        if "fee" in content_lower and not context_metadata.financial_amounts:
            gaps.append("missing_specific_fee_amounts")
        if "contact" in content_lower and not re.search(r"[\w.-]+@[\w.-]+", content):
            gaps.append("missing_contact_information")
        if "deadline" in content_lower and not re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{4}", content):
            gaps.append("missing_specific_dates")
        
        return gaps
    
    async def _generate_optimization_recommendations(self, content: str, context_metadata: ContextMetadata, quality_metrics: Dict[str, float]) -> List[str]:
        """Generate optimization recommendations for content improvement."""
        recommendations = []
        
        # Context completeness recommendations
        if quality_metrics["context_completeness"] < 0.8:
            recommendations.append("enhance_context_completeness")
        
        # Structure improvements
        if quality_metrics["structure_score"] < 0.7:
            recommendations.append("improve_content_structure")
        
        # Specificity improvements
        if quality_metrics["specificity_score"] < 0.6:
            recommendations.append("add_specific_details")
        
        # Actionability improvements
        if quality_metrics["actionability_score"] < 0.6:
            recommendations.append("enhance_actionable_guidance")
        
        # Multilingual support
        if quality_metrics["multilingual_support"] < 0.3:
            recommendations.append("add_multilingual_keywords")
        
        # Source reliability
        if quality_metrics["source_reliability"] < 0.8:
            recommendations.append("strengthen_source_attribution")
        
        return recommendations
    
    async def _generate_global_insights(self, analyses: List[AdvancedAnalysisResult]) -> Dict[str, Any]:
        """Generate global insights across all analyzed files."""
        if not analyses:
            return {}
        
        # Aggregate statistics
        total_universities = set()
        total_programs = set()
        total_academic_levels = set()
        content_categories = Counter()
        priority_levels = Counter()
        
        for analysis in analyses:
            total_universities.update(analysis.context_metadata.universities)
            total_programs.update(analysis.context_metadata.programs)
            total_academic_levels.update(analysis.context_metadata.academic_levels)
            content_categories[analysis.content_category] += 1
            priority_levels[analysis.context_metadata.priority_level] += 1
        
        # Calculate average quality metrics
        avg_quality = {}
        if analyses:
            for metric in analyses[0].quality_metrics.keys():
                avg_quality[metric] = sum(a.quality_metrics[metric] for a in analyses) / len(analyses)
        
        # Identify top gaps and recommendations
        all_gaps = [gap for analysis in analyses for gap in analysis.content_gaps]
        all_recommendations = [rec for analysis in analyses for rec in analysis.optimization_recommendations]
        
        return {
            "coverage_statistics": {
                "universities_covered": list(total_universities),
                "programs_covered": list(total_programs),
                "academic_levels_covered": list(total_academic_levels),
                "total_unique_universities": len(total_universities),
                "total_unique_programs": len(total_programs)
            },
            "content_distribution": {
                "by_category": dict(content_categories),
                "by_priority": dict(priority_levels)
            },
            "quality_overview": {
                "average_metrics": avg_quality,
                "highest_quality_files": self._get_highest_quality_files(analyses),
                "lowest_quality_files": self._get_lowest_quality_files(analyses)
            },
            "common_gaps": Counter(all_gaps).most_common(10),
            "common_recommendations": Counter(all_recommendations).most_common(10),
            "context_completeness_distribution": self._analyze_context_distribution(analyses),
            "source_attribution_summary": self._summarize_source_attribution(analyses)
        }
    
    def _get_highest_quality_files(self, analyses: List[AdvancedAnalysisResult], top_n: int = 5) -> List[Dict[str, Any]]:
        """Get files with highest overall quality scores."""
        def calculate_overall_score(analysis: AdvancedAnalysisResult) -> float:
            metrics = analysis.quality_metrics
            return (
                metrics.get("context_completeness", 0) * 0.3 +
                metrics.get("structure_score", 0) * 0.2 +
                metrics.get("specificity_score", 0) * 0.2 +
                metrics.get("actionability_score", 0) * 0.15 +
                metrics.get("source_reliability", 0) * 0.15
            )
        
        sorted_analyses = sorted(analyses, key=calculate_overall_score, reverse=True)
        
        return [
            {
                "file_path": analysis.file_path,
                "overall_score": calculate_overall_score(analysis),
                "category": analysis.content_category.value,
                "context_completeness": analysis.quality_metrics.get("context_completeness", 0)
            }
            for analysis in sorted_analyses[:top_n]
        ]
    
    def _get_lowest_quality_files(self, analyses: List[AdvancedAnalysisResult], bottom_n: int = 5) -> List[Dict[str, Any]]:
        """Get files with lowest overall quality scores."""
        def calculate_overall_score(analysis: AdvancedAnalysisResult) -> float:
            metrics = analysis.quality_metrics
            return (
                metrics.get("context_completeness", 0) * 0.3 +
                metrics.get("structure_score", 0) * 0.2 +
                metrics.get("specificity_score", 0) * 0.2 +
                metrics.get("actionability_score", 0) * 0.15 +
                metrics.get("source_reliability", 0) * 0.15
            )
        
        sorted_analyses = sorted(analyses, key=calculate_overall_score)
        
        return [
            {
                "file_path": analysis.file_path,
                "overall_score": calculate_overall_score(analysis),
                "category": analysis.content_category.value,
                "recommendations": analysis.optimization_recommendations[:3]
            }
            for analysis in sorted_analyses[:bottom_n]
        ]
    
    def _analyze_context_distribution(self, analyses: List[AdvancedAnalysisResult]) -> Dict[str, Any]:
        """Analyze context completeness distribution."""
        completeness_scores = [a.context_metadata.context_completeness_score() for a in analyses]
        
        return {
            "average_completeness": sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0,
            "minimum_completeness": min(completeness_scores) if completeness_scores else 0,
            "maximum_completeness": max(completeness_scores) if completeness_scores else 0,
            "files_with_complete_context": len([s for s in completeness_scores if s >= 0.9]),
            "files_needing_context_improvement": len([s for s in completeness_scores if s < 0.7])
        }
    
    def _summarize_source_attribution(self, analyses: List[AdvancedAnalysisResult]) -> Dict[str, Any]:
        """Summarize source attribution across all files."""
        total_files = len(analyses)
        files_with_sources = sum(1 for a in analyses if a.context_metadata.source_attribution)
        
        source_types = Counter()
        reliability_scores = []
        
        for analysis in analyses:
            if analysis.context_metadata.source_attribution:
                source_types[analysis.context_metadata.source_attribution.source_type] += 1
                reliability_scores.append(analysis.context_metadata.source_attribution.source_reliability)
        
        return {
            "files_with_source_attribution": files_with_sources,
            "attribution_coverage_percentage": (files_with_sources / total_files) * 100 if total_files > 0 else 0,
            "source_type_distribution": dict(source_types),
            "average_source_reliability": sum(reliability_scores) / len(reliability_scores) if reliability_scores else 0,
            "high_reliability_sources": len([s for s in reliability_scores if s >= 0.8])
        }
    
    async def _generate_prompt_recommendations(self, analyses: List[AdvancedAnalysisResult]) -> Dict[str, Any]:
        """Generate comprehensive prompt engineering recommendations."""
        return {
            "context_enhancement_strategies": self._recommend_context_strategies(analyses),
            "question_type_optimization": self._recommend_question_types(analyses),
            "multilingual_integration": self._recommend_multilingual_approaches(analyses),
            "source_attribution_improvements": self._recommend_source_improvements(analyses),
            "audience_targeting_refinements": self._recommend_audience_targeting(analyses),
            "advanced_prompt_templates": self._generate_advanced_prompt_templates(analyses)
        }
    
    def _recommend_context_strategies(self, analyses: List[AdvancedAnalysisResult]) -> List[str]:
        """Recommend context enhancement strategies."""
        strategies = []
        
        # Analyze context gaps across all files
        university_coverage = sum(1 for a in analyses if a.context_metadata.universities) / len(analyses)
        program_coverage = sum(1 for a in analyses if a.context_metadata.programs) / len(analyses)
        
        if university_coverage < 0.8:
            strategies.append("mandatory_university_specification_in_all_qa")
        if program_coverage < 0.8:
            strategies.append("mandatory_program_context_in_all_qa")
        
        strategies.append("implement_context_completeness_scoring")
        strategies.append("add_cultural_context_for_bangladeshi_students")
        strategies.append("ensure_timeline_consistency_across_all_content")
        
        return strategies
    
    def _recommend_question_types(self, analyses: List[AdvancedAnalysisResult]) -> Dict[str, List[str]]:
        """Recommend question types based on content analysis."""
        recommendations = defaultdict(list)
        
        for analysis in analyses:
            category = analysis.content_category.value
            
            if category == "financial_information":
                recommendations[category].extend([
                    "cost_calculation_questions",
                    "scholarship_eligibility_questions",
                    "financial_planning_questions"
                ])
            elif category == "admission_processes":
                recommendations[category].extend([
                    "step_by_step_process_questions",
                    "document_requirement_questions",
                    "timeline_and_deadline_questions"
                ])
            elif category == "comparative_analysis":
                recommendations[category].extend([
                    "university_comparison_questions",
                    "program_comparison_questions",
                    "value_proposition_questions"
                ])
        
        return dict(recommendations)
    
    def _recommend_multilingual_approaches(self, analyses: List[AdvancedAnalysisResult]) -> List[str]:
        """Recommend multilingual integration approaches."""
        return [
            "add_bengali_keywords_to_technical_terms",
            "provide_cultural_context_explanations",
            "include_bengali_transliteration_for_university_names",
            "add_bangladeshi_education_system_equivalents",
            "integrate_bengali_phrases_for_common_questions"
        ]
    
    def _recommend_source_improvements(self, analyses: List[AdvancedAnalysisResult]) -> List[str]:
        """Recommend source attribution improvements."""
        improvements = []
        
        # Check source attribution coverage
        files_with_sources = sum(1 for a in analyses if a.context_metadata.source_attribution)
        if files_with_sources < len(analyses) * 0.9:
            improvements.append("ensure_complete_source_attribution_coverage")
        
        improvements.extend([
            "standardize_source_citation_format",
            "verify_all_university_website_urls",
            "add_document_verification_dates",
            "include_source_reliability_indicators",
            "implement_source_currency_tracking"
        ])
        
        return improvements
    
    def _recommend_audience_targeting(self, analyses: List[AdvancedAnalysisResult]) -> Dict[str, List[str]]:
        """Recommend audience targeting refinements."""
        return {
            "students": [
                "direct_actionable_guidance",
                "step_by_step_instructions",
                "peer_perspective_language",
                "practical_tips_and_tricks"
            ],
            "parents": [
                "comprehensive_explanations",
                "cost_benefit_analysis",
                "safety_and_security_information",
                "long_term_career_implications"
            ],
            "agents": [
                "detailed_process_documentation",
                "comparison_matrices",
                "troubleshooting_guides",
                "regulatory_compliance_information"
            ]
        }
    
    def _generate_advanced_prompt_templates(self, analyses: List[AdvancedAnalysisResult]) -> Dict[str, str]:
        """Generate advanced prompt templates based on analysis."""
        return {
            "context_rich_extraction": """
            Generate Q&A pairs with MANDATORY CONTEXT ELEMENTS:
            - University: {specify exact university from: Sharda, Amity, Galgotias, G.L. Bajaj, NIU}
            - Program: {specify exact program: B.Tech CSE, BCA, BBA, etc.}
            - Student Background: "for Bangladeshi students"
            - Timeline: "for 2025-26 academic year"
            - Academic Level: {specify SSC/HSC/Diploma/Bachelor's level}
            - Audience: {specify students/parents/agents}
            
            SOURCE ATTRIBUTION REQUIRED:
            - Data Source File: {file_name}
            - Original Source: {official source document}
            - Source URL: {official website URL}
            - Verification Date: January 2025
            - Source Type: {official brochure/website/document}
            """,
            
            "multilingual_enhancement": """
            Enhance Q&A with Bengali-English integration:
            - Include Bengali keywords: শিক্ষার্থী (student), বিশ্ববিদ্যালয় (university)
            - Add cultural context for Bangladeshi students
            - Explain Indian education system terms
            - Use "বাংলাদেশি শিক্ষার্থীদের জন্য" where appropriate
            """,
            
            "financial_analysis": """
            Generate financial Q&A with complete context:
            - Specify exact amounts in ₹ (Rupees)
            - Include scholarship calculations with CGPA requirements
            - Provide total cost breakdowns for 4-year programs
            - Add lateral entry fee structures (3-year programs)
            - Include all mandatory fees and hidden costs
            """
        }
    
    async def _assess_data_quality(self, analyses: List[AdvancedAnalysisResult]) -> Dict[str, Any]:
        """Assess overall data quality across all files."""
        if not analyses:
            return {}
        
        # Calculate aggregate quality scores
        quality_metrics = defaultdict(list)
        for analysis in analyses:
            for metric, score in analysis.quality_metrics.items():
                quality_metrics[metric].append(score)
        
        aggregate_scores = {
            metric: {
                "average": sum(scores) / len(scores),
                "minimum": min(scores),
                "maximum": max(scores),
                "files_above_threshold": len([s for s in scores if s >= 0.7])
            }
            for metric, scores in quality_metrics.items()
        }
        
        return {
            "overall_quality_assessment": aggregate_scores,
            "data_consistency_analysis": self._analyze_data_consistency(analyses),
            "completeness_evaluation": self._evaluate_completeness(analyses),
            "accuracy_indicators": self._assess_accuracy_indicators(analyses),
            "improvement_priorities": self._identify_improvement_priorities(analyses)
        }
    
    def _analyze_data_consistency(self, analyses: List[AdvancedAnalysisResult]) -> Dict[str, Any]:
        """Analyze data consistency across files."""
        # Check for consistent university information
        university_mentions = defaultdict(int)
        program_mentions = defaultdict(int)
        
        for analysis in analyses:
            for university in analysis.context_metadata.universities:
                university_mentions[university] += 1
            for program in analysis.context_metadata.programs:
                program_mentions[program] += 1
        
        return {
            "university_consistency": dict(university_mentions),
            "program_consistency": dict(program_mentions),
            "timeline_consistency": len([a for a in analyses if a.context_metadata.timeline == "2025-26"]) / len(analyses),
            "student_background_consistency": len([a for a in analyses if a.context_metadata.student_background == "bangladeshi_students"]) / len(analyses)
        }
    
    def _evaluate_completeness(self, analyses: List[AdvancedAnalysisResult]) -> Dict[str, Any]:
        """Evaluate content completeness."""
        return {
            "files_with_complete_context": len([a for a in analyses if a.context_metadata.context_completeness_score() >= 0.9]),
            "files_with_source_attribution": len([a for a in analyses if a.context_metadata.source_attribution]),
            "average_context_completeness": sum(a.context_metadata.context_completeness_score() for a in analyses) / len(analyses),
            "coverage_gaps": self._identify_coverage_gaps(analyses)
        }
    
    def _assess_accuracy_indicators(self, analyses: List[AdvancedAnalysisResult]) -> Dict[str, Any]:
        """Assess accuracy indicators across content."""
        return {
            "current_timeline_usage": len([a for a in analyses if "2025-26" in str(a.context_metadata.timeline)]) / len(analyses),
            "official_source_percentage": len([a for a in analyses if a.context_metadata.source_attribution and a.context_metadata.source_attribution.source_reliability >= 0.8]) / len(analyses),
            "specific_data_presence": len([a for a in analyses if a.context_metadata.financial_amounts]) / len(analyses)
        }
    
    def _identify_improvement_priorities(self, analyses: List[AdvancedAnalysisResult]) -> List[Dict[str, Any]]:
        """Identify improvement priorities based on analysis."""
        priorities = []
        
        # Context completeness priority
        low_context_files = [a for a in analyses if a.context_metadata.context_completeness_score() < 0.7]
        if low_context_files:
            priorities.append({
                "priority": "high",
                "area": "context_completeness",
                "affected_files": len(low_context_files),
                "recommendation": "enhance_mandatory_context_elements"
            })
        
        # Source attribution priority
        missing_sources = [a for a in analyses if not a.context_metadata.source_attribution]
        if missing_sources:
            priorities.append({
                "priority": "medium",
                "area": "source_attribution", 
                "affected_files": len(missing_sources),
                "recommendation": "add_complete_source_attribution"
            })
        
        return priorities
    
    def _identify_coverage_gaps(self, analyses: List[AdvancedAnalysisResult]) -> List[str]:
        """Identify gaps in content coverage."""
        gaps = []
        
        # Check university coverage
        all_universities = {"Sharda University", "Amity University", "Galgotias University", "G.L. Bajaj", "NIU"}
        covered_universities = set()
        for analysis in analyses:
            covered_universities.update(analysis.context_metadata.universities)
        
        missing_universities = all_universities - covered_universities
        if missing_universities:
            gaps.extend([f"missing_{uni.lower().replace(' ', '_')}_coverage" for uni in missing_universities])
        
        # Check program coverage  
        essential_programs = {"B.Tech CSE", "BCA", "BBA", "B.Com"}
        covered_programs = set()
        for analysis in analyses:
            covered_programs.update(analysis.context_metadata.programs)
        
        missing_programs = essential_programs - covered_programs
        if missing_programs:
            gaps.extend([f"missing_{prog.lower().replace('.', '').replace(' ', '_')}_coverage" for prog in missing_programs])
        
        return gaps
    
    async def _analyze_context_completeness(self, analyses: List[AdvancedAnalysisResult]) -> Dict[str, Any]:
        """Analyze context completeness across all files."""
        completeness_data = {
            "mandatory_elements_analysis": {},
            "completeness_distribution": {},
            "improvement_recommendations": []
        }
        
        # Analyze each mandatory element
        mandatory_elements = ["universities", "programs", "student_background", "timeline", "academic_levels", "audiences"]
        
        for element in mandatory_elements:
            element_presence = []
            for analysis in analyses:
                if element == "universities":
                    element_presence.append(bool(analysis.context_metadata.universities))
                elif element == "programs":
                    element_presence.append(bool(analysis.context_metadata.programs))
                elif element == "student_background":
                    element_presence.append(analysis.context_metadata.student_background == "bangladeshi_students")
                elif element == "timeline":
                    element_presence.append(analysis.context_metadata.timeline == "2025-26")
                elif element == "academic_levels":
                    element_presence.append(bool(analysis.context_metadata.academic_levels))
                elif element == "audiences":
                    element_presence.append(bool(analysis.context_metadata.audiences))
            
            completeness_data["mandatory_elements_analysis"][element] = {
                "coverage_percentage": (sum(element_presence) / len(element_presence)) * 100,
                "files_with_element": sum(element_presence),
                "files_missing_element": len(element_presence) - sum(element_presence)
            }
        
        # Distribution analysis
        completeness_scores = [a.context_metadata.context_completeness_score() for a in analyses]
        completeness_data["completeness_distribution"] = {
            "excellent (90-100%)": len([s for s in completeness_scores if s >= 0.9]),
            "good (70-89%)": len([s for s in completeness_scores if 0.7 <= s < 0.9]),
            "needs_improvement (50-69%)": len([s for s in completeness_scores if 0.5 <= s < 0.7]),
            "poor (<50%)": len([s for s in completeness_scores if s < 0.5])
        }
        
        # Generate improvement recommendations
        for element, data in completeness_data["mandatory_elements_analysis"].items():
            if data["coverage_percentage"] < 80:
                completeness_data["improvement_recommendations"].append(
                    f"improve_{element}_specification_across_content"
                )
        
        return completeness_data
    
    def export_analysis_results(self, output_path: str) -> None:
        """Export comprehensive analysis results to JSON file."""
        export_data = {
            "analysis_metadata": {
                "timestamp": time.time(),
                "analyzer_version": "2.0.0",
                "total_files_analyzed": len(self.analysis_results)
            },
            "individual_file_analyses": [
                {
                    "file_path": result.file_path,
                    "content_category": result.content_category.value,
                    "context_metadata": {
                        "universities": list(result.context_metadata.universities),
                        "programs": list(result.context_metadata.programs),
                        "student_background": result.context_metadata.student_background,
                        "timeline": result.context_metadata.timeline,
                        "academic_levels": list(result.context_metadata.academic_levels),
                        "audiences": list(result.context_metadata.audiences),
                        "context_completeness_score": result.context_metadata.context_completeness_score(),
                        "source_attribution": result.context_metadata.source_attribution.to_dict() if result.context_metadata.source_attribution else None
                    },
                    "quality_metrics": result.quality_metrics,
                    "content_gaps": result.content_gaps,
                    "optimization_recommendations": result.optimization_recommendations
                }
                for result in self.analysis_results
            ],
            "global_insights": self.global_insights
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Analysis results exported to {output_path}")


async def main():
    """Main function for testing the advanced analyzer."""
    config = Config()
    analyzer = AdvancedEducationalDataAnalyzer(config)
    
    # Analyze the educational directory
    results = await analyzer.analyze_educational_directory("data/educational")
    
    # Export results
    analyzer.export_analysis_results("advanced_educational_analysis_results.json")
    
    print("Advanced Educational Data Analysis Complete!")
    print(f"Analyzed {results['analysis_summary']['successful_analyses']} files successfully")
    print(f"Average context completeness: {results['context_completeness_analysis']['completeness_distribution']}")


if __name__ == "__main__":
    asyncio.run(main())
