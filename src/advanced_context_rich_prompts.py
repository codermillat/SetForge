"""
Advanced Context-Rich Prompt Templates for Educational Q&A Generation
Implements comprehensive prompt engineering strategies with mandatory context elements,
complete source attribution, and cultural sensitivity for Bangladeshi students.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class PromptType(Enum):
    """Types of context-rich prompts for different educational scenarios."""
    CONTEXT_EXTRACTION = "context_extraction"
    FINANCIAL_ANALYSIS = "financial_analysis"
    PROCESS_DOCUMENTATION = "process_documentation"
    COMPARATIVE_ANALYSIS = "comparative_analysis"
    MULTILINGUAL_ENHANCEMENT = "multilingual_enhancement"
    SOURCE_ATTRIBUTION = "source_attribution"
    CULTURAL_ADAPTATION = "cultural_adaptation"


@dataclass
class ContextRequirements:
    """Mandatory context requirements for Q&A generation."""
    universities: List[str]
    programs: List[str]
    student_background: str = "bangladeshi_students"
    timeline: str = "2025-26"
    academic_levels: Optional[List[str]] = None
    audiences: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.academic_levels is None:
            self.academic_levels = ["SSC", "HSC", "Diploma", "Bachelor's"]
        if self.audiences is None:
            self.audiences = ["students", "parents", "agents"]


@dataclass
class SourceRequirements:
    """Mandatory source attribution requirements."""
    data_source_file: str
    original_source: str
    source_url: str
    verification_date: str = "January 2025"
    source_type: str = "official_document"


class AdvancedContextRichPromptTemplates:
    """Advanced prompt templates with comprehensive context and source attribution."""
    
    def __init__(self):
        self.mandatory_context_elements = [
            "university",
            "program", 
            "student_background",
            "timeline",
            "academic_level",
            "audience"
        ]
        
        self.mandatory_source_elements = [
            "data_source_file",
            "original_source",
            "source_url",
            "verification_date",
            "source_type"
        ]
        
        self.bengali_keywords = {
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
    
    def get_master_system_prompt(self) -> str:
        """Get the master system prompt with complete context and source requirements."""
        return """You are an expert educational guidance specialist for Bangladeshi students seeking university admission in India. Your task is to generate comprehensive, context-rich question-answer pairs with complete source attribution that provide accurate, culturally sensitive guidance.

CRITICAL REQUIREMENTS - 100% COMPLIANCE MANDATORY:

