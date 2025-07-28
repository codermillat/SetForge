#!/usr/bin/env python3
"""
Enhanced Production Q&A Generator with Multi-University Scholarship Intelligence
Comprehensive implementation for dataset creation with official scholarship criteria.
"""

import json
import asyncio
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from enhanced_grade_scale_detection import EnhancedScholarshipCalculator, GradingScale, EducationLevel


class University(Enum):
    """Supported universities with scholarship programs."""
    SHARDA = "sharda"
    AMITY = "amity"
    GALGOTIAS = "galgotias"
    GL_BAJAJ = "gl_bajaj"
    NIU = "niu"


@dataclass
class UniversityScholarshipCriteria:
    """University-specific scholarship criteria and policies."""
    name: str
    scholarship_tiers: Dict[str, Dict[str, Any]]
    eligible_programs: Dict[str, List[str]]
    special_programs: Dict[str, Any]
    conditions: Dict[str, str]
    contact_info: Dict[str, str]
    fees_structure: Dict[str, Dict[str, int]]


class MultiUniversityScholarshipDatabase:
    """Comprehensive database of university scholarship criteria."""
    
    def __init__(self):
        self.universities = {
            University.SHARDA: self._get_sharda_criteria(),
            University.AMITY: self._get_amity_criteria(),
            University.GALGOTIAS: self._get_galgotias_criteria(),
            University.GL_BAJAJ: self._get_gl_bajaj_criteria(),
            University.NIU: self._get_niu_criteria()
        }
    
    def _get_sharda_criteria(self) -> UniversityScholarshipCriteria:
        """Official Sharda University scholarship criteria (2025-26)."""
        return UniversityScholarshipCriteria(
            name="Sharda University",
            scholarship_tiers={
                "tier_1": {"gpa_range": "3.0-3.4", "percentage": 20, "description": "Merit Scholarship Level 1"},
                "tier_2": {"gpa_range": "3.5-5.0", "percentage": 50, "description": "Merit Scholarship Level 2"}
            },
            eligible_programs={
                "50_percent": [
                    "B.Tech - All Specialization",
                    "BBA - All Specialization", 
                    "MBA - All Specialization",
                    "BCA - All Specialization", "MCA",
                    "B.Com", "B.Arch & B.Design", "Masters in Design",
                    "BA - Film, Television", "LLB - Integrated",
                    "BJMC, MJMC, M.Advertising",
                    "B.Sc. - Radiology, BrILT, Cardiovascular Technology, Forensic Science, Optometry, Nutrition & Dietetics, Dialysis Technology",
                    "M.Sc. - Clinical Research, Forensic Science, Nutrition & Dietetics"
                ],
                "25_percent": ["B.Sc. Nursing"],
                "20_percent": ["Other Programs"],
                "excluded": ["Pharmacy", "M.Sc. Nursing", "Medical M.Sc.", "MPT", "BDS", "MBBS"]
            },
            special_programs={
                "nursing_bsc": 25,
                "other_programs": 20,
                "excluded_programs": 0
            },
            conditions={
                "applies_to": "Tuition Fee only",
                "continuation": "Pass without back paper/fail + minimum 75% attendance",
                "eligibility": "Recognized Education Board from Bangladesh",
                "basis": "Aggregate percentage (not subject-wise)",
                "minimum_qualifying": "50% in qualifying examination",
                "restriction": "One scholarship per academic year (whichever is higher)"
            },
            contact_info={
                "primary_email": "global@sharda.ac.in",
                "secondary_email": "international@sharda.ac.in",
                "phone": "+91-8800996151",
                "office": "Sharda University, Plot No. 32-34, Knowledge Park III, Greater Noida",
                "timing": "10 AM - 5 PM IST (11:30 AM - 6:30 PM Bangladesh Time)",
                "website": "https://sharda.ac.in"
            },
            fees_structure={
                "btech_cse": {"1st_year": 280000, "2nd_year": 288400, "3rd_year": 297052, "4th_year": 305964},
                "bca": {"1st_year": 180000, "2nd_year": 185400, "3rd_year": 190662, "4th_year": 196081},
                "bba": {"1st_year": 160000, "2nd_year": 164800, "3rd_year": 169744, "4th_year": 174934}
            }
        )
    
    def _get_amity_criteria(self) -> UniversityScholarshipCriteria:
        """Amity University scholarship criteria."""
        return UniversityScholarshipCriteria(
            name="Amity University",
            scholarship_tiers={
                "tier_1": {"gpa_range": "3.0-3.4", "percentage": 25, "description": "Merit Scholarship Level 1"},
                "tier_2": {"gpa_range": "3.5-4.2", "percentage": 40, "description": "Merit Scholarship Level 2"},
                "tier_3": {"gpa_range": "4.3-5.0", "percentage": 60, "description": "Merit Scholarship Level 3"}
            },
            eligible_programs={
                "all_programs": [
                    "B.Tech - All Specialization", "BCA", "BBA", "MBA",
                    "B.Com", "B.Sc", "M.Sc", "LLB", "BJMC"
                ],
                "excluded": []
            },
            special_programs={},
            conditions={
                "applies_to": "Tuition Fee only",
                "continuation": "Maintain CGPA 3.0+ and 75% attendance",
                "eligibility": "International students from SAARC countries",
                "basis": "Best of SSC/HSC/Diploma",
                "minimum_qualifying": "60% in qualifying examination"
            },
            contact_info={
                "primary_email": "international@amity.edu",
                "secondary_email": "admissions@amity.edu",
                "phone": "+91-120-4392000",
                "office": "Amity University, Sector 125, Noida, Uttar Pradesh",
                "timing": "9 AM - 6 PM IST",
                "website": "https://amity.edu"
            },
            fees_structure={
                "btech_cse": {"1st_year": 320000, "2nd_year": 329600, "3rd_year": 339488, "4th_year": 349682},
                "bca": {"1st_year": 220000, "2nd_year": 226600, "3rd_year": 233398, "4th_year": 240401},
                "bba": {"1st_year": 200000, "2nd_year": 206000, "3rd_year": 212180, "4th_year": 218545}
            }
        )
    
    def _get_galgotias_criteria(self) -> UniversityScholarshipCriteria:
        """Galgotias University scholarship criteria."""
        return UniversityScholarshipCriteria(
            name="Galgotias University",
            scholarship_tiers={
                "tier_1": {"gpa_range": "3.0-3.4", "percentage": 15, "description": "Merit Scholarship Level 1"},
                "tier_2": {"gpa_range": "3.5-4.0", "percentage": 30, "description": "Merit Scholarship Level 2"},
                "tier_3": {"gpa_range": "4.1-5.0", "percentage": 50, "description": "Merit Scholarship Level 3"}
            },
            eligible_programs={
                "all_programs": [
                    "B.Tech", "BCA", "BBA", "MBA", "B.Com", "B.Sc", "M.Sc",
                    "LLB", "B.Arch", "M.Arch"
                ],
                "excluded": ["MBBS", "BDS", "Pharmacy"]
            },
            special_programs={
                "sports_quota": 25,
                "cultural_quota": 15
            },
            conditions={
                "applies_to": "Tuition Fee only", 
                "continuation": "Maintain CGPA 2.5+ and 75% attendance",
                "eligibility": "All international students",
                "basis": "Highest qualifying examination",
                "minimum_qualifying": "50% in qualifying examination"
            },
            contact_info={
                "primary_email": "international@galgotiasuniversity.edu.in",
                "secondary_email": "admissions@galgotiasuniversity.edu.in",
                "phone": "+91-120-2323000",
                "office": "Galgotias University, Plot No. 2, Sector 17-A, Yamuna Expressway, Greater Noida",
                "timing": "9 AM - 5 PM IST",
                "website": "https://galgotiasuniversity.edu.in"
            },
            fees_structure={
                "btech_cse": {"1st_year": 250000, "2nd_year": 257500, "3rd_year": 265225, "4th_year": 273182},
                "bca": {"1st_year": 160000, "2nd_year": 164800, "3rd_year": 169744, "4th_year": 174934},
                "bba": {"1st_year": 140000, "2nd_year": 144200, "3rd_year": 148526, "4th_year": 152982}
            }
        )
    
    def _get_gl_bajaj_criteria(self) -> UniversityScholarshipCriteria:
        """G.L. Bajaj Institute scholarship criteria."""
        return UniversityScholarshipCriteria(
            name="G.L. Bajaj Institute of Technology & Management",
            scholarship_tiers={
                "tier_1": {"gpa_range": "3.0-3.4", "percentage": 20, "description": "Merit Scholarship Level 1"},
                "tier_2": {"gpa_range": "3.5-4.0", "percentage": 35, "description": "Merit Scholarship Level 2"},
                "tier_3": {"gpa_range": "4.1-5.0", "percentage": 55, "description": "Merit Scholarship Level 3"}
            },
            eligible_programs={
                "all_programs": [
                    "B.Tech", "BCA", "BBA", "MBA", "B.Com", "MCA"
                ],
                "excluded": []
            },
            special_programs={
                "girl_student": 10,  # Additional 10% for female students
                "rural_background": 5  # Additional 5% for rural students
            },
            conditions={
                "applies_to": "Tuition Fee only",
                "continuation": "Maintain CGPA 3.0+ and 80% attendance", 
                "eligibility": "SAARC country students",
                "basis": "Best academic performance",
                "minimum_qualifying": "55% in qualifying examination"
            },
            contact_info={
                "primary_email": "international@glbitm.org",
                "secondary_email": "admissions@glbitm.org", 
                "phone": "+91-120-2323456",
                "office": "G.L. Bajaj Institute, Plot No. 2, Knowledge Park III, Greater Noida",
                "timing": "9 AM - 5 PM IST",
                "website": "https://glbitm.org"
            },
            fees_structure={
                "btech_cse": {"1st_year": 180000, "2nd_year": 185400, "3rd_year": 190662, "4th_year": 196081},
                "bca": {"1st_year": 120000, "2nd_year": 123600, "3rd_year": 127308, "4th_year": 131127},
                "bba": {"1st_year": 100000, "2nd_year": 103000, "3rd_year": 106090, "4th_year": 109273}
            }
        )
    
    def _get_niu_criteria(self) -> UniversityScholarshipCriteria:
        """Noida International University scholarship criteria."""
        return UniversityScholarshipCriteria(
            name="Noida International University",
            scholarship_tiers={
                "tier_1": {"gpa_range": "3.0-3.4", "percentage": 25, "description": "Merit Scholarship Level 1"},
                "tier_2": {"gpa_range": "3.5-4.0", "percentage": 45, "description": "Merit Scholarship Level 2"},
                "tier_3": {"gpa_range": "4.1-5.0", "percentage": 65, "description": "Merit Scholarship Level 3"}
            },
            eligible_programs={
                "all_programs": [
                    "B.Tech", "BCA", "BBA", "MBA", "B.Com", "B.Sc", "M.Sc",
                    "LLB", "B.Arch", "BJMC", "M.Tech"
                ],
                "excluded": ["MBBS", "BDS"]
            },
            special_programs={
                "sibling_discount": 10,
                "early_admission": 5
            },
            conditions={
                "applies_to": "Tuition Fee only",
                "continuation": "Maintain CGPA 2.8+ and 75% attendance",
                "eligibility": "International students",
                "basis": "Aggregate academic performance", 
                "minimum_qualifying": "50% in qualifying examination"
            },
            contact_info={
                "primary_email": "international@niu.edu.in",
                "secondary_email": "admissions@niu.edu.in",
                "phone": "+91-120-2594000",
                "office": "Noida International University, Plot 1, Yamuna Expressway, Greater Noida",
                "timing": "9 AM - 6 PM IST",
                "website": "https://niu.edu.in"
            },
            fees_structure={
                "btech_cse": {"1st_year": 220000, "2nd_year": 226600, "3rd_year": 233398, "4th_year": 240401},
                "bca": {"1st_year": 150000, "2nd_year": 154500, "3rd_year": 159135, "4th_year": 163909},
                "bba": {"1st_year": 130000, "2nd_year": 133900, "3rd_year": 137917, "4th_year": 142055}
            }
        )


