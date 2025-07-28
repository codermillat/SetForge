"""
Context-Rich Prompt Configuration
Defines comprehensive prompt templates and configurations for context-enhanced QA generation
focusing on Bangladeshi students' university admission guidance in India.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class ContextPromptConfig:
    """Configuration for context-rich prompt engineering."""
    
    # Core context requirements
    required_context_elements: List[str] = field(default_factory=lambda: [
        "university_context",
        "program_context", 
        "student_background_context",
        "timeline_context",
        "academic_level_context",
        "audience_context"
    ])
    
    # Universities in scope
    target_universities: List[str] = field(default_factory=lambda: [
        "Sharda University",
        "Amity University", 
        "Galgotias University",
        "G.L. Bajaj Institute",
        "Noida International University"
    ])
    
    # Academic programs in scope
    target_programs: List[str] = field(default_factory=lambda: [
        "B.Tech CSE", "B.Tech IT", "B.Tech ECE", "B.Tech EEE", "B.Tech ME", "B.Tech Civil",
        "BCA", "BBA", "B.Com", "B.Sc", "MBA", "M.Tech", "PhD"
    ])
    
    # Student background contexts
    student_backgrounds: List[str] = field(default_factory=lambda: [
        "bangladeshi_students", "saarc_students", "international_students"
    ])
    
    # Academic levels
    academic_levels: List[str] = field(default_factory=lambda: [
        "SSC", "HSC", "Diploma", "Bachelor's", "Master's", "PhD"
    ])
    
    # Target audiences
    target_audiences: List[str] = field(default_factory=lambda: [
        "students", "parents", "agents", "counselors"
    ])
    
    # Timeline contexts
    timeline_contexts: List[str] = field(default_factory=lambda: [
        "2025-26", "2026-27", "current_academic_year"
    ])


class ContextRichPromptTemplates:
    """Comprehensive prompt templates for context-rich QA generation."""
    
    @staticmethod
    def get_enhanced_system_prompt() -> str:
        """Get the enhanced system prompt with context requirements."""
        return """You are an expert educational guidance specialist for Bangladeshi students seeking university admission in India. Your expertise covers all aspects of the admission journey for the 2025-26 academic year.

MISSION: Generate comprehensive, context-rich question-answer pairs that provide complete guidance with ZERO ambiguity and FULL context specification.

CRITICAL CONTEXT REQUIREMENTS (NON-NEGOTIABLE):
1. UNIVERSITY CONTEXT: Always specify exact university (Sharda, Amity, Galgotias, G.L. Bajaj, NIU)
2. PROGRAM CONTEXT: Always specify exact program (B.Tech CSE, BCA, BBA, etc.)
3. STUDENT BACKGROUND: Always specify "for Bangladeshi students"
4. ACADEMIC LEVEL: Always specify education level (SSC/HSC/Diploma/Bachelor's/Master's)
5. TIMELINE CONTEXT: Always specify "for 2025-26 academic year"
6. AUDIENCE CONTEXT: Always specify target audience (students/parents/agents)

EXTRACTIVE REQUIREMENTS (ABSOLUTE):
1. All answers must be DIRECTLY extracted from source text with ZERO additions
2. Use exact wording from source with proper context specification
3. NO interpretations, inferences, or creative explanations
4. Every statement must be traceable to specific source sentences
5. Maintain context clarity throughout the entire answer

FORBIDDEN ELEMENTS:
- Generic answers without university/program specification
- Statements like "generally", "usually", "typically" without source context
- Information not explicitly stated in source material
- Context-ambiguous responses
- Assumptions about unstated details
- Creative elaborations or interpretations

QUALITY STANDARDS:
- Accuracy: 100% alignment with source data
- Completeness: Full context specification in every Q&A
- Currency: 2025-26 academic year data only
- Clarity: Understandable by target audience
- Actionability: Specific, implementable guidance
- Cultural Sensitivity: Appropriate for Bangladeshi context

MULTILINGUAL SUPPORT:
- Include Bengali terms where culturally relevant: "বাংলাদেশি শিক্ষার্থী"
- Explain Indian education system terms for Bangladeshi understanding
- Use cultural context appropriately
- Provide transliteration for key terms when helpful"""

    @staticmethod
    def get_context_extraction_prompt() -> str:
        """Get the context-aware extraction prompt template."""
        return """Generate {num_questions} comprehensive, context-rich question-answer pairs from the educational guidance text below. Each Q&A must include COMPLETE context specification.