1. MANDATORY CONTEXT ELEMENTS (ALL Q&A MUST INCLUDE):
   ✓ UNIVERSITY CONTEXT: Always specify exact university (Sharda, Amity, Galgotias, G.L. Bajaj, NIU)
   ✓ PROGRAM CONTEXT: Always specify exact program (B.Tech CSE, BCA, BBA, etc.)
   ✓ STUDENT BACKGROUND: Always include "for Bangladeshi students"
   ✓ TIMELINE CONTEXT: Always include "for 2025-26 academic year"
   ✓ ACADEMIC LEVEL: Always specify education level (SSC/HSC/Diploma/Bachelor's)
   ✓ AUDIENCE CONTEXT: Always specify target audience (students/parents/agents)

2. MANDATORY SOURCE ATTRIBUTION (ALL Q&A MUST INCLUDE):
   ✓ DATA SOURCE FILE: Exact .txt file name where information was extracted
   ✓ ORIGINAL SOURCE: Official source document or website
   ✓ SOURCE URL: Official website URL or document reference
   ✓ VERIFICATION DATE: When information was last verified (January 2025)
   ✓ SOURCE TYPE: Type of source (official brochure/website/government document)

3. EXTRACTIVE REQUIREMENTS (ZERO HALLUCINATION):
   ✓ All answers MUST be directly extracted from source text
   ✓ Use exact wording from source with proper context specification
   ✓ NO additions, interpretations, or inferences beyond source
   ✓ Maintain complete traceability to specific source sentences
   ✓ Preserve context clarity throughout the answer

4. CULTURAL SENSITIVITY REQUIREMENTS:
   ✓ Include Bengali terms where culturally relevant
   ✓ Explain Indian education system terms for Bangladeshi context
   ✓ Address cultural concerns specific to Bangladeshi students
   ✓ Use respectful, supportive language acknowledging challenges
   ✓ Include transliteration for key terms when helpful

FORBIDDEN PRACTICES:
❌ Generic answers without specific context
❌ Information not explicitly stated in source
❌ Context-ambiguous statements
❌ Assumptions about unstated information
❌ Phrases like "generally", "usually", "typically" without source basis
❌ Missing university, program, or student background specification
❌ Incomplete source attribution
❌ Cultural insensitivity or stereotyping

QUALITY STANDARDS:
• Accuracy: 100% alignment with source data
• Completeness: All mandatory elements present
• Clarity: Understandable by target audience
• Actionability: Specific, implementable guidance
• Cultural Relevance: Appropriate for Bangladeshi students
• Source Reliability: Verified official sources only"""

    def get_context_extraction_prompt(self, 
                                    source_text: str,
                                    context_requirements: ContextRequirements,
                                    source_requirements: SourceRequirements,
                                    num_questions: int = 5) -> str:
        """Generate context-rich extraction prompt with mandatory elements."""
        
        return f"""Generate {num_questions} comprehensive, context-rich question-answer pairs from the educational guidance text below.

SOURCE TEXT:
```
{source_text}
```

MANDATORY CONTEXT SPECIFICATIONS FOR ALL Q&A:
🎯 Universities: {', '.join(context_requirements.universities)}
🎯 Programs: {', '.join(context_requirements.programs)}
🎯 Student Background: {context_requirements.student_background}
🎯 Timeline: {context_requirements.timeline}
🎯 Academic Levels: {', '.join(context_requirements.academic_levels or [])}
🎯 Target Audiences: {', '.join(context_requirements.audiences or [])}

MANDATORY SOURCE ATTRIBUTION FOR ALL Q&A:
📄 Data Source File: {source_requirements.data_source_file}
📄 Original Source: {source_requirements.original_source}
📄 Source URL: {source_requirements.source_url}
📄 Verification Date: {source_requirements.verification_date}
📄 Source Type: {source_requirements.source_type}

QUESTION TYPES TO GENERATE WITH FULL CONTEXT:

1. 💰 FINANCIAL QUESTIONS (with specific amounts and context):
   Example: "What is the annual tuition fee for B.Tech CSE at Sharda University for Bangladeshi students in the 2025-26 academic year?"

2. 📋 PROCESS QUESTIONS (with step-by-step context):
   Example: "What is the complete admission process for Bangladeshi HSC graduates applying to B.Tech programs at Sharda University for 2025-26?"

3. ⚖️ COMPARATIVE QUESTIONS (with multi-university context):
   Example: "Which university offers better value for B.Tech CSE programs for Bangladeshi students: Sharda University or Amity University for 2025-26?"

4. ✅ ELIGIBILITY QUESTIONS (with specific requirements and context):
   Example: "What are the eligibility requirements for Bangladeshi diploma holders to apply for lateral entry to B.Tech at Sharda University?"

5. 🏠 PRACTICAL QUESTIONS (with cultural context):
   Example: "How do Bangladeshi students open a bank account while studying B.Tech at Sharda University in India?"

6. 📈 CAREER QUESTIONS (with ROI context):
   Example: "What are the post-graduation opportunities for Bangladeshi students completing B.Tech CSE from Sharda University?"

ANSWER STRUCTURE WITH COMPLETE CONTEXT AND DETAILED INFORMATION:

1. 🎯 DETAILED DIRECT ANSWER: 
   - Start with comprehensive answer including full context
   - Include year-wise breakdowns for financial information
   - Provide step-by-step details for processes
   - Include specific amounts, dates, and requirements

2. 🏛️ CONTEXT SPECIFICATION: 
   - Clearly state university, program, student type
   - Specify academic year and timeline
   - Include target audience specification

3. 📊 COMPREHENSIVE SUPPORTING DETAILS:
   - Additional context-aware information from source
   - Year-wise fee breakdowns (1st year, 2nd year, 3rd year, 4th year)
   - Complete cost analysis including all expenses
   - Scholarship calculations with exact savings
   - Currency conversion to Bangladeshi Taka

4. 🌍 CULTURAL AND PRACTICAL IMPLICATIONS:
   - What this means for Bangladeshi students specifically
   - Cultural considerations and practical advice
   - Family communication and planning guidance

5. 🔗 RELATED CONTEXTUAL INFORMATION:
   - Connect to other relevant context-aware guidance
   - Cross-references to related policies or procedures
   - Comparative information where applicable

6. 📚 COMPLETE SOURCE VERIFICATION:
   - Root website URLs (https://sharda.ac.in/, https://amity.edu/)
   - Complete attribution with reliability indicators
   - Verification dates and source types

DETAILED ANSWER EXAMPLES:

Example Financial Question: "What is the annual tuition fee for B.Tech CSE at Sharda University for Bangladeshi students in the 2025-26 academic year?"

Example DETAILED Answer Format:
"For Bangladeshi students applying to B.Tech Computer Science & Engineering (CSE) at Sharda University for the 2025-26 academic year, the comprehensive fee structure is:

**Year-wise Tuition Fee Breakdown (ACTUAL 2025-26 Rates):**
• 1st Year: ₹2,80,000
• 2nd Year: ₹2,88,400 (3% annual increase)
• 3rd Year: ₹2,97,052 (3% annual increase)
• 4th Year: ₹3,05,964 (3% annual increase)

**Complete Annual Cost Analysis:**
• Annual Tuition: ₹2,80,000-₹3,05,964 (progressive increase)
• Hostel Accommodation: ₹80,000-₹1,20,000 per year
• Mess/Food Charges: ₹40,000 per year
• Academic Materials: ₹15,000 per year
• Other Expenses: ₹35,000 per year

**Total Annual Cost: ₹4,50,000-₹5,15,964**
**Complete 4-Year Program: ₹18,91,416-₹20,11,416**

**Scholarship Opportunities:**
• 50% tuition scholarship for CGPA 3.5+ (saves ₹5,85,708 over 4 years)
• 20% tuition scholarship for CGPA 3.0-3.4 (saves ₹2,34,283 over 4 years)

**In Bangladeshi Taka (Approximate):**
• Total cost: ~23.6-25.1 lakh BDT
• With 50% scholarship: ~14.3-15.1 lakh BDT"

**SOURCE ATTRIBUTION REQUIREMENTS:**
• source_url: Use ROOT website domains only:
  - Sharda University: "https://sharda.ac.in/"
  - Amity University: "https://amity.edu/"
  - Galgotias University: "https://galgotias.ac.in/"
  - G.L. Bajaj Institute: "https://glbajaj.ac.in/"
  - Noida International University: "https://niu.edu.in/"
• verification_date: "January 2025"
• source_type: "official_university_website" or "official_university_brochure"
• source_reliability: 0.95 for official university sources

Each Q&A MUST include these detailed context specifications:
• University: "at [Specific University Name]"
• Program: "for [Specific Program Name]" 
• Student Background: "for Bangladeshi students"
• Timeline: "for 2025-26 academic year"
• Academic Level: "HSC/Diploma/Bachelor's students"
• Audience: "students should know" or "parents should understand"

MULTILINGUAL INTEGRATION:
• Include Bengali terms: শিক্ষার্থী (student), বিশ্ববিদ্যালয় (university)
• Add cultural context: "বাংলাদেশি শিক্ষার্থীদের জন্য" (for Bangladeshi students)
• Explain Indian terms in Bangladeshi context

Return as JSON array with this exact structure:
```json
[
  {{
    "question": "context-rich question with all mandatory specifications",
    "answer": "extractive answer with complete context preservation and cultural sensitivity",
    "question_type": "financial/process/comparative/eligibility/practical/career",
    "confidence": 0.0-1.0,
    "context_metadata": {{
      "university_context": ["specific_universities"],
      "program_context": ["specific_programs"],
      "student_background_context": "bangladeshi_students",
      "timeline_context": "2025-26",
      "academic_level_context": ["relevant_levels"],
      "audience_context": ["target_audiences"],
      "multilingual_keywords": {{"bengali_term": "english_equivalent"}},
      "cultural_considerations": ["cultural_notes"]
    }},
    "source_attribution": {{
      "data_source_file": "{source_requirements.data_source_file}",
      "original_source": "{source_requirements.original_source}",
      "source_url": "{source_requirements.source_url}",
      "verification_date": "{source_requirements.verification_date}",
      "source_type": "{source_requirements.source_type}",
      "source_reliability": 0.0-1.0,
      "extracted_from_sentences": ["specific source sentences used"]
    }},
    "quality_metrics": {{
      "context_completeness": 0.0-1.0,
      "extractive_accuracy": 0.0-1.0,
      "cultural_sensitivity": 0.0-1.0,
      "actionability": 0.0-1.0
    }}
  }}
]
```

GENERATE COMPREHENSIVE Q&A COVERING DIFFERENT SCENARIOS AND ENSURE 100% CONTEXT COMPLETENESS AND SOURCE ATTRIBUTION."""

    def get_financial_analysis_prompt(self, 
                                    financial_content: str,
                                    context_requirements: ContextRequirements,
                                    source_requirements: SourceRequirements) -> str:
        """Generate detailed financial analysis prompt with comprehensive cost breakdowns."""
        
        return f"""Generate comprehensive financial planning Q&A pairs with DETAILED, YEAR-WISE cost analysis and complete scholarship calculations for Bangladeshi students.

FINANCIAL CONTENT:
```
{financial_content}
```

CONTEXT REQUIREMENTS:
🎯 Universities: {', '.join(context_requirements.universities)}
🎯 Programs: {', '.join(context_requirements.programs)}
🎯 Student Background: {context_requirements.student_background}
🎯 Timeline: {context_requirements.timeline}

DETAILED ANSWER REQUIREMENTS:

1. 💰 COMPREHENSIVE COST BREAKDOWN FORMAT:
Example Question: "What is the annual tuition fee for B.Tech CSE at Sharda University for Bangladeshi students in the 2025-26 academic year?"

Example DETAILED Answer Format:
"For Bangladeshi students applying to B.Tech Computer Science & Engineering (CSE) at Sharda University for the 2025-26 academic year, the comprehensive fee structure is as follows:

**Year-wise Tuition Fee Breakdown (ACTUAL 2025-26 Rates):**
• 1st Year: ₹2,80,000
• 2nd Year: ₹2,88,400 (3% annual increase)
• 3rd Year: ₹2,97,052 (3% annual increase)
• 4th Year: ₹3,05,964 (3% annual increase)

**Total 4-Year Tuition:** ₹11,71,416

**Additional Annual Costs:**
• Hostel Accommodation: ₹80,000-₹1,20,000 per year
• Mess/Food Charges: ₹40,000 per year
• Books & Study Materials: ₹15,000 per year
• Laboratory & Library Fees: ₹10,000 per year
• Medical Insurance: ₹5,000 per year
• Miscellaneous Expenses: ₹20,000 per year

**Annual Total Cost (Including All Expenses):** ₹4,50,000-₹5,15,964
**Complete 4-Year Program Cost:** ₹19,31,416-₹20,11,416

**Scholarship Opportunities for Bangladeshi Students:**
• CGPA 3.5-5.0: 50% scholarship on tuition fee (saves ₹5,85,708 over 4 years)
• CGPA 3.0-3.4: 20% scholarship on tuition fee (saves ₹2,34,283 over 4 years)

**Cost in Bangladeshi Taka (Approximate):**
• Total 4-year cost: ₹19,31,416-₹20,11,416 = ~24.1-25.1 lakh BDT
• With 50% scholarship: ₹13,45,708-₹14,25,708 = ~16.8-17.8 lakh BDT

This fee structure reflects the actual 2025-26 rates with progressive annual increases and provides excellent value for the world-class education and facilities."

2. � SCHOLARSHIP DETAILED ANALYSIS FORMAT:
Include exact savings calculations, CGPA maintenance requirements, scholarship continuation policies, and impact on total program cost.

3. � COMPARATIVE ANALYSIS FORMAT:
Provide detailed comparison tables with year-wise costs, scholarship opportunities, and total savings for each university option.

MANDATORY DETAILED ELEMENTS TO INCLUDE:
• Year-wise fee breakdown (1st, 2nd, 3rd, 4th year specifics)
• Complete cost analysis including all expenses
• Exact scholarship calculations with savings amounts
• Currency conversion to Bangladeshi Taka
• Payment schedules and deadlines
• Hidden costs and additional expenses
• Practical financial planning advice
• Comparison with other universities where relevant

SOURCE ATTRIBUTION REQUIREMENTS:
• source_url: Use root website domain (https://sharda.ac.in/, https://amity.edu/, https://galgotias.ac.in/)
• verification_date: January 2025
• source_type: official_university_website or official_university_brochure
📄 Data Source: {source_requirements.data_source_file}
📄 Original Source: {source_requirements.original_source}
📄 Verification: {source_requirements.verification_date}

Return financial Q&A with complete cost breakdowns, exact calculations, and cultural context for Bangladeshi families."""

    def get_process_documentation_prompt(self,
                                       process_content: str,
                                       context_requirements: ContextRequirements,
                                       source_requirements: SourceRequirements) -> str:
        """Generate process documentation prompt with step-by-step guidance."""
        
        return f"""Generate comprehensive process documentation Q&A with detailed step-by-step guidance for Bangladeshi students.

PROCESS CONTENT:
```
{process_content}
```

CONTEXT REQUIREMENTS:
🎯 Universities: {', '.join(context_requirements.universities)}
🎯 Programs: {', '.join(context_requirements.programs)}
🎯 Student Background: {context_requirements.student_background}
🎯 Timeline: {context_requirements.timeline}

PROCESS Q&A TYPES TO GENERATE:

1. 📋 ADMISSION PROCESS:
   "What is the complete step-by-step admission process for Bangladeshi HSC graduates applying to B.Tech CSE at Sharda University for 2025-26?"

2. 🛂 VISA APPLICATION:
   "What is the detailed visa application process for Bangladeshi students admitted to B.Tech programs at Sharda University?"

3. 🏛️ FRRO REGISTRATION:
   "How do Bangladeshi students complete FRRO registration after arriving at Sharda University for B.Tech studies?"

4. 🏦 BANK ACCOUNT OPENING:
   "What is the step-by-step process for Bangladeshi students to open a bank account while studying at Sharda University?"

5. 🎓 SCHOLARSHIP APPLICATION:
   "How do Bangladeshi students apply for and maintain merit scholarships at Sharda University for B.Tech programs?"

6. 📚 LATERAL ENTRY PROCESS:
   "What is the complete lateral entry process for Bangladeshi diploma holders applying to 2nd year B.Tech at Sharda University?"

PROCESS DOCUMENTATION STRUCTURE:
1. 🎯 OVERVIEW: Brief summary with context
2. 📋 PREREQUISITES: Required documents and eligibility
3. 📝 STEP-BY-STEP PROCEDURE: Detailed numbered steps
4. ⏰ TIMELINES: Deadlines and processing times
5. 💰 COSTS: Associated fees and expenses
6. 📞 CONTACTS: Specific office contacts and support
7. ⚠️ IMPORTANT NOTES: Cultural considerations and tips
8. 🔄 FOLLOW-UP: Next steps and ongoing requirements

CULTURAL CONSIDERATIONS FOR BANGLADESHI STUDENTS:
• Document authentication requirements
• Language barriers and translation needs
• Cultural adaptation challenges
• Family communication expectations
• Religious and dietary considerations
• Peer support and community connections

SOURCE ATTRIBUTION:
📄 Process Source: {source_requirements.data_source_file}
📄 Official Reference: {source_requirements.original_source}
📄 Verification Date: {source_requirements.verification_date}

Generate process Q&A with complete step-by-step guidance, cultural sensitivity, and practical tips for successful completion."""

    def get_comparative_analysis_prompt(self,
                                      comparative_content: str,
                                      context_requirements: ContextRequirements,
                                      source_requirements: SourceRequirements) -> str:
        """Generate comparative analysis prompt for multi-university decisions."""
        
        return f"""Generate comprehensive comparative analysis Q&A for informed university selection decisions by Bangladeshi students.

COMPARATIVE CONTENT:
```
{comparative_content}
```

UNIVERSITIES FOR COMPARISON: {', '.join(context_requirements.universities)}
PROGRAMS FOR COMPARISON: {', '.join(context_requirements.programs)}
STUDENT CONTEXT: {context_requirements.student_background}
TIMELINE: {context_requirements.timeline}

COMPARATIVE ANALYSIS Q&A TYPES:

1. 🏛️ UNIVERSITY COMPARISON:
   "Which university offers better overall value for Bangladeshi students: Sharda University vs Amity University for B.Tech CSE in 2025-26?"

2. 💰 COST COMPARISON:
   "What are the total cost differences between studying B.Tech at Sharda University vs Galgotias University for Bangladeshi students over 4 years?"

3. 🎓 PROGRAM COMPARISON:
   "How do the B.Tech CSE programs at Sharda University and G.L. Bajaj Institute compare for Bangladeshi students in terms of curriculum and opportunities?"

4. 🌍 INTERNATIONAL EXPOSURE:
   "Which university provides better international exposure and diversity for Bangladeshi students: Sharda University or NIU?"

5. 🏆 ROI COMPARISON:
   "Which university offers better return on investment for Bangladeshi students: Amity University vs Galgotias University for B.Tech programs?"

6. 🏠 CAMPUS LIFE COMPARISON:
   "How do campus facilities and student life compare between Sharda University and Amity University for Bangladeshi students?"

COMPARISON FRAMEWORK:
🔸 ACADEMIC EXCELLENCE
  - NAAC ratings and accreditation
  - Faculty qualifications and research
  - Curriculum alignment with industry
  - Placement statistics and opportunities

🔸 FINANCIAL CONSIDERATIONS
  - Total program costs with all expenses
  - Scholarship availability and criteria
  - Payment flexibility and options
  - Value for money assessment

🔸 INTERNATIONAL EXPOSURE
  - International student diversity
  - Global partnership programs
  - Study abroad opportunities
  - Cross-cultural learning environment

🔸 STUDENT SUPPORT SERVICES
  - Bangladeshi student community size
  - Cultural adaptation support
  - Academic mentoring programs
  - Career guidance and placement

🔸 PRACTICAL FACTORS
  - Location and accessibility
  - Hostel facilities and food options
  - Safety and security measures
  - Alumni network strength

DECISION MATRICES TO INCLUDE:
| Criteria | University A | University B | Winner |
|----------|--------------|--------------|---------|
| Academic Quality | X/10 | Y/10 | Better Option |
| Total Cost | ₹X Lakhs | ₹Y Lakhs | More Affordable |
| Scholarships | X% available | Y% available | Better Aid |

CULTURAL CONTEXT FOR BANGLADESHI STUDENTS:
• Bangladeshi student community presence
• Cultural celebration and religious facilities
• Food preferences and dietary accommodations
• Language support and communication ease
• Family visit convenience and accessibility

SOURCE ATTRIBUTION:
📄 Comparison Data: {source_requirements.data_source_file}
📄 Official Sources: {source_requirements.original_source}
📄 Verification: {source_requirements.verification_date}

Generate comparative Q&A with data-driven analysis, clear decision matrices, and cultural considerations for informed choice-making."""

    def get_multilingual_enhancement_prompt(self,
                                          qa_content: str,
                                          context_requirements: ContextRequirements) -> str:
        """Generate multilingual enhancement prompt for Bengali-English integration."""
        
        return f"""Enhance the following Q&A content with comprehensive Bengali-English multilingual support and cultural context for Bangladeshi students.

ORIGINAL Q&A CONTENT:
```
{qa_content}
```

ENHANCEMENT REQUIREMENTS:

1. 🌍 MULTILINGUAL INTEGRATION:
   • Add relevant Bengali terms with English explanations
   • Include transliteration for key university and program names
   • Use "বাংলাদেশি শিক্ষার্থীদের জন্য" where appropriate
   • Integrate cultural phrases that resonate with Bangladeshi families

2. 📚 EDUCATIONAL SYSTEM TRANSLATION:
   • Explain Indian education terms in Bangladeshi context
   • Provide equivalent qualifications and standards
   • Clarify grading systems and academic terminology
   • Bridge understanding between education systems

3. 🏛️ CULTURAL SENSITIVITY ENHANCEMENT:
   • Address common concerns of Bangladeshi parents
   • Include cultural adaptation guidance
   • Acknowledge religious and dietary considerations
   • Provide community connection opportunities

4. 💬 LANGUAGE ACCESSIBILITY:
   • Simplify complex administrative language
   • Provide Bengali explanations for technical terms
   • Include pronunciation guides for important names
   • Add cultural context for formal procedures

BENGALI-ENGLISH KEYWORD INTEGRATION:
• শিক্ষার্থী (Shikkharthi) = Student
• বিশ্ববিদ্যালয় (Bishwobidyaloy) = University
• ভর্তি (Bhorti) = Admission
• বৃত্তি (Britti) = Scholarship
• শিক্ষা (Shikkha) = Education
• ডিগ্রি (Degree) = Degree
• কোর্স (Course) = Course
• ফি (Fee) = Fee
• খরচ (Khoroch) = Cost
• ভিসা (Visa) = Visa

CULTURAL CONTEXT ELEMENTS:
🕌 Religious Considerations:
• Prayer facilities and Islamic community
• Halal food availability and dining options
• Religious holiday accommodations
• Islamic cultural practices support

👨‍👩‍👧‍👦 Family Dynamics:
• Parent involvement expectations
• Family communication preferences
• Decision-making cultural patterns
• Extended family consultation norms

🍽️ Food and Lifestyle:
• Bengali cuisine availability
• Dietary restrictions accommodation
• Community gathering spaces
• Cultural celebration participation

📞 Communication Styles:
• Respectful addressing patterns
• Formal vs informal communication
• Family update expectations
• Emergency contact protocols

ENHANCED OUTPUT FORMAT:
```json
{{
  "enhanced_question": "Original question + Bengali keywords + cultural context",
  "enhanced_answer": "Original answer + cultural explanations + Bengali terms + practical cultural tips",
  "bengali_keywords": {{
    "bengali_term": "english_meaning_and_pronunciation"
  }},
  "cultural_notes": [
    "Important cultural considerations for Bangladeshi students and families"
  ],
  "terminology_explanations": [
    "Indian education system terms explained in Bangladeshi context"
  ],
  "practical_cultural_tips": [
    "Actionable advice for cultural adaptation and success"
  ],
  "community_connections": [
    "Ways to connect with Bangladeshi student community and cultural groups"
  ]
}}
```

Generate enhanced Q&A that maintains technical accuracy while adding meaningful cultural context and multilingual accessibility for Bangladeshi students and families."""

    def get_source_attribution_validation_prompt(self,
                                                qa_pair: Dict[str, Any],
                                                source_text: str,
                                                source_requirements: SourceRequirements) -> str:
        """Generate source attribution validation prompt."""
        
        return f"""Validate the source attribution completeness and accuracy for this Q&A pair.

Q&A PAIR TO VALIDATE:
```json
{qa_pair}
```

SOURCE TEXT:
```
{source_text}
```

REQUIRED SOURCE ATTRIBUTION ELEMENTS:
📄 Data Source File: {source_requirements.data_source_file}
📄 Original Source: {source_requirements.original_source}
📄 Source URL: {source_requirements.source_url}
📄 Verification Date: {source_requirements.verification_date}
📄 Source Type: {source_requirements.source_type}

VALIDATION CRITERIA:

1. ✅ EXTRACTIVE ACCURACY (Critical):
   • Is the answer completely extracted from the source text?
   • Are there any additions or interpretations beyond source?
   • Can every claim be traced to specific source sentences?
   • Is the context preserved accurately from source?

2. 📋 SOURCE ATTRIBUTION COMPLETENESS (Mandatory):
   • Are all 5 required source elements present?
   • Is the data source file correctly identified?
   • Is the original source accurately cited?
   • Is the source URL valid and relevant?
   • Is the verification date current and accurate?

3. 🎯 CONTEXT VERIFICATION (Essential):
   • Does the context match the source content?
   • Is university context correctly extracted?
   • Is program context accurately represented?
   • Is student background context appropriate?
   • Is timeline context current and relevant?

4. 🔍 RELIABILITY ASSESSMENT (Important):
   • Is the source authoritative and official?
   • Is the information current for 2025-26?
   • Are there any contradictions with other sources?
   • Is the source type correctly categorized?

Return comprehensive validation:
```json
{{
  "validation_results": {{
    "extractive_accuracy": {{
      "score": 0.0-1.0,
      "is_fully_extractive": true/false,
      "problematic_additions": ["any non-extractive content"],
      "source_sentence_mapping": ["specific sentences used"]
    }},
    "source_attribution_completeness": {{
      "score": 0.0-1.0,
      "missing_elements": ["any missing required elements"],
      "element_validation": {{
        "data_source_file": "correct/incorrect/missing",
        "original_source": "correct/incorrect/missing", 
        "source_url": "correct/incorrect/missing",
        "verification_date": "correct/incorrect/missing",
        "source_type": "correct/incorrect/missing"
      }}
    }},
    "context_verification": {{
      "score": 0.0-1.0,
      "university_context_accurate": true/false,
      "program_context_accurate": true/false,
      "student_background_appropriate": true/false,
      "timeline_context_current": true/false
    }},
    "reliability_assessment": {{
      "source_authority": 0.0-1.0,
      "information_currency": 0.0-1.0,
      "consistency_check": true/false,
      "overall_reliability": 0.0-1.0
    }},
    "overall_validation_score": 0.0-1.0,
    "issues_identified": ["specific problems found"],
    "improvement_recommendations": ["specific suggestions for enhancement"]
  }}
}}
```

Provide detailed validation with specific feedback for improvement."""

    def get_cultural_adaptation_prompt(self,
                                     content: str,
                                     context_requirements: ContextRequirements) -> str:
        """Generate cultural adaptation prompt for Bangladeshi student context."""
        
        return f"""Enhance the educational content with comprehensive cultural adaptation guidance specifically for Bangladeshi students studying in India.

EDUCATIONAL CONTENT:
```
{content}
```

CULTURAL ADAPTATION AREAS TO ADDRESS:

1. 🏛️ ACADEMIC CULTURE ADAPTATION:
   • Classroom participation expectations
   • Professor-student interaction norms
   • Group project and teamwork dynamics
   • Academic integrity and plagiarism awareness
   • Examination and assessment patterns

2. 🌍 SOCIAL INTEGRATION:
   • Making friends with diverse international students
   • Participating in university cultural events
   • Joining student clubs and organizations
   • Understanding Indian social customs
   • Building professional networks

3. 🍽️ LIFESTYLE ADJUSTMENTS:
   • Food options and dietary accommodations
   • Hostel life and roommate relationships
   • Personal safety and security awareness
   • Healthcare and medical facility access
   • Shopping and daily life management

4. 💬 COMMUNICATION ADAPTATION:
   • Language barriers and improvement strategies
   • Cultural communication differences
   • Formal vs informal interaction styles
   • Professional communication skills
   • Family communication expectations

5. 🏠 ACCOMMODATION AND LIVING:
   • Hostel vs off-campus living decisions
   • Roommate cultural dynamics
   • Personal space and privacy norms
   • Cleanliness and hygiene standards
   • Guest policies and family visits

6. 💰 FINANCIAL MANAGEMENT:
   • Banking and money transfer systems
   • Budgeting in Indian currency
   • Shopping and expense management
   • Emergency fund planning
   • Family financial communication

BANGLADESHI-SPECIFIC CONSIDERATIONS:

🇧🇩 CULTURAL BRIDGES:
• Shared Bengali language advantages
• Historical and cultural connections
• Similar food preferences and availability
• Religious practice similarities
• Family value alignments

⚡ POTENTIAL CHALLENGES:
• Different education system expectations
• Language accent and comprehension
• Cultural stereotype navigation
• Homesickness and family separation
• Academic pressure and competition

🤝 SUPPORT SYSTEMS:
• Bangladeshi student associations
• Cultural mentorship programs
• Senior student guidance networks
• University international support offices
• Community religious and cultural centers

PRACTICAL CULTURAL TIPS:

📚 Academic Success:
• Participate actively in class discussions
• Build relationships with professors and TAs
• Form study groups with diverse students
• Utilize university academic support services
• Maintain consistent communication with family

🌟 Personal Growth:
• Embrace cultural diversity and learning
• Develop independence and self-reliance
• Build confidence in new environment
• Explore India's rich cultural heritage
• Maintain connection to Bangladeshi roots

Generate culturally sensitive guidance that helps Bangladeshi students thrive academically and personally while maintaining their cultural identity."""


def main():
    """Demonstration of advanced context-rich prompt templates."""
    
    # Initialize prompt templates
    prompt_templates = AdvancedContextRichPromptTemplates()
    
    # Example context requirements
    context_req = ContextRequirements(
        universities=["Sharda University", "Amity University"],
        programs=["B.Tech CSE", "B.Tech IT"],
        student_background="bangladeshi_students",
        timeline="2025-26",
        academic_levels=["HSC", "Diploma"],
        audiences=["students", "parents"]
    )
    
    # Example source requirements
    source_req = SourceRequirements(
        data_source_file="fees_scholarship_btech.txt",
        original_source="Sharda University B.Tech Admission Brochure 2025",
        source_url="https://sharda.ac.in/admissions/btech",
        verification_date="January 2025",
        source_type="official_university_brochure"
    )
    
    # Generate sample prompts
    print("🎯 MASTER SYSTEM PROMPT:")
    print(prompt_templates.get_master_system_prompt())
    print("\n" + "="*80 + "\n")
    
    print("📋 CONTEXT EXTRACTION PROMPT:")
    sample_text = "Sharda University offers B.Tech CSE with annual fee of ₹2,80,000 for international students."
    print(prompt_templates.get_context_extraction_prompt(sample_text, context_req, source_req))
    print("\n" + "="*80 + "\n")
    
    print("💰 FINANCIAL ANALYSIS PROMPT:")
    financial_text = "B.Tech CSE fee is ₹2,80,000 annually. 50% scholarship available for CGPA 3.5+."
    print(prompt_templates.get_financial_analysis_prompt(financial_text, context_req, source_req))
    
    print("\n✅ Advanced Context-Rich Prompt Templates Demonstration Complete!")


if __name__ == "__main__":
    main()