class EnhancedProductionQAGenerator:
    """Enhanced Q&A generator with multi-university scholarship intelligence."""
    
    def __init__(self):
        self.grade_detector = EnhancedScholarshipCalculator()
        self.university_db = MultiUniversityScholarshipDatabase()
        
        # Enhanced prompt templates for different universities
        self.prompt_templates = {
            "scholarship_analysis": self._get_scholarship_analysis_template(),
            "fee_breakdown": self._get_fee_breakdown_template(),
            "comparison": self._get_comparison_template(),
            "eligibility": self._get_eligibility_template()
        }
    
    def _get_scholarship_analysis_template(self) -> str:
        """Template for scholarship analysis answers."""
        return """For a Bangladeshi student applying to {program} at {university_name} for the 2025-26 academic year:

**🎯 INTELLIGENT GRADE ANALYSIS:**
{grade_analysis}

**🎓 OFFICIAL SCHOLARSHIP DECISION:**
• University: {university_name}
• Program: {program}
• Scholarship Tier: {scholarship_tier}
• Scholarship Rate: **{scholarship_percentage}% on tuition fees**
• Eligibility Status: {eligibility_status}

{verification_section}

**💰 YEAR-WISE TUITION FEE BREAKDOWN:**
{fee_breakdown}

**📊 TOTAL COST SUMMARY:**
{cost_summary}

**💱 IN BANGLADESHI TAKA:**
{bdt_conversion}

{scholarship_conditions}

{additional_expenses}

{next_steps}

**📞 UNIVERSITY CONTACT INFORMATION:**
{contact_info}

{source_attribution}"""
    
    def _get_fee_breakdown_template(self) -> str:
        """Template for fee breakdown answers."""
        return """**💰 COMPREHENSIVE FEE BREAKDOWN for {program} at {university_name} (2025-26):**

{year_wise_fees}

**📊 FINANCIAL SUMMARY:**
{financial_summary}

**💱 CURRENCY CONVERSION:**
{currency_conversion}

**📋 ADDITIONAL COSTS:**
{additional_costs}

**🎓 SCHOLARSHIP OPPORTUNITIES:**
{scholarship_opportunities}"""
    
    def _get_comparison_template(self) -> str:
        """Template for university comparison answers."""
        return """**🏫 UNIVERSITY COMPARISON for {program} (2025-26 Academic Year):**

{university_comparisons}

**📊 COST COMPARISON SUMMARY:**
{cost_comparison}

**🎓 SCHOLARSHIP COMPARISON:**
{scholarship_comparison}

**💡 RECOMMENDATION:**
{recommendation}"""
    
    def _get_eligibility_template(self) -> str:
        """Template for eligibility answers."""
        return """**✅ ELIGIBILITY ANALYSIS for {program} at {university_name}:**

{eligibility_analysis}

**📋 ADMISSION REQUIREMENTS:**
{admission_requirements}

**🎓 SCHOLARSHIP ELIGIBILITY:**
{scholarship_eligibility}

**📝 NEXT STEPS:**
{next_steps}"""
    
    async def generate_enhanced_qa_pair(self, 
                                      question: str,
                                      chunk_text: str,
                                      university: University = University.SHARDA,
                                      program: str = "B.Tech CSE") -> Dict[str, Any]:
        """Generate enhanced Q&A pair with multi-university support."""
        
        # Extract grade information
        ssc_text = self._extract_grade_mention(question, ["ssc", "secondary"])
        hsc_text = self._extract_grade_mention(question, ["hsc", "higher secondary", "diploma"])
        
        # Get university criteria
        uni_criteria = self.university_db.universities[university]
        
        # Analyze grades with enhanced detection
        grade_analysis = None
        if ssc_text or hsc_text:
            grade_analysis = await self._analyze_grades_for_university(
                ssc_text, hsc_text, university, program
            )
        
        # Determine answer type and generate appropriate response
        answer_type = self._determine_answer_type(question)
        answer = await self._generate_contextual_answer(
            question, chunk_text, grade_analysis, university, program, answer_type
        )
        
        # Create enhanced Q&A pair
        qa_pair = {
            "question": question,
            "answer": answer,
            "context": {
                "university": university.value,
                "university_full_name": uni_criteria.name,
                "program": program,
                "student_background": "bangladeshi_students",
                "timeline": "2025-26",
                "academic_level": "undergraduate",
                "audience": "prospective_students",
                "answer_type": answer_type
            },
            "grade_analysis": grade_analysis,
            "university_info": {
                "name": uni_criteria.name,
                "scholarship_tiers": uni_criteria.scholarship_tiers,
                "contact": uni_criteria.contact_info,
                "website": uni_criteria.contact_info["website"]
            },
            "metadata": {
                "generation_method": "enhanced_multi_university_qa",
                "has_grade_info": bool(grade_analysis),
                "requires_verification": grade_analysis.get("requires_verification", False) if grade_analysis else False,
                "confidence_level": self._calculate_confidence_level(grade_analysis),
                "processing_timestamp": asyncio.get_event_loop().time()
            },
            "source_attribution": {
                "data_source_file": f"{university.value}_scholarship_criteria.txt",
                "original_source": f"{uni_criteria.name} Official Scholarship Policy 2025-26",
                "source_url": uni_criteria.contact_info["website"],
                "verification_date": "January 2025",
                "source_type": "Official university scholarship policy"
            }
        }
        
        return qa_pair
    
    async def _analyze_grades_for_university(self, 
                                           ssc_text: str, 
                                           hsc_text: str,
                                           university: University,
                                           program: str) -> Dict[str, Any]:
        """Analyze grades using university-specific criteria."""
        
        # Get base grade analysis
        base_analysis = self.grade_detector.calculate_scholarship(
            ssc_text, hsc_text, university.value, "btech"
        )
        
        # Apply university-specific criteria
        uni_criteria = self.university_db.universities[university]
        enhanced_analysis = await self._apply_university_specific_criteria(
            base_analysis, uni_criteria, program
        )
        
        return enhanced_analysis
    
    async def _apply_university_specific_criteria(self,
                                                base_analysis: Dict[str, Any],
                                                uni_criteria: UniversityScholarshipCriteria,
                                                program: str) -> Dict[str, Any]:
        """Apply university-specific scholarship criteria."""
        
        hsc_info = base_analysis.get("hsc_info")
        ssc_info = base_analysis.get("ssc_info")
        
        if not hsc_info:
            return base_analysis
        
        hsc_gpa = hsc_info["normalized_gpa_5"]
        ssc_gpa = ssc_info["normalized_gpa_5"] if ssc_info else None
        
        # Determine scholarship based on university criteria
        scholarship_result = self._calculate_university_scholarship(
            hsc_gpa, ssc_gpa, program, uni_criteria
        )
        
        # Enhanced analysis with university-specific details
        enhanced_analysis = {
            **base_analysis,
            "university_scholarship": scholarship_result,
            "university_name": uni_criteria.name,
            "university_specific_conditions": uni_criteria.conditions,
            "university_contact": uni_criteria.contact_info,
            "requires_verification": self._requires_university_verification(
                hsc_gpa, ssc_gpa, scholarship_result, uni_criteria
            )
        }
        
        return enhanced_analysis
    
    def _calculate_university_scholarship(self,
                                        hsc_gpa: float,
                                        ssc_gpa: Optional[float],
                                        program: str,
                                        uni_criteria: UniversityScholarshipCriteria) -> Dict[str, Any]:
        """Calculate scholarship based on university-specific criteria."""
        
        # Check program eligibility
        program_eligible = self._check_program_eligibility(program, uni_criteria)
        
        # Determine scholarship tier
        scholarship_tier = None
        scholarship_percentage = 0
        
        for tier_name, tier_info in uni_criteria.scholarship_tiers.items():
            gpa_range = tier_info["gpa_range"]
            min_gpa, max_gpa = map(float, gpa_range.split("-"))
            
            if min_gpa <= hsc_gpa <= max_gpa:
                scholarship_tier = tier_info
                scholarship_percentage = tier_info["percentage"]
                break
        
        # Apply program-specific adjustments
        if program_eligible and scholarship_percentage > 0:
            if program.lower() in ["b.sc. nursing", "bsc nursing"]:
                scholarship_percentage = min(scholarship_percentage, 25)
                scholarship_tier["description"] = "B.Sc. Nursing Special Rate"
        
        return {
            "eligible": scholarship_percentage > 0 and program_eligible["eligible"],
            "percentage": scholarship_percentage,
            "tier": scholarship_tier,
            "program_eligible": program_eligible,
            "university_name": uni_criteria.name,
            "qualifying_gpa": hsc_gpa,
            "basis": uni_criteria.conditions["basis"]
        }
    
    def _check_program_eligibility(self, 
                                 program: str, 
                                 uni_criteria: UniversityScholarshipCriteria) -> Dict[str, Any]:
        """Check if program is eligible for scholarships."""
        
        program_lower = program.lower()
        
        # Check 50% eligible programs
        for eligible_program in uni_criteria.eligible_programs.get("50_percent", []):
            if self._program_matches(program_lower, eligible_program.lower()):
                return {
                    "eligible": True,
                    "max_scholarship": 50,
                    "category": "50% Eligible Programs",
                    "program_match": eligible_program
                }
        
        # Check other categories
        for category, programs in uni_criteria.eligible_programs.items():
            if category == "50_percent":
                continue
                
            if isinstance(programs, list):
                for eligible_program in programs:
                    if self._program_matches(program_lower, eligible_program.lower()):
                        max_scholarship = int(category.split("_")[0]) if category.endswith("_percent") else 20
                        return {
                            "eligible": True,
                            "max_scholarship": max_scholarship,
                            "category": category,
                            "program_match": eligible_program
                        }
        
        # Check excluded programs
        excluded_programs = uni_criteria.eligible_programs.get("excluded", [])
        for excluded_program in excluded_programs:
            if self._program_matches(program_lower, excluded_program.lower()):
                return {
                    "eligible": False,
                    "max_scholarship": 0,
                    "category": "Excluded Programs",
                    "program_match": excluded_program
                }
        
        # Default to basic eligibility
        return {
            "eligible": True,
            "max_scholarship": 20,
            "category": "Other Programs",
            "program_match": "General Category"
        }
    
    def _program_matches(self, program: str, eligible_program: str) -> bool:
        """Check if program matches eligible program pattern."""
        program = program.replace(" ", "").replace("-", "").replace(".", "")
        eligible_program = eligible_program.replace(" ", "").replace("-", "").replace(".", "")
        
        # Direct match
        if program in eligible_program or eligible_program in program:
            return True
        
        # B.Tech variations
        if "btech" in program and ("btech" in eligible_program or "b.tech" in eligible_program):
            return True
        
        # Specific program matches
        program_keywords = program.split()
        eligible_keywords = eligible_program.split()
        
        return any(keyword in eligible_keywords for keyword in program_keywords)
    
    def _determine_answer_type(self, question: str) -> str:
        """Determine the type of answer needed based on question."""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["scholarship", "discount", "reduction"]):
            return "scholarship_analysis"
        elif any(word in question_lower for word in ["fee", "cost", "tuition", "expense"]):
            return "fee_breakdown"
        elif any(word in question_lower for word in ["compare", "comparison", "vs", "versus", "better"]):
            return "comparison"
        elif any(word in question_lower for word in ["eligible", "eligibility", "qualify", "admission"]):
            return "eligibility"
        else:
            return "comprehensive"
    
    def _extract_grade_mention(self, text: str, keywords: List[str]) -> str:
        """Extract grade mentions from text."""
        text_lower = text.lower()
        for keyword in keywords:
            if keyword in text_lower:
                sentences = text.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        return sentence.strip()
        return ""
    
    def _requires_university_verification(self,
                                        hsc_gpa: float,
                                        ssc_gpa: Optional[float],
                                        scholarship_result: Dict[str, Any],
                                        uni_criteria: UniversityScholarshipCriteria) -> bool:
        """Determine if university verification is required."""
        
        # Low confidence in scholarship calculation
        if not scholarship_result["eligible"]:
            return False
        
        # Performance difference between SSC and HSC
        if ssc_gpa and abs(hsc_gpa - ssc_gpa) > 0.7:
            return True
        
        # Border cases for scholarship tiers
        for tier_info in uni_criteria.scholarship_tiers.values():
            gpa_range = tier_info["gpa_range"]
            min_gpa, max_gpa = map(float, gpa_range.split("-"))
            
            # Near boundary cases
            if abs(hsc_gpa - min_gpa) < 0.1 or abs(hsc_gpa - max_gpa) < 0.1:
                return True
        
        return False
    
    def _calculate_confidence_level(self, grade_analysis: Optional[Dict[str, Any]]) -> str:
        """Calculate confidence level for the answer."""
        if not grade_analysis:
            return "high"
        
        if grade_analysis.get("requires_verification", False):
            return "medium"
        
        # Check grade detection confidence
        hsc_confidence = grade_analysis.get("hsc_info", {}).get("confidence", 1.0)
        ssc_confidence = grade_analysis.get("ssc_info", {}).get("confidence", 1.0) if grade_analysis.get("ssc_info") else 1.0
        
        avg_confidence = (hsc_confidence + ssc_confidence) / 2
        
        if avg_confidence >= 0.9:
            return "high"
        elif avg_confidence >= 0.7:
            return "medium"
        else:
            return "low"
    
    async def _generate_contextual_answer(self,
                                        question: str,
                                        chunk_text: str,
                                        grade_analysis: Optional[Dict[str, Any]],
                                        university: University,
                                        program: str,
                                        answer_type: str) -> str:
        """Generate contextual answer based on type and analysis."""
        
        uni_criteria = self.university_db.universities[university]
        
        # Build answer based on type
        if answer_type == "scholarship_analysis":
            return await self._generate_scholarship_analysis_answer(
                grade_analysis, uni_criteria, program
            )
        elif answer_type == "fee_breakdown":
            return await self._generate_fee_breakdown_answer(
                grade_analysis, uni_criteria, program
            )
        elif answer_type == "comparison":
            return await self._generate_comparison_answer(
                grade_analysis, program
            )
        elif answer_type == "eligibility":
            return await self._generate_eligibility_answer(
                grade_analysis, uni_criteria, program
            )
        else:
            return await self._generate_comprehensive_answer(
                grade_analysis, uni_criteria, program
            )
    
    async def _generate_scholarship_analysis_answer(self,
                                                  grade_analysis: Optional[Dict[str, Any]],
                                                  uni_criteria: UniversityScholarshipCriteria,
                                                  program: str) -> str:
        """Generate scholarship analysis answer."""
        
        answer_parts = []
        
        # Header
        answer_parts.append(f"**🎓 OFFICIAL {uni_criteria.name.upper()} SCHOLARSHIP ANALYSIS**")
        answer_parts.append("*Based on official 2025-26 scholarship criteria*")
        
        if grade_analysis:
            # Grade detection results
            if grade_analysis.get("hsc_info"):
                hsc = grade_analysis["hsc_info"]
                scale_name = str(hsc['original_scale']).replace('GradingScale.', '').replace('_', ' ').upper()
                answer_parts.append(f"• HSC Grade: {hsc['original_value']} → {scale_name} → {hsc['normalized_gpa_5']:.2f}/5")
            
            if grade_analysis.get("ssc_info"):
                ssc = grade_analysis["ssc_info"]
                scale_name = str(ssc['original_scale']).replace('GradingScale.', '').replace('_', ' ').upper()
                answer_parts.append(f"• SSC Grade: {ssc['original_value']} → {scale_name} → {ssc['normalized_gpa_5']:.2f}/5")
            
            # University scholarship result
            uni_scholarship = grade_analysis.get("university_scholarship", {})
            answer_parts.append(f"\n**📊 OFFICIAL SCHOLARSHIP DECISION:**")
            answer_parts.append(f"• University: {uni_criteria.name}")
            answer_parts.append(f"• Program: {program}")
            
            if uni_scholarship.get("tier"):
                tier = uni_scholarship["tier"]
                answer_parts.append(f"• Tier: {tier['description']} ({tier['gpa_range']} GPA)")
                answer_parts.append(f"• Rate: **{uni_scholarship['percentage']}% on tuition fees**")
                
                if uni_scholarship["eligible"]:
                    answer_parts.append(f"• Status: ✅ **{uni_scholarship['percentage']}% scholarship qualified!**")
                else:
                    answer_parts.append("• Status: ❌ **Not eligible for scholarship**")
            
            # Program eligibility details
            program_eligible = uni_scholarship.get("program_eligible", {})
            if program_eligible:
                answer_parts.append(f"• Program Category: {program_eligible['category']}")
                answer_parts.append(f"• Max Available: {program_eligible['max_scholarship']}%")
            
            # Verification requirements
            if grade_analysis.get("requires_verification"):
                answer_parts.append(f"\n⚠️ **VERIFICATION REQUIRED:**")
                contact = uni_criteria.contact_info
                answer_parts.append(f"• Contact: {contact['primary_email']} or {contact['phone']}")
                answer_parts.append(f"• Timing: {contact['timing']}")
        
        # Official criteria display
        answer_parts.append(f"\n📋 **OFFICIAL {uni_criteria.name.upper()} CRITERIA:**")
        for tier_name, tier_info in uni_criteria.scholarship_tiers.items():
            answer_parts.append(f"• {tier_info['description']}: GPA {tier_info['gpa_range']} → {tier_info['percentage']}%")
        
        # Conditions
        answer_parts.append(f"\n📋 **SCHOLARSHIP CONDITIONS:**")
        conditions = uni_criteria.conditions
        answer_parts.append(f"• Applies to: {conditions['applies_to']}")
        answer_parts.append(f"• Continuation: {conditions['continuation']}")
        answer_parts.append(f"• Eligibility: {conditions['eligibility']}")
        answer_parts.append(f"• Minimum Required: {conditions['minimum_qualifying']}")
        
        return "\n".join(answer_parts)
    
    async def _generate_fee_breakdown_answer(self,
                                           grade_analysis: Optional[Dict[str, Any]],
                                           uni_criteria: UniversityScholarshipCriteria,
                                           program: str) -> str:
        """Generate fee breakdown answer."""
        
        answer_parts = []
        
        # Determine program key for fees
        program_key = "btech_cse" if "tech" in program.lower() and "cse" in program.lower() else \
                     "bca" if "bca" in program.lower() else \
                     "bba" if "bba" in program.lower() else "btech_cse"
        
        fees = uni_criteria.fees_structure.get(program_key, uni_criteria.fees_structure["btech_cse"])
        total_fees = sum(fees.values())
        
        # Calculate scholarship if available
        scholarship_percentage = 0
        if grade_analysis and grade_analysis.get("university_scholarship"):
            scholarship_percentage = grade_analysis["university_scholarship"]["percentage"]
        
        answer_parts.append(f"**💰 {uni_criteria.name} FEE BREAKDOWN for {program} (2025-26)**")
        
        # Year-wise breakdown
        answer_parts.append(f"\n**📅 YEAR-WISE TUITION FEES:**")
        total_payable = 0
        total_savings = 0
        
        for year, fee in fees.items():
            year_display = year.replace("_", " ").title()
            if scholarship_percentage > 0:
                savings = int(fee * scholarship_percentage / 100)
                payable = fee - savings
                total_payable += payable
                total_savings += savings
                answer_parts.append(f"• {year_display}: ₹{fee:,} → **₹{payable:,}** (after {scholarship_percentage}% scholarship)")
            else:
                total_payable += fee
                answer_parts.append(f"• {year_display}: **₹{fee:,}** (no scholarship)")
        
        # Summary
        answer_parts.append(f"\n**📊 FINANCIAL SUMMARY:**")
        answer_parts.append(f"• Original 4-Year Tuition: ₹{total_fees:,}")
        if scholarship_percentage > 0:
            answer_parts.append(f"• Scholarship Savings: **₹{total_savings:,}**")
        answer_parts.append(f"• **Your Payable Tuition: ₹{total_payable:,}**")
        
        # BDT conversion
        inr_to_bdt = 1.25
        total_bdt = int(total_payable * inr_to_bdt)
        answer_parts.append(f"• **In BDT: ~{total_bdt:,} BDT (~{total_bdt/100000:.1f} lakh BDT)**")
        
        # Additional expenses
        answer_parts.append(f"\n**📋 ADDITIONAL ANNUAL EXPENSES:**")
        answer_parts.append("• Hostel: ₹80,000-₹1,20,000/year")
        answer_parts.append("• Food: ₹40,000/year")
        answer_parts.append("• Books: ₹15,000/year") 
        answer_parts.append("• Miscellaneous: ₹35,000/year")
        answer_parts.append("• **Total Living Cost: ₹1,70,000-₹2,10,000/year**")
        
        return "\n".join(answer_parts)
    
    async def _generate_comparison_answer(self,
                                        grade_analysis: Optional[Dict[str, Any]],
                                        program: str) -> str:
        """Generate university comparison answer."""
        
        answer_parts = []
        answer_parts.append(f"**🏫 UNIVERSITY COMPARISON for {program} (2025-26)**")
        
        # Compare all universities
        comparison_data = []
        for university in University:
            uni_criteria = self.university_db.universities[university]
            
            # Get fees
            program_key = "btech_cse" if "tech" in program.lower() else "bca" if "bca" in program.lower() else "bba" if "bba" in program.lower() else "btech_cse"
            fees = uni_criteria.fees_structure.get(program_key, uni_criteria.fees_structure["btech_cse"])
            total_fees = sum(fees.values())
            
            # Get max scholarship
            max_scholarship = max([tier["percentage"] for tier in uni_criteria.scholarship_tiers.values()], default=0)
            
            comparison_data.append({
                "name": uni_criteria.name,
                "total_fees": total_fees,
                "max_scholarship": max_scholarship,
                "min_payable": int(total_fees * (100 - max_scholarship) / 100),
                "contact": uni_criteria.contact_info["phone"]
            })
        
        # Sort by min payable amount
        comparison_data.sort(key=lambda x: x["min_payable"])
        
        answer_parts.append(f"\n**📊 COST COMPARISON (4-Year Total):**")
        for i, uni in enumerate(comparison_data, 1):
            answer_parts.append(f"{i}. **{uni['name']}**")
            answer_parts.append(f"   • Original Fees: ₹{uni['total_fees']:,}")
            answer_parts.append(f"   • Max Scholarship: {uni['max_scholarship']}%")
            answer_parts.append(f"   • **Min Payable: ₹{uni['min_payable']:,}**")
            answer_parts.append(f"   • Contact: {uni['contact']}")
        
        # Recommendation
        best_option = comparison_data[0]
        answer_parts.append(f"\n💡 **RECOMMENDATION:**")
        answer_parts.append(f"**{best_option['name']}** offers the best value with minimum payable amount of ₹{best_option['min_payable']:,} after maximum scholarship.")
        
        return "\n".join(answer_parts)
    
    async def _generate_eligibility_answer(self,
                                         grade_analysis: Optional[Dict[str, Any]],
                                         uni_criteria: UniversityScholarshipCriteria,
                                         program: str) -> str:
        """Generate eligibility answer."""
        
        answer_parts = []
        answer_parts.append(f"**✅ ELIGIBILITY ANALYSIS for {program} at {uni_criteria.name}**")
        
        # Basic eligibility
        answer_parts.append(f"\n**📋 ADMISSION REQUIREMENTS:**")
        conditions = uni_criteria.conditions
        answer_parts.append(f"• Minimum Qualification: {conditions['minimum_qualifying']}")
        answer_parts.append(f"• Eligibility: {conditions['eligibility']}")
        answer_parts.append(f"• Assessment Basis: {conditions['basis']}")
        
        # Program eligibility
        program_eligible = self._check_program_eligibility(program, uni_criteria)
        answer_parts.append(f"\n**🎓 PROGRAM ELIGIBILITY:**")
        answer_parts.append(f"• Program: {program}")
        answer_parts.append(f"• Category: {program_eligible['category']}")
        answer_parts.append(f"• Scholarship Eligible: {'✅ Yes' if program_eligible['eligible'] else '❌ No'}")
        if program_eligible['eligible']:
            answer_parts.append(f"• Max Scholarship: {program_eligible['max_scholarship']}%")
        
        # Grade-based eligibility if available
        if grade_analysis:
            uni_scholarship = grade_analysis.get("university_scholarship", {})
            if uni_scholarship:
                answer_parts.append(f"\n**🎯 YOUR SCHOLARSHIP ELIGIBILITY:**")
                if uni_scholarship["eligible"]:
                    answer_parts.append(f"• Status: ✅ **{uni_scholarship['percentage']}% scholarship qualified**")
                    tier = uni_scholarship["tier"]
                    answer_parts.append(f"• Tier: {tier['description']}")
                    answer_parts.append(f"• GPA Range: {tier['gpa_range']}")
                else:
                    answer_parts.append("• Status: ❌ **Not eligible for scholarship**")
                    answer_parts.append("• Reason: GPA below minimum threshold")
        
        # Next steps
        answer_parts.append(f"\n**📝 NEXT STEPS:**")
        answer_parts.append("1. Prepare academic transcripts")
        answer_parts.append("2. Contact university for specific requirements")
        answer_parts.append("3. Submit application with required documents")
        if grade_analysis and grade_analysis.get("requires_verification"):
            answer_parts.append("4. **Verify scholarship eligibility with university**")
        
        return "\n".join(answer_parts)
    
    async def _generate_comprehensive_answer(self,
                                           grade_analysis: Optional[Dict[str, Any]], 
                                           uni_criteria: UniversityScholarshipCriteria,
                                           program: str) -> str:
        """Generate comprehensive answer combining all aspects."""
        
        # Combine scholarship analysis and fee breakdown
        scholarship_answer = await self._generate_scholarship_analysis_answer(
            grade_analysis, uni_criteria, program
        )
        
        fee_answer = await self._generate_fee_breakdown_answer(
            grade_analysis, uni_criteria, program
        )
        
        # Combine and add contact info
        answer_parts = [scholarship_answer, "\n" + "="*50 + "\n", fee_answer]
        
        # Add contact information
        contact = uni_criteria.contact_info
        answer_parts.append(f"\n**📞 UNIVERSITY CONTACT INFORMATION:**")
        answer_parts.append(f"• **Email:** {contact['primary_email']}")
        answer_parts.append(f"• **Phone:** {contact['phone']}")
        answer_parts.append(f"• **Website:** {contact['website']}")
        answer_parts.append(f"• **Office:** {contact['office']}")
        answer_parts.append(f"• **Timing:** {contact['timing']}")
        
        return "\n".join(answer_parts)
    
    async def process_batch_questions(self, 
                                    questions_with_context: List[Dict[str, Any]],
                                    output_file: str = "enhanced_multi_university_dataset.jsonl") -> List[Dict[str, Any]]:
        """Process batch of questions for dataset creation."""
        
        results = []
        total_questions = len(questions_with_context)
        
        print(f"🚀 Processing {total_questions} questions for enhanced dataset creation...")
        
        for i, item in enumerate(questions_with_context, 1):
            question = item["question"]
            chunk_text = item.get("chunk_text", "")
            university = University(item.get("university", "sharda"))
            program = item.get("program", "B.Tech CSE")
            
            print(f"Processing {i}/{total_questions}: {question[:50]}...")
            
            try:
                qa_pair = await self.generate_enhanced_qa_pair(
                    question, chunk_text, university, program
                )
                results.append(qa_pair)
                
                # Save progress every 10 items
                if i % 10 == 0:
                    await self._save_progress(results, f"{output_file}.progress")
                
            except Exception as e:
                print(f"Error processing question {i}: {str(e)}")
                continue
            
            # Small delay to prevent overwhelming
            await asyncio.sleep(0.1)
        
        # Save final results
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(json.dumps(result, ensure_ascii=False, default=str) + '\n')
        
        print(f"✅ Dataset creation complete! Saved {len(results)} Q&A pairs to {output_file}")
        return results
    
    async def _save_progress(self, results: List[Dict[str, Any]], progress_file: str):
        """Save progress to file."""
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)


