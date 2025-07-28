#!/usr/bin/env python3
"""
Official Sharda University Scholarship Integration
Combines enhanced grade detection with official scholarship criteria for accurate Q&A generation.
"""

import json
from typing import Dict, Any
from enhanced_grade_scale_detection import EnhancedScholarshipCalculator


class OfficialShardaScholarshipCalculator:
    """Official Sharda University scholarship calculator with enhanced grade detection."""
    
    def __init__(self):
        self.grade_detector = EnhancedScholarshipCalculator()
        
        # Official Sharda University scholarship criteria (2025-26)
        self.official_criteria = {
            "scholarship_tiers": {
                "tier_1": {"gpa_range": "3.0-3.4", "percentage": 20},
                "tier_2": {"gpa_range": "3.5-5.0", "percentage": 50}
            },
            "eligible_programs_50": [
                "B.Tech - All Specialization",
                "BBA - All Specialization", 
                "MBA - All Specialization",
                "BCA - All Specialization",
                "MCA",
                "B.Com",
                "B.Arch & B.Design",
                "Masters in Design",
                "BA - Film, Television",
                "LLB - Integrated",
                "BJMC, MJMC, M.Advertising",
                "B.Sc. - Radiology, BrILT, Cardiovascular Technology, Forensic Science, Optometry, Nutrition & Dietetics, Dialysis Technology",
                "M.Sc. - Clinical Research, Forensic Science, Nutrition & Dietetics"
            ],
            "special_programs": {
                "bsc_nursing": 25,  # 25% scholarship for B.Sc. Nursing
                "other_programs": 20,  # 20% for rest programs (except excluded)
                "excluded_programs": ["Pharmacy", "M.Sc. Nursing", "Medical M.Sc.", "MPT", "BDS", "MBBS"]
            },
            "conditions": {
                "applies_to": "Tuition Fee only",
                "continuation": "Pass without back paper/fail + minimum 75% attendance",
                "eligibility": "Students from recognized Education Board from Bangladesh",
                "basis": "Aggregate percentage (not subject-wise)",
                "minimum_qualifying": "50% in qualifying examination",
                "restriction": "One scholarship per academic year (whichever is higher)"
            }
        }
    
    def calculate_official_scholarship(self, ssc_text: str, hsc_text: str, program: str = "B.Tech CSE") -> Dict[str, Any]:
        """Calculate scholarship using official Sharda University criteria with enhanced grade detection."""
        
        # Use enhanced grade detection first
        grade_analysis = self.grade_detector.calculate_scholarship(ssc_text, hsc_text, "sharda", "btech")
        
        # Apply official Sharda criteria
        hsc_info = grade_analysis.get("hsc_info")
        ssc_info = grade_analysis.get("ssc_info") 
        
        if not hsc_info:
            return {
                "error": "HSC grade required for scholarship calculation",
                "grade_analysis": grade_analysis
            }
        
        hsc_gpa = hsc_info["normalized_gpa_5"]
        ssc_gpa = ssc_info["normalized_gpa_5"] if ssc_info else None
        
        # Determine scholarship based on official criteria
        official_scholarship = self._apply_official_criteria(hsc_gpa, ssc_gpa, program)
        
        # Enhanced analysis with warnings
        enhanced_analysis = {
            "official_scholarship": official_scholarship,
            "grade_detection": grade_analysis,
            "verification_required": self._requires_verification(hsc_gpa, ssc_gpa, grade_analysis),
            "recommendations": self._generate_recommendations(hsc_gpa, ssc_gpa, official_scholarship),
            "alternative_scenarios": self._calculate_alternatives(hsc_gpa, ssc_gpa),
            "official_contact": {
                "email": ["global@sharda.ac.in", "international@sharda.ac.in"],
                "phone": "+91-8800996151",
                "office": "Sharda University, Plot No. 32-34, Knowledge Park III, Greater Noida",
                "timing": "10 AM - 5 PM IST (11:30 AM - 6:30 PM Bangladesh Time)"
            }
        }
        
        return enhanced_analysis
    
    def _apply_official_criteria(self, hsc_gpa: float, ssc_gpa: float = None, program: str = "B.Tech CSE") -> Dict[str, Any]:
        """Apply official Sharda University scholarship criteria."""
        
        # Check program eligibility for 50% scholarship
        program_eligible_50 = (
            "b.tech" in program.lower() or 
            "btech" in program.lower() or
            any(prog.lower().replace(" ", "").replace("-", "") in program.lower().replace(" ", "").replace("-", "") 
                for prog in self.official_criteria["eligible_programs_50"])
        )
        
        # Special program checks
        if "nursing" in program.lower() and "b.sc" in program.lower():
            return {
                "percentage": 25,
                "tier": "B.Sc. Nursing Special Rate",
                "program_eligible": True,
                "criteria_met": hsc_gpa >= 2.5,  # Assuming 50% minimum
                "basis": "Special B.Sc. Nursing criteria"
            }
        
        if any(excluded.lower() in program.lower() for excluded in self.official_criteria["special_programs"]["excluded_programs"]):
            return {
                "percentage": 0,
                "tier": "Excluded Program",
                "program_eligible": False,
                "criteria_met": False,
                "basis": "Program not eligible for scholarship"
            }
        
        # Apply standard criteria based on HSC GPA
        if hsc_gpa >= 3.5 and program_eligible_50:
            scholarship_rate = 50
            tier = "GPA 3.5-5.0 (50% Scholarship)"
            criteria_met = True
        elif hsc_gpa >= 3.0:
            # Either 50% programs get 50%, or others get 20%
            if program_eligible_50:
                scholarship_rate = 50
                tier = "GPA 3.5-5.0 (50% Scholarship) - Program Eligible"
            else:
                scholarship_rate = 20
                tier = "Other Programs (20% Scholarship)"
            criteria_met = True
        elif hsc_gpa >= 2.5:  # Assuming 50% minimum requirement
            if not program_eligible_50:
                scholarship_rate = 20
                tier = "Other Programs (20% Scholarship)"
                criteria_met = True
            else:
                scholarship_rate = 0
                tier = "Below GPA 3.5 threshold"
                criteria_met = False
        else:
            scholarship_rate = 0
            tier = "Below minimum 50% requirement"
            criteria_met = False
        
        return {
            "percentage": scholarship_rate,
            "tier": tier,
            "program_eligible": program_eligible_50,
            "criteria_met": criteria_met,
            "basis": "Official Sharda University criteria 2025-26",
            "qualifying_gpa": hsc_gpa
        }
    
    def _requires_verification(self, hsc_gpa: float, ssc_gpa: float = None, grade_analysis: Dict = None) -> bool:
        """Determine if university verification is required."""
        
        # Grade detection uncertainty
        if grade_analysis:
            hsc_confidence = grade_analysis.get("hsc_info", {}).get("confidence", 1.0)
            ssc_confidence = grade_analysis.get("ssc_info", {}).get("confidence", 1.0) if grade_analysis.get("ssc_info") else 1.0
            
            if hsc_confidence < 0.8 or ssc_confidence < 0.8:
                return True
        
        # Performance difference between SSC and HSC
        if ssc_gpa and abs(hsc_gpa - ssc_gpa) > 0.5:
            return True
        
        # Border cases
        if 2.9 <= hsc_gpa <= 3.1 or 3.4 <= hsc_gpa <= 3.6:
            return True
        
        return False
    
    def _generate_recommendations(self, hsc_gpa: float, ssc_gpa: float = None, official_scholarship: Dict = None) -> list:
        """Generate personalized recommendations."""
        recommendations = []
        
        if official_scholarship and official_scholarship["percentage"] > 0:
            recommendations.append(f"✅ Strong scholarship eligibility: {official_scholarship['percentage']}% based on HSC GPA {hsc_gpa:.2f}")
        
        if ssc_gpa and ssc_gpa < 3.0:
            recommendations.append("⚠️ SSC GPA below 3.0 may raise questions - prepare explanation for university")
        
        if ssc_gpa and hsc_gpa and abs(hsc_gpa - ssc_gpa) > 0.5:
            recommendations.append("📞 Contact university for clarification due to SSC-HSC performance difference")
        
        recommendations.append("📄 Get written scholarship confirmation before proceeding with admission")
        recommendations.append("📊 Maintain 75% attendance and pass all exams to continue scholarship from 2nd year")
        
        return recommendations
    
    def _calculate_alternatives(self, hsc_gpa: float, ssc_gpa: float = None) -> Dict[str, Any]:
        """Calculate alternative scholarship scenarios."""
        alternatives = {}
        
        # If HSC qualifies for 50% but SSC is low
        if hsc_gpa >= 3.5 and ssc_gpa and ssc_gpa < 3.5:
            alternatives["conservative_scenario"] = {
                "description": "If university considers overall performance",
                "scholarship": 20,
                "basis": f"SSC GPA {ssc_gpa:.2f} in 3.0-3.4 range"
            }
        
        # If currently getting 20%, show upgrade potential
        if 3.0 <= hsc_gpa < 3.5:
            alternatives["upgrade_possibility"] = {
                "description": "If university rounds up or considers other factors",
                "scholarship": 50,
                "basis": "Borderline case - may qualify for higher tier"
            }
        
        return alternatives
    
    def generate_comprehensive_answer(self, question: str, ssc_text: str = "", hsc_text: str = "", program: str = "B.Tech CSE") -> str:
        """Generate comprehensive answer using official criteria."""
        
        # Calculate using official criteria
        analysis = self.calculate_official_scholarship(ssc_text, hsc_text, program)
        
        if "error" in analysis:
            return f"Unable to process: {analysis['error']}"
        
        official = analysis["official_scholarship"]
        grade_info = analysis["grade_detection"]
        
        answer_parts = []
        
        # Header
        answer_parts.append("**🎓 OFFICIAL SHARDA UNIVERSITY SCHOLARSHIP ANALYSIS**")
        answer_parts.append("*Based on official 2025-26 scholarship criteria*")
        
        # Grade detection results
        if grade_info.get("hsc_info"):
            hsc = grade_info["hsc_info"]
            scale_name = str(hsc['original_scale']).replace('GradingScale.', '').replace('_', ' ').upper()
            answer_parts.append(f"• HSC Grade: {hsc['original_value']} → {scale_name} → {hsc['normalized_gpa_5']:.2f}/5")
        
        if grade_info.get("ssc_info"):
            ssc = grade_info["ssc_info"]
            scale_name = str(ssc['original_scale']).replace('GradingScale.', '').replace('_', ' ').upper()
            answer_parts.append(f"• SSC Grade: {ssc['original_value']} → {scale_name} → {ssc['normalized_gpa_5']:.2f}/5")
        
        # Official scholarship result
        answer_parts.append(f"\n**📊 OFFICIAL SCHOLARSHIP DECISION:**")
        answer_parts.append(f"• Tier: {official['tier']}")
        answer_parts.append(f"• Rate: **{official['percentage']}% on tuition fees**")
        answer_parts.append(f"• Program Eligible: {'✅ Yes' if official['program_eligible'] else '❌ No'}")
        answer_parts.append(f"• Criteria Met: {'✅ Yes' if official['criteria_met'] else '❌ No'}")
        
        # Verification requirements
        if analysis["verification_required"]:
            answer_parts.append(f"\n⚠️ **VERIFICATION REQUIRED:**")
            contact = analysis["official_contact"]
            answer_parts.append(f"• Contact: {', '.join(contact['email'])} or {contact['phone']}")
            answer_parts.append(f"• Timing: {contact['timing']}")
        
        # Recommendations
        if analysis["recommendations"]:
            answer_parts.append(f"\n💡 **RECOMMENDATIONS:**")
            for rec in analysis["recommendations"]:
                answer_parts.append(f"• {rec}")
        
        # Alternative scenarios
        if analysis["alternative_scenarios"]:
            answer_parts.append(f"\n🔄 **ALTERNATIVE SCENARIOS:**")
            for key, alt in analysis["alternative_scenarios"].items():
                answer_parts.append(f"• {alt['description']}: {alt['scholarship']}% ({alt['basis']})")
        
        # Official criteria reference
        answer_parts.append(f"\n📋 **OFFICIAL CRITERIA REFERENCE:**")
        answer_parts.append("• GPA 3.0-3.4: 20% scholarship")
        answer_parts.append("• GPA 3.5-5.0: 50% scholarship") 
        answer_parts.append("• B.Tech - All Specialization: 50% eligible")
        answer_parts.append("• Applies to tuition fee only")
        answer_parts.append("• Continuation: Pass + 75% attendance required")
        
        return "\n".join(answer_parts)