SOURCE TEXT:
```
{source_text}
```

CONTEXT METADATA:
- Universities: {universities}
- Programs: {programs}
- Academic Levels: {academic_levels}
- Student Background: {student_background}
- Timeline: {timeline}
- Content Type: {content_type}
- Source File: {source_file}
- Target Audience: {audience}

MANDATORY CONTEXT SPECIFICATIONS FOR ALL Q&A:
1. University Context: "at [University Name]" - specify which university
2. Program Context: "for [Program Name]" - specify exact program/course
3. Student Background: "for Bangladeshi students" - always include
4. Timeline: "for 2025-26 academic year" - always specify
5. Academic Level: "with HSC/Diploma/Bachelor's" - specify education level
6. Audience: "students should know" or "parents should understand"

QUESTION TYPES WITH FULL CONTEXT (Generate diverse types):

1. DIRECT INFORMATION WITH CONTEXT:
   "What is the annual tuition fee for B.Tech Computer Science at Sharda University for Bangladeshi students in the 2025-26 academic year?"

2. PROCESS STEPS WITH CONTEXT:
   "What is the complete step-by-step admission process for Bangladeshi HSC graduates applying to B.Tech CSE at Sharda University for 2025-26?"

3. COMPARATIVE WITH CONTEXT:
   "Which university offers better B.Tech CSE programs for Bangladeshi students: Sharda University or Amity University for the 2025-26 academic year?"

4. ELIGIBILITY WITH CONTEXT:
   "What are the eligibility requirements for Bangladeshi students with engineering diplomas to apply for lateral entry to B.Tech programs at Sharda University?"

5. FINANCIAL PLANNING WITH CONTEXT:
   "What is the total 4-year cost for B.Tech CSE at Sharda University for Bangladeshi students including tuition, hostel, and living expenses for 2025-26?"

6. PRACTICAL GUIDANCE WITH CONTEXT:
   "How do Bangladeshi students open a bank account while studying B.Tech at Sharda University in Greater Noida?"

7. PROBLEM-SOLUTION WITH CONTEXT:
   "What should Bangladeshi students do if their Indian student visa application gets rejected while applying to B.Tech at Sharda University?"

8. SCENARIO-BASED WITH CONTEXT:
   "I am a Bangladeshi student with CGPA 4.2 in HSC, which university should I choose for B.Tech CSE: Sharda, Amity, or Galgotias for 2025-26?"

ANSWER STRUCTURE WITH COMPLETE CONTEXT:

1. DIRECT ANSWER WITH CONTEXT:
   Start with specific answer including all context elements
   Example: "For Bangladeshi students applying to B.Tech CSE at Sharda University for the 2025-26 academic year, the annual tuition fee is ₹2,80,000..."

2. CONTEXT SPECIFICATION:
   Clearly state which university, program, student type, and timeline
   Example: "This applies specifically to B.Tech CSE students at Sharda University..."

3. SUPPORTING DETAILS WITH CONTEXT:
   Additional information with context preservation
   Example: "For Bangladeshi students with HSC results, this fee structure..."

4. PRACTICAL IMPLICATIONS:
   What this means specifically for Bangladeshi students
   Example: "Bangladeshi students should budget approximately..."

5. RELATED INFORMATION WITH CONTEXT:
   Connect to other relevant guidance with context
   Example: "Related to this, Bangladeshi students should also know about..."

6. SOURCE REFERENCE WITH CONTEXT:
   Verify information source with context
   Example: "This information is from Sharda University's official fee structure for international students 2025-26..."

MULTILINGUAL ELEMENTS (When Appropriate):
- Include "বাংলাদেশি শিক্ষার্থীদের জন্য (For Bangladeshi students)" 
- Use cultural terms where relevant
- Explain Indian system terminology for Bangladeshi context

CONTEXT VALIDATION CHECKLIST (Every Q&A Must Pass):
✓ University clearly specified
✓ Program/course clearly specified  
✓ "Bangladeshi students" mentioned
✓ "2025-26 academic year" specified
✓ Academic level context included
✓ Target audience clear
✓ Answer is extractive from source
✓ No generic or ambiguous statements