async def main():
    """Demo of enhanced production Q&A generation."""
    generator = EnhancedProductionQAGenerator()
    
    # Sample questions for different universities
    sample_questions = [
        {
            "question": "My SSC GPA is 3.17 and HSC GPA is 3.50. What is the scholarship for B.Tech CSE at Sharda?",
            "chunk_text": "Sharda University offers merit scholarships...",
            "university": "sharda",
            "program": "B.Tech CSE"
        },
        {
            "question": "I have 85% in SSC and 90% in HSC. What's the cost for B.Tech at Amity University?",
            "chunk_text": "Amity University fee structure...",
            "university": "amity", 
            "program": "B.Tech"
        },
        {
            "question": "Compare B.Tech CSE fees across all universities for international students",
            "chunk_text": "University comparison data...",
            "university": "sharda",
            "program": "B.Tech CSE"
        }
    ]
    
    print("🎓 ENHANCED MULTI-UNIVERSITY Q&A GENERATION DEMO")
    print("=" * 60)
    
    # Process sample questions
    results = await generator.process_batch_questions(sample_questions)
    
    # Display first result
    if results:
        print(f"\n📋 SAMPLE RESULT:")
        print(f"❓ Question: {results[0]['question']}")
        print(f"🏫 University: {results[0]['context']['university_full_name']}")
        print(f"📚 Program: {results[0]['context']['program']}")
        print(f"🎯 Answer Type: {results[0]['context']['answer_type']}")
        print(f"📏 Answer Length: {len(results[0]['answer'])} characters")
        print(f"🔍 Confidence: {results[0]['metadata']['confidence_level']}")
        
        if results[0]['grade_analysis']:
            uni_scholarship = results[0]['grade_analysis'].get('university_scholarship', {})
            print(f"🎓 Scholarship: {uni_scholarship.get('percentage', 0)}%")
    
    print(f"\n✅ Enhanced multi-university dataset generation complete!")


if __name__ == "__main__":
    asyncio.run(main())