def test_official_integration():
    """Test the official integration with sample questions."""
    
    calculator = OfficialShardaScholarshipCalculator()
    
    test_cases = [
        {
            "question": "My SSC GPA is 3.17 and HSC GPA is 3.50. What scholarship for CSE at Sharda?",
            "ssc_text": "SSC GPA is 3.17",
            "hsc_text": "HSC GPA is 3.50",
            "program": "B.Tech CSE"
        },
        {
            "question": "I have 85% in SSC and 90% in HSC. What's the scholarship for B.Tech at Sharda?",
            "ssc_text": "85% in SSC",
            "hsc_text": "90% in HSC", 
            "program": "B.Tech"
        },
        {
            "question": "My diploma CGPA is 3.2. What about scholarship for lateral entry to CSE?",
            "ssc_text": "",
            "hsc_text": "diploma CGPA is 3.2",
            "program": "B.Tech CSE"
        }
    ]
    
    print("🎓 OFFICIAL SHARDA UNIVERSITY SCHOLARSHIP INTEGRATION TEST")
    print("=" * 70)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 TEST CASE {i}:")
        print(f"❓ Question: {case['question']}")
        print("-" * 50)
        
        answer = calculator.generate_comprehensive_answer(
            case["question"], case["ssc_text"], case["hsc_text"], case["program"]
        )
        
        print(answer)
        print("=" * 70)
    
    print("\n✅ OFFICIAL INTEGRATION TESTING COMPLETE!")


if __name__ == "__main__":
    test_official_integration()