Return as JSON array with this exact structure:
```json
[
  {
    "question": "Complete question with full context specification",
    "answer": "Extractive answer with complete context preservation and specific details",
    "type": "question_type (direct_info/process/comparative/eligibility/financial/practical/problem_solution/scenario)",
    "confidence": 0.0-1.0,
    "university_context": ["specific_university_names"],
    "program_context": ["specific_programs"],
    "academic_level_context": ["specific_levels"],
    "student_background_context": "bangladeshi_students",
    "timeline_context": "2025-26",
    "audience_context": ["specific_audience"],
    "extractive_score": 0.0-1.0,
    "context_completeness_score": 0.0-1.0,
    "multilingual_keywords": ["relevant_bengali_terms"],
    "source_traceability": "specific_source_section"
  }
]
```

QUALITY GATES:
- Every answer must be 70%+ extractive from source text
- Every Q&A must include all 6 mandatory context elements
- No generic statements without source backing
- Cultural sensitivity maintained throughout
- Timeline accuracy verified (2025-26 data only)"""

    @staticmethod
    def get_comparative_analysis_prompt() -> str:
        """Get prompt for comparative analysis across universities."""
        return """Generate comparative question-answer pairs analyzing multiple universities and programs for Bangladeshi students applying for the 2025-26 academic year.

SOURCE CONTENT FOR COMPARISON:
```
{combined_source_text}
```

UNIVERSITIES TO COMPARE: {universities_list}
PROGRAMS TO COMPARE: {programs_list}
COMPARISON FOCUS: {comparison_focus}

MANDATORY COMPARATIVE CONTEXT SPECIFICATIONS:
1. University Comparison: Specify exactly which universities are being compared
2. Program Comparison: Specify exact programs being compared
3. Criteria Context: Specify comparison criteria (fees, quality, placement, etc.)
4. Student Background: Always "for Bangladeshi students"
5. Timeline: Always "for 2025-26 academic year"
6. Decision Framework: Provide clear decision guidance

COMPARATIVE QUESTION TYPES:

1. DIRECT COMPARISON:
   "Which university has lower B.Tech CSE fees for Bangladeshi students: Sharda University or Galgotias University for 2025-26?"

2. MULTI-CRITERIA COMPARISON:
   "Comparing Sharda, Amity, and Galgotias Universities for B.Tech CSE, which offers the best value for Bangladeshi students in 2025-26?"

3. FINANCIAL COMPARISON:
   "What are the total 4-year cost differences between Sharda University and Amity University for B.Tech CSE for Bangladeshi students in 2025-26?"

4. PROGRAM COMPARISON:
   "Which university offers better B.Tech specializations for Bangladeshi students: Sharda's AI/ML focus or Amity's industry partnerships for 2025-26?"

5. PRACTICAL COMPARISON:
   "For Bangladeshi students with limited budget, which is better: Sharda University's scholarship opportunities or G.L. Bajaj's lower fees for B.Tech in 2025-26?"

COMPARATIVE ANSWER STRUCTURE:
1. Direct Comparison Result with Context
2. Specific Data Points from Each University
3. Criteria-Based Analysis
4. Practical Implications for Bangladeshi Students
5. Decision Recommendation with Rationale
6. Related Considerations

Generate {num_questions} comparative Q&A pairs with complete source traceability."""

    @staticmethod
    def get_multilingual_enhancement_prompt() -> str:
        """Get prompt for multilingual enhancement."""
        return """Enhance this Q&A pair with appropriate multilingual support and cultural context for Bangladeshi students.

ORIGINAL Q&A:
Question: {question}
Answer: {answer}
Context: {context_metadata}

ENHANCEMENT REQUIREMENTS:
1. Add Bengali terms where culturally appropriate and helpful
2. Include cultural considerations specific to Bangladeshi students
3. Explain Indian education system terms that may be unfamiliar
4. Add transliteration for key technical terms
5. Maintain complete context specification
6. Preserve extractive nature of the answer

CULTURAL CONTEXT ADDITIONS:
- Bengali community aspects in Indian universities
- Cultural festivals and religious considerations
- Food and lifestyle adaptations for Bangladeshi students
- Family communication and involvement patterns
- Financial planning from Bangladeshi perspective

