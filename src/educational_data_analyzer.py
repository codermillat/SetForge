"""
Educational Data Context Analyzer
Analyzes the 48 comprehensive educational data files to extract context patterns,
entities, and metadata for enhanced QA generation.
"""

import asyncio
import json
import re
import os
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import logging
from collections import defaultdict, Counter


@dataclass
class EducationalEntity:
    """Represents an educational entity with context."""
    name: str
    entity_type: str  # university, program, process, etc.
    aliases: List[str] = field(default_factory=list)
    context_files: Set[str] = field(default_factory=set)
    frequency: int = 0
    associated_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentAnalysis:
    """Analysis results for educational content."""
    file_path: str
    content_type: str
    universities: List[str] = field(default_factory=list)
    programs: List[str] = field(default_factory=list)
    academic_levels: List[str] = field(default_factory=list)
    processes: List[str] = field(default_factory=list)
    financial_data: List[str] = field(default_factory=list)
    timeline_markers: List[str] = field(default_factory=list)
    key_concepts: List[str] = field(default_factory=list)
    bengali_terms: List[str] = field(default_factory=list)
    source_citations: List[str] = field(default_factory=list)
    structured_sections: List[str] = field(default_factory=list)
    word_count: int = 0
    context_density_score: float = 0.0


class EducationalDataAnalyzer:
    """Comprehensive analyzer for educational data files."""
    
    def __init__(self, data_directory: str):
        self.data_directory = Path(data_directory)
        self.logger = logging.getLogger(__name__)
        
        # Initialize pattern libraries
        self.entity_patterns = self._init_entity_patterns()
        self.context_patterns = self._init_context_patterns()
        self.multilingual_patterns = self._init_multilingual_patterns()
        
        # Analysis results
        self.file_analyses: Dict[str, ContentAnalysis] = {}
        self.global_entities: Dict[str, EducationalEntity] = {}
        self.context_relationships: Dict[str, List[str]] = defaultdict(list)
        self.content_gaps: List[str] = []
    
    def _init_entity_patterns(self) -> Dict[str, List[str]]:
        """Initialize comprehensive entity detection patterns."""
        return {
            "universities": [
                r"Sharda\s+University",
                r"Amity\s+University(?:\s*\(Noida\))?",
                r"Galgotias\s+University",
                r"G\.?L\.?\s*Bajaj(?:\s+Institute)?",
                r"Noida\s+International\s+University",
                r"NIU"
            ],
            
            "btech_programs": [
                r"B\.Tech(?:\s+in)?\s+(?:Computer\s+Science|CSE)",
                r"B\.Tech(?:\s+in)?\s+(?:Information\s+Technology|IT)",
                r"B\.Tech(?:\s+in)?\s+(?:Electronics?\s*(?:&|and)\s*Communication|ECE)",
                r"B\.Tech(?:\s+in)?\s+(?:Electrical\s*(?:&|and)\s*Electronics|EEE)",
                r"B\.Tech(?:\s+in)?\s+(?:Mechanical\s+Engineering|ME)",
                r"B\.Tech(?:\s+in)?\s+Civil\s+Engineering",
                r"B\.Tech(?:\s+in)?\s+Biotechnology",
                r"B\.Tech\s+CSE\s+with.*(?:AI|ML|Blockchain|IoT|Cloud|Data\s+Science)"
            ],
            
            "other_programs": [
                r"BCA", r"BBA", r"B\.Com", r"B\.Sc",
                r"MBA", r"M\.Tech", r"PhD",
                r"Allied\s+Health", r"Mass\s+Communication"
            ],
            
            "academic_levels": [
                r"SSC", r"HSC", r"Class\s+(?:10|12)",
                r"Diploma", r"Bachelor'?s?", r"Master'?s?", r"PhD",
                r"Undergraduate", r"Postgraduate",
                r"Higher\s+Secondary", r"Secondary\s+School"
            ],
            
            "admission_processes": [
                r"admission\s+process", r"application\s+process",
                r"lateral\s+entry", r"direct\s+admission",
                r"entrance\s+exam", r"interview\s+process",
                r"document\s+verification", r"seat\s+allocation"
            ],
            
            "visa_legal_processes": [
                r"visa\s+application", r"student\s+visa",
                r"FRRO\s+registration", r"e-FRRO", r"C-Form",
                r"address\s+verification", r"bank\s+account\s+opening",
                r"embassy\s+requirements", r"consulate"
            ],
            
            "financial_terms": [
                r"tuition\s+fee", r"annual\s+fee", r"semester\s+fee",
                r"scholarship", r"merit\s+scholarship", r"SAARC\s+scholarship",
                r"hostel\s+fee", r"total\s+cost", r"living\s+expenses",
                r"₹[\d,]+", r"BDT\s+[\d,]+", r"USD\s+[\d,]+"
            ],
            
            "timeline_markers": [
                r"2025-26", r"academic\s+year\s+2025-26?",
                r"July\s+intake", r"January\s+intake",
                r"application\s+deadline", r"session\s+start",
                r"semester\s+\d+", r"year\s+\d+"
            ],
            
            "location_terms": [
                r"Greater\s+Noida", r"Noida", r"Delhi\s+NCR",
                r"India", r"Bangladesh", r"SAARC",
                r"campus", r"hostel", r"accommodation"
            ]
        }
    
    def _init_context_patterns(self) -> Dict[str, List[str]]:
        """Initialize context-specific patterns."""
        return {
            "bangladeshi_context": [
                r"Bangladeshi\s+students?", r"Bangladesh(?:i)?",
                r"SAARC\s+(?:students?|nationals?)", r"international\s+students?",
                r"Dhaka", r"Chittagong", r"Sylhet"
            ],
            
            "comparative_language": [
                r"compared?\s+to", r"vs\.?", r"versus", r"better\s+than",
                r"different\s+from", r"similar\s+to", r"contrast",
                r"advantages?", r"disadvantages?", r"pros?\s+and\s+cons?"
            ],
            
            "process_indicators": [
                r"step\s+\d+", r"first\s+step", r"next\s+step", r"final\s+step",
                r"procedure", r"guidelines?", r"requirements?",
                r"how\s+to", r"process\s+of", r"steps?\s+(?:for|to)"
            ],
            
            "urgency_indicators": [
                r"mandatory", r"required", r"must", r"critical",
                r"important", r"essential", r"necessary",
                r"deadline", r"within\s+\d+\s+days", r"immediately"
            ],
            
            "audience_indicators": [
                r"students?\s+should", r"parents?\s+should",
                r"agents?\s+should", r"counsellors?\s+should",
                r"for\s+students?", r"for\s+parents?",
                r"student\s+guide", r"parent\s+guide"
            ]
        }
    
    def _init_multilingual_patterns(self) -> Dict[str, str]:
        """Initialize Bengali-English patterns and terms."""
        return {
            "bengali_terms": {
                r"শিক্ষার্থী": "student",
                r"বিশ্ববিদ্যালয়": "university", 
                r"ভর্তি": "admission",
                r"বৃত্তি": "scholarship",
                r"শিক্ষা": "education",
                r"ডিগ্রি": "degree",
                r"কোর্স": "course",
                r"ফি": "fee",
                r"খরচ": "cost",
                r"ভিসা": "visa",
                r"বাংলাদেশি": "bangladeshi",
                r"ভারত": "india"
            },
            
            "cultural_terms": [
                r"halal\s+food", r"prayer\s+room", r"mosque",
                r"Bengali\s+community", r"cultural\s+festival",
                r"Durga\s+Puja", r"Eid", r"Pohela\s+Boishakh"
            ]
        }
    
    async def analyze_all_files(self) -> Dict[str, Any]:
        """Analyze all educational data files comprehensively."""
        self.logger.info(f"Starting analysis of educational files in {self.data_directory}")
        
        # Get all educational files
        educational_files = list(self.data_directory.glob("*.txt"))
        self.logger.info(f"Found {len(educational_files)} educational files")
        
        # Analyze each file
        for file_path in educational_files:
            try:
                analysis = await self._analyze_single_file(file_path)
                self.file_analyses[str(file_path)] = analysis
                self._update_global_entities(analysis)
            except Exception as e:
                self.logger.error(f"Error analyzing {file_path}: {e}")
        
        # Perform cross-file analysis
        self._analyze_relationships()
        self._identify_content_gaps()
        self._calculate_context_scores()
        
        # Generate comprehensive report
        return self._generate_analysis_report()
    
    async def _analyze_single_file(self, file_path: Path) -> ContentAnalysis:
        """Analyze a single educational file."""
        self.logger.debug(f"Analyzing file: {file_path.name}")
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {e}")
            return ContentAnalysis(file_path=str(file_path), content_type="error")
        
        # Initialize analysis
        analysis = ContentAnalysis(
            file_path=str(file_path),
            content_type=self._determine_content_type(file_path.name),
            word_count=len(content.split())
        )
        
        # Extract entities and patterns
        analysis.universities = self._extract_entities(content, "universities")
        analysis.programs = (
            self._extract_entities(content, "btech_programs") +
            self._extract_entities(content, "other_programs")
        )
        analysis.academic_levels = self._extract_entities(content, "academic_levels")
        analysis.processes = (
            self._extract_entities(content, "admission_processes") +
            self._extract_entities(content, "visa_legal_processes")
        )
        analysis.financial_data = self._extract_entities(content, "financial_terms")
        analysis.timeline_markers = self._extract_entities(content, "timeline_markers")
        
        # Extract contextual information
        analysis.key_concepts = self._extract_key_concepts(content)
        analysis.bengali_terms = self._extract_bengali_terms(content)
        analysis.source_citations = self._extract_source_citations(content)
        analysis.structured_sections = self._extract_structured_sections(content)
        
        # Calculate context density score
        analysis.context_density_score = self._calculate_context_density(analysis)
        
        return analysis
    
    def _extract_entities(self, content: str, entity_type: str) -> List[str]:
        """Extract entities of a specific type from content."""
        entities = []
        patterns = self.entity_patterns.get(entity_type, [])
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            entities.extend([match.strip() for match in matches if match.strip()])
        
        return list(set(entities))  # Remove duplicates
    
    def _extract_key_concepts(self, content: str) -> List[str]:
        """Extract key educational concepts from content."""
        concepts = []
        
        # Extract concepts from section headers
        section_pattern = r"#+\s*(.+)"
        sections = re.findall(section_pattern, content)
        concepts.extend([section.strip() for section in sections])
        
        # Extract numbered list items that represent concepts
        list_pattern = r"^\d+\.\s*(.+?)(?:\n|$)"
        list_items = re.findall(list_pattern, content, re.MULTILINE)
        concepts.extend([item.strip()[:50] for item in list_items])  # Limit length
        
        # Extract bullet point concepts
        bullet_pattern = r"^[-*]\s*(.+?)(?:\n|$)"
        bullets = re.findall(bullet_pattern, content, re.MULTILINE)
        concepts.extend([bullet.strip()[:50] for bullet in bullets])
        
        return list(set(concepts))
    
    def _extract_bengali_terms(self, content: str) -> List[str]:
        """Extract Bengali terms from content."""
        bengali_terms = []
        
        for bengali_pattern, english_term in self.multilingual_patterns["bengali_terms"].items():
            if re.search(bengali_pattern, content):
                bengali_terms.append(f"{bengali_pattern} ({english_term})")
        
        return bengali_terms
    
    def _extract_source_citations(self, content: str) -> List[str]:
        """Extract source citations from content."""
        citation_pattern = r"—source:\s*(.+?)(?:\n|$)"
        citations = re.findall(citation_pattern, content, re.MULTILINE)
        return [citation.strip() for citation in citations]
    
    def _extract_structured_sections(self, content: str) -> List[str]:
        """Extract structured section headers from content."""
        # Extract markdown-style headers
        header_pattern = r"^#+\s*(.+)"
        headers = re.findall(header_pattern, content, re.MULTILINE)
        return [header.strip() for header in headers]
    
    def _determine_content_type(self, filename: str) -> str:
        """Determine content type from filename."""
        filename = filename.lower()
        
        type_mapping = {
            "fees": "financial",
            "scholarship": "financial",
            "admission": "admission_process",
            "process": "admission_process",
            "comparison": "comparative_analysis",
            "comparative": "comparative_analysis",
            "visa": "legal_compliance",
            "frro": "legal_compliance",
            "bank": "legal_compliance",
            "hostel": "accommodation",
            "accommodation": "accommodation",
            "campus": "campus_life",
            "life": "campus_life",
            "career": "career_guidance",
            "alumni": "career_guidance",
            "post_graduation": "career_guidance",
            "lateral_entry": "admission_policy",
            "safety": "support_services",
            "support": "support_services",
            "guide": "practical_guidance",
            "logistics": "practical_guidance",
            "glossary": "reference",
            "terms": "reference"
        }
        
        for keyword, content_type in type_mapping.items():
            if keyword in filename:
                return content_type
        
        return "general"
    
    def _update_global_entities(self, analysis: ContentAnalysis):
        """Update global entity tracking with file analysis."""
        all_entities = (
            analysis.universities + analysis.programs + 
            analysis.academic_levels + analysis.processes
        )
        
        for entity in all_entities:
            if entity not in self.global_entities:
                self.global_entities[entity] = EducationalEntity(
                    name=entity,
                    entity_type=self._classify_entity_type(entity)
                )
            
            self.global_entities[entity].context_files.add(analysis.file_path)
            self.global_entities[entity].frequency += 1
    
    def _classify_entity_type(self, entity: str) -> str:
        """Classify entity type based on content."""
        entity_lower = entity.lower()
        
        if any(uni in entity_lower for uni in ["sharda", "amity", "galgotias", "bajaj", "noida"]):
            return "university"
        elif any(prog in entity_lower for prog in ["b.tech", "bca", "bba", "mba"]):
            return "program"
        elif any(level in entity_lower for level in ["ssc", "hsc", "diploma", "bachelor"]):
            return "academic_level"
        elif any(proc in entity_lower for proc in ["admission", "visa", "application"]):
            return "process"
        else:
            return "concept"
    
    def _analyze_relationships(self):
        """Analyze relationships between content across files."""
        # Find files that mention the same entities
        entity_file_map = defaultdict(set)
        
        for entity_name, entity in self.global_entities.items():
            for file_path in entity.context_files:
                entity_file_map[entity_name].add(file_path)
        
        # Build relationship map
        for entity_name, files in entity_file_map.items():
            if len(files) > 1:
                self.context_relationships[entity_name] = list(files)
    
    def _identify_content_gaps(self):
        """Identify potential content gaps in the educational data."""
        # Required combinations that should exist
        required_combinations = [
            ("Sharda University", "B.Tech CSE", "Bangladeshi students"),
            ("Amity University", "B.Tech CSE", "Bangladeshi students"),
            ("Galgotias University", "B.Tech CSE", "Bangladeshi students"),
            ("lateral entry", "diploma", "B.Tech"),
            ("scholarship", "CGPA", "Bangladeshi students"),
            ("visa application", "bank statement", "BDT 1,00,000"),
            ("FRRO registration", "14 days", "arrival")
        ]
        
        for combination in required_combinations:
            # Check if combination exists across files
            covering_files = []
            for file_path, analysis in self.file_analyses.items():
                file_content = " ".join([
                    " ".join(analysis.universities),
                    " ".join(analysis.programs),
                    " ".join(analysis.processes),
                    " ".join(analysis.key_concepts)
                ]).lower()
                
                if all(term.lower() in file_content for term in combination):
                    covering_files.append(file_path)
            
            if not covering_files:
                self.content_gaps.append(f"Missing comprehensive coverage: {' + '.join(combination)}")
    
    def _calculate_context_density(self, analysis: ContentAnalysis) -> float:
        """Calculate context density score for an analysis."""
        total_entities = (
            len(analysis.universities) + len(analysis.programs) +
            len(analysis.academic_levels) + len(analysis.processes) +
            len(analysis.financial_data) + len(analysis.timeline_markers)
        )
        
        # Context indicators
        context_indicators = len(analysis.source_citations) + len(analysis.structured_sections)
        
        # Normalize by word count
        if analysis.word_count > 0:
            entity_density = total_entities / (analysis.word_count / 100)  # Per 100 words
            context_density = context_indicators / (analysis.word_count / 1000)  # Per 1000 words
            return min(1.0, (entity_density + context_density) / 2)
        
        return 0.0
    
    def _calculate_context_scores(self):
        """Calculate overall context scores for the dataset."""
        for file_path, analysis in self.file_analyses.items():
            analysis.context_density_score = self._calculate_context_density(analysis)
    
    def _generate_analysis_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report."""
        # Calculate statistics
        total_files = len(self.file_analyses)
        total_entities = len(self.global_entities)
        avg_context_density = sum(
            analysis.context_density_score for analysis in self.file_analyses.values()
        ) / total_files if total_files > 0 else 0
        
        # Count entities by type
        entity_type_counts = Counter(
            entity.entity_type for entity in self.global_entities.values()
        )
        
        # Content type distribution
        content_type_counts = Counter(
            analysis.content_type for analysis in self.file_analyses.values()
        )
        
        # High context density files
        high_context_files = [
            (file_path, analysis.context_density_score)
            for file_path, analysis in self.file_analyses.items()
            if analysis.context_density_score > 0.7
        ]
        
        # Most frequent entities
        top_entities = sorted(
            self.global_entities.values(),
            key=lambda x: x.frequency,
            reverse=True
        )[:20]
        
        return {
            "analysis_summary": {
                "total_files_analyzed": total_files,
                "total_unique_entities": total_entities,
                "average_context_density": round(avg_context_density, 3),
                "content_gaps_identified": len(self.content_gaps)
            },
            
            "entity_distribution": dict(entity_type_counts),
            "content_type_distribution": dict(content_type_counts),
            
            "high_context_files": [
                {"file": Path(file).name, "context_density": score}
                for file, score in high_context_files
            ],
            
            "top_entities": [
                {
                    "name": entity.name,
                    "type": entity.entity_type,
                    "frequency": entity.frequency,
                    "file_coverage": len(entity.context_files)
                }
                for entity in top_entities
            ],
            
            "content_gaps": self.content_gaps,
            
            "relationship_analysis": {
                entity: len(files) for entity, files in self.context_relationships.items()
                if len(files) > 3  # Show entities appearing in 4+ files
            },
            
            "file_analyses": {
                Path(file_path).name: {
                    "content_type": analysis.content_type,
                    "word_count": analysis.word_count,
                    "context_density": analysis.context_density_score,
                    "universities_mentioned": len(analysis.universities),
                    "programs_mentioned": len(analysis.programs),
                    "key_concepts_count": len(analysis.key_concepts),
                    "source_citations_count": len(analysis.source_citations)
                }
                for file_path, analysis in self.file_analyses.items()
            }
        }
    
    async def generate_context_enhancement_recommendations(self) -> Dict[str, List[str]]:
        """Generate recommendations for context enhancement."""
        recommendations = {
            "high_priority_enhancements": [],
            "context_standardization": [],
            "multilingual_opportunities": [],
            "comparative_analysis_gaps": [],
            "process_documentation_improvements": []
        }
        
        # Analyze for high priority enhancements
        for gap in self.content_gaps:
            if "scholarship" in gap.lower() or "fee" in gap.lower():
                recommendations["high_priority_enhancements"].append(
                    f"Add comprehensive coverage for: {gap}"
                )
        
        # Context standardization recommendations
        university_coverage = defaultdict(int)
        for analysis in self.file_analyses.values():
            for uni in analysis.universities:
                university_coverage[uni] += 1
        
        min_coverage = min(university_coverage.values()) if university_coverage else 0
        max_coverage = max(university_coverage.values()) if university_coverage else 0
        
        if max_coverage - min_coverage > 5:
            recommendations["context_standardization"].append(
                "Standardize university coverage across all content types"
            )
        
        # Multilingual opportunities
        low_multilingual_files = [
            Path(file_path).name for file_path, analysis in self.file_analyses.items()
            if len(analysis.bengali_terms) == 0 and "parent" in file_path.lower()
        ]
        
        for file in low_multilingual_files:
            recommendations["multilingual_opportunities"].append(
                f"Add Bengali terms and cultural context to: {file}"
            )
        
        return recommendations