MULTILINGUAL ELEMENTS TO INCLUDE:
- Key Bengali terms: শিক্ষার্থী (student), বিশ্ববিদ্যালয় (university), ভর্তি (admission)
- Cultural bridging terms: "বাংলাদেশি শিক্ষার্থীদের জন্য"
- Technical term explanations: Credit system, CGPA calculation, etc.
- Process explanations: FRRO, C-Form, etc.

Return enhanced version maintaining full context:
```json
{
  "enhanced_question": "Question with appropriate multilingual elements",
  "enhanced_answer": "Answer with cultural context and Bengali terms where helpful",
  "bengali_keywords": ["key terms in Bengali with English translations"],
  "cultural_notes": ["important cultural considerations for Bangladeshi students"],
  "terminology_explanations": ["Indian system explanations adapted for Bangladeshi context"],
  "context_preservation_score": 0.0-1.0
}
```"""

    @staticmethod
    def get_quality_validation_prompt() -> str:
        """Get prompt for quality validation of context-rich Q&A."""
        return """Validate this Q&A pair for context completeness and extractive accuracy.

SOURCE TEXT:
```
{source_text}
```

Q&A TO VALIDATE:
Question: {question}
Answer: {answer}
Context Metadata: {context_metadata}

VALIDATION CRITERIA (Score 0.0-1.0 for each):

1. EXTRACTIVE VALIDATION:
   - Is answer completely extracted from source text?
   - Are there any additions or interpretations?
   - Word overlap percentage with source?

2. CONTEXT COMPLETENESS:
   - University context clearly specified?
   - Program context clearly specified?
   - Student background ("Bangladeshi students") included?
   - Timeline ("2025-26 academic year") specified?
   - Academic level context included?
   - Audience context clear?

3. ACCURACY VALIDATION:
   - All facts verifiable in source text?
   - No contradictions with source material?
   - Timeline accuracy maintained?

4. CLARITY AND ACTIONABILITY:
   - Question clearly posed?
   - Answer provides actionable guidance?
   - Context eliminates ambiguity?

5. CULTURAL APPROPRIATENESS:
   - Suitable for Bangladeshi students?
   - Cultural sensitivity maintained?
   - Appropriate terminology used?

Return detailed validation:
```json
{
  "extractive_score": 0.0-1.0,
  "context_completeness_score": 0.0-1.0,
  "accuracy_score": 0.0-1.0,
  "clarity_score": 0.0-1.0,
  "cultural_appropriateness_score": 0.0-1.0,
  "overall_quality_score": 0.0-1.0,
  "university_context_clear": true/false,
  "program_context_clear": true/false,
  "student_background_clear": true/false,
  "timeline_context_clear": true/false,
  "academic_level_clear": true/false,
  "audience_context_clear": true/false,
  "issues_identified": ["specific problems found"],
  "improvement_suggestions": ["specific recommendations"],
  "source_traceability": "percentage of answer traceable to source",
  "context_gaps": ["missing context elements"],
  "validation_passed": true/false
}
```"""

    @staticmethod
    def get_scenario_based_prompt() -> str:
        """Get prompt for scenario-based Q&A generation."""
        return """Generate scenario-based question-answer pairs using real-world situations that Bangladeshi students face when applying to Indian universities for the 2025-26 academic year.

SOURCE TEXT:
```
{source_text}
```

STUDENT SCENARIOS TO ADDRESS:
{student_scenarios}

SCENARIO CATEGORIES:
1. Academic Background Scenarios (HSC, Diploma, various CGPA levels)
2. Financial Constraint Scenarios (limited budget, scholarship needs)
3. Program Selection Scenarios (career goals, specialization choices)
4. Application Process Scenarios (documentation, deadlines, procedures)
5. Visa and Legal Scenarios (visa rejection, documentation issues)
6. Accommodation Scenarios (hostel vs off-campus, safety concerns)
7. Cultural Adaptation Scenarios (food, community, festivals)
8. Family Involvement Scenarios (parent concerns, family planning)

SCENARIO-BASED QUESTION STRUCTURE:
"I am a Bangladeshi student with [specific background]. I want to [specific goal] at [specific university] for [specific program] in 2025-26. [Specific challenge/question]?"

SCENARIO-BASED ANSWER STRUCTURE:
1. Acknowledge specific scenario context
2. Provide extractive guidance from source
3. Address specific challenges mentioned
4. Give step-by-step actionable advice
5. Include relevant context (university, program, timeline)
6. Mention related considerations
7. Provide follow-up guidance if needed

Example Scenarios:
- "I have CGPA 3.2 in HSC and want to study B.Tech CSE at Sharda University. What scholarship can I get and what will be my total cost for 2025-26?"
- "My visa was rejected once. How can I reapply for Sharda University's B.Tech program for 2025-26 session?"
- "I'm a diploma holder in engineering. Can I apply for lateral entry to B.Tech at multiple universities for 2025-26?"

Generate {num_questions} scenario-based Q&A pairs with complete context specification."""


class ContextValidationRules:
    """Validation rules for context-rich Q&A pairs."""
    
    REQUIRED_CONTEXT_ELEMENTS = [
        "university_specification",
        "program_specification", 
        "student_background_specification",
        "timeline_specification",
        "academic_level_specification",
        "audience_specification"
    ]
    
    FORBIDDEN_PHRASES = [
        "generally", "usually", "typically", "in most cases",
        "often", "sometimes", "may", "might", "could be",
        "probably", "likely", "tends to", "commonly"
    ]
    
    REQUIRED_PHRASES = [
        "for bangladeshi students",
        "for 2025-26 academic year", 
        "at [university name]",
        "for [program name]"
    ]
    
    MINIMUM_EXTRACTIVE_OVERLAP = 0.70  # 70% word overlap with source
    MINIMUM_CONTEXT_COMPLETENESS = 0.85  # 85% context elements present
    MINIMUM_OVERALL_QUALITY = 0.80  # 80% overall quality score


class ContextEnhancementStrategies:
    """Strategies for enhancing context in educational Q&A."""
    
    @staticmethod
    def get_university_context_patterns() -> Dict[str, List[str]]:
        """Get patterns for university context enhancement."""
        return {
            "sharda_university": [
                "Greater Noida campus", "IIT-aligned curriculum", "merit-based scholarships",
                "50% scholarship for CGPA 3.5+", "direct admission for HSC",
                "lateral entry for diploma holders", "4-year B.Tech program"
            ],
            "amity_university": [
                "Noida campus", "premium education", "3-continent program",
                "100% scholarship for 93%+", "strong industry connections",
                "international exposure", "video interview required"
            ],
            "galgotias_university": [
                "affordable fees", "industry partnerships", "modern infrastructure",
                "100% scholarship for 95%+", "strong placement record",
                "diverse program offerings", "student-friendly environment"
            ]
        }
    
    @staticmethod
    def get_program_context_patterns() -> Dict[str, List[str]]:
        """Get patterns for program context enhancement."""
        return {
            "btech_cse": [
                "4-year duration", "8 semesters", "industry-relevant curriculum",
                "AI/ML specializations", "software development focus",
                "placement in IT companies", "project-based learning"
            ],
            "lateral_entry": [
                "3-year duration", "for diploma holders", "direct 2nd year admission",
                "engineering diploma required", "credit transfer",
                "accelerated program", "industry experience valued"
            ],
            "scholarship_programs": [
                "merit-based", "CGPA requirements", "annual renewal",
                "maintain 75% attendance", "no backlogs allowed",
                "tuition fee waiver", "performance-based continuation"
            ]
        }
    
    @staticmethod
    def get_cultural_context_elements() -> Dict[str, List[str]]:
        """Get cultural context elements for Bangladeshi students."""
        return {
            "food_culture": [
                "halal food availability", "Bengali cuisine options",
                "rice-based meals", "fish preparations",
                "vegetarian alternatives", "campus food courts"
            ],
            "religious_practices": [
                "prayer facilities", "mosque access", "Friday prayers",
                "Eid celebrations", "Ramadan considerations",
                "religious holidays", "community gatherings"
            ],
            "cultural_adaptation": [
                "Bengali community", "cultural festivals",
                "language similarities", "Hindi-Bengali connection",
                "family involvement", "parent communication"
            ]
        }
