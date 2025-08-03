#!/usr/bin/env python3
"""
SetForge Utilities - Bangladeshi Education System Support
=========================================================

Comprehensive utilities for handling Bangladeshi grading systems,
qualification equivalents, and grade conversions for Indian universities.
"""

import random
from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass

class BangladeshiQualification(Enum):
    """Bangladeshi educational qualifications."""
    SSC = "SSC"
    DAKHIL = "Dakhil"
    HSC = "HSC"
    ALIM = "Alim"
    DIPLOMA = "Diploma"
    BACHELOR = "Bachelor"
    HONOURS = "Honours"
    MASTERS = "Masters"

class IndianEquivalent(Enum):
    """Indian equivalent qualifications."""
    CLASS_10 = "Class 10"
    CLASS_12 = "Class 12"
    POLYTECHNIC_DIPLOMA = "Polytechnic Diploma"
    UG_DEGREE = "UG Degree"
    PG_DEGREE = "PG Degree"

@dataclass
class GradeProfile:
    """Complete grade profile for a Bangladeshi student."""
    qualification: BangladeshiQualification
    gpa_cgpa: float
    percentage: Optional[float]
    scale: str
    indian_equivalent: IndianEquivalent
    indian_cgpa_10: float
    grade_letter: str
    is_scholarship_eligible: bool
    performance_category: str

class BangladeshiGradingSystem:
    """Comprehensive Bangladeshi grading system handler."""
    
    # GPA to Letter Grade mappings (5-point scale)
    GPA_5_SCALE = {
        5.0: "A+",
        4.0: "A",
        3.5: "A-",
        3.0: "B",
        2.5: "C",
        2.0: "D",
        1.0: "F"
    }
    
    # Qualification equivalents
    QUALIFICATION_MAPPING = {
        BangladeshiQualification.SSC: IndianEquivalent.CLASS_10,
        BangladeshiQualification.DAKHIL: IndianEquivalent.CLASS_10,
        BangladeshiQualification.HSC: IndianEquivalent.CLASS_12,
        BangladeshiQualification.ALIM: IndianEquivalent.CLASS_12,
        BangladeshiQualification.DIPLOMA: IndianEquivalent.POLYTECHNIC_DIPLOMA,
        BangladeshiQualification.BACHELOR: IndianEquivalent.UG_DEGREE,
        BangladeshiQualification.HONOURS: IndianEquivalent.UG_DEGREE,
        BangladeshiQualification.MASTERS: IndianEquivalent.PG_DEGREE
    }
    
    @staticmethod
    def gpa_5_to_percentage(gpa: float) -> float:
        """Convert 5-point GPA to percentage."""
        if gpa >= 5.0: return 95.0
        elif gpa >= 4.0: return 85.0
        elif gpa >= 3.5: return 78.0
        elif gpa >= 3.0: return 70.0
        elif gpa >= 2.5: return 60.0
        elif gpa >= 2.0: return 50.0
        else: return 40.0
    
    @staticmethod
    def diploma_cgpa_to_percentage(cgpa: float) -> float:
        """Convert Diploma CGPA (4-point) to percentage."""
        return cgpa * 25
    
    @staticmethod
    def percentage_to_indian_cgpa_10(percentage: float) -> float:
        """Convert percentage to Indian 10-point CGPA."""
        return percentage / 9.5
    
    @staticmethod
    def gpa_5_to_indian_cgpa_10(gpa: float) -> float:
        """Convert 5-point GPA to Indian 10-point CGPA."""
        percentage = BangladeshiGradingSystem.gpa_5_to_percentage(gpa)
        return BangladeshiGradingSystem.percentage_to_indian_cgpa_10(percentage)
    
    @staticmethod
    def get_letter_grade(gpa: float, scale: str = "5") -> str:
        """Get letter grade for given GPA."""
        if scale == "5":
            for grade_point, letter in BangladeshiGradingSystem.GPA_5_SCALE.items():
                if gpa >= grade_point:
                    return letter
            return "F"
        else:
            # For 4-point scale (Diploma)
            if gpa >= 3.75: return "A+"
            elif gpa >= 3.5: return "A"
            elif gpa >= 3.25: return "A-"
            elif gpa >= 3.0: return "B+"
            elif gpa >= 2.75: return "B"
            elif gpa >= 2.5: return "B-"
            elif gpa >= 2.25: return "C+"
            elif gpa >= 2.0: return "C"
            else: return "F"
    
    @staticmethod
    def is_scholarship_eligible(qualification: BangladeshiQualification, 
                              gpa_cgpa: float, scale: str = "5") -> bool:
        """Check scholarship eligibility based on grades."""
        if scale == "5":
            return gpa_cgpa >= 4.0  # A grade or above
        else:  # 4-point scale
            return gpa_cgpa >= 3.5  # A- or above
    
    @staticmethod
    def get_performance_category(gpa_cgpa: float, scale: str = "5") -> str:
        """Categorize student performance."""
        if scale == "5":
            if gpa_cgpa >= 4.5: return "Excellent"
            elif gpa_cgpa >= 4.0: return "Very Good"
            elif gpa_cgpa >= 3.5: return "Good"
            elif gpa_cgpa >= 3.0: return "Average"
            else: return "Below Average"
        else:  # 4-point scale
            if gpa_cgpa >= 3.75: return "Excellent"
            elif gpa_cgpa >= 3.5: return "Very Good"
            elif gpa_cgpa >= 3.0: return "Good"
            elif gpa_cgpa >= 2.5: return "Average"
            else: return "Below Average"
    
    @staticmethod
    def normalize_grade(grade_text: str) -> float:
        """
        Normalize various Bangladeshi grade formats to a 0-1 scale.
        
        Args:
            grade_text: Grade in various formats (e.g., "SSC: 4.5/5", "HSC: 85%")
            
        Returns:
            Normalized grade score (0.0 to 1.0)
        """
        import re
        
        grade_text = grade_text.strip().upper()
        
        # Extract percentage patterns first (XX%)
        percentage_pattern = r'(\d+\.?\d*)%'
        percentage_match = re.search(percentage_pattern, grade_text)
        
        if percentage_match:
            percentage = float(percentage_match.group(1))
            return min(percentage / 100.0, 1.0)
        
        # Extract GPA patterns (X.X/Y or X.X out of Y)
        gpa_pattern = r'(\d+\.?\d*)\s*[/]\s*(\d+\.?\d*)'
        gpa_match = re.search(gpa_pattern, grade_text)
        
        if gpa_match:
            score = float(gpa_match.group(1))
            max_score = float(gpa_match.group(2))
            return min(score / max_score, 1.0)
        
        # Try to extract just a number and infer scale
        number_pattern = r'(\d+\.?\d*)'
        number_match = re.search(number_pattern, grade_text)
        
        if number_match:
            score = float(number_match.group(1))
            
            # Determine scale based on qualification type and score range
            if 'SSC' in grade_text or 'HSC' in grade_text or 'DAKHIL' in grade_text or 'ALIM' in grade_text:
                # 5-point scale for SSC/HSC
                if score <= 5.0:
                    return score / 5.0
                else:
                    # Assume it's a percentage if > 5
                    return min(score / 100.0, 1.0)
                    
            elif 'BACHELOR' in grade_text or 'HONOURS' in grade_text or 'MASTERS' in grade_text or 'DIPLOMA' in grade_text:
                # 4-point scale for higher education
                if score <= 4.0:
                    return score / 4.0
                else:
                    # Assume it's a percentage if > 4
                    return min(score / 100.0, 1.0)
            else:
                # Default heuristic based on score range
                if score <= 4.0:
                    return score / 4.0  # Assume 4-point scale
                elif score <= 5.0:
                    return score / 5.0  # Assume 5-point scale
                else:
                    return min(score / 100.0, 1.0)  # Assume percentage
        
        # Default fallback for unrecognized patterns
        return 0.0

def normalize_bangladeshi_grade(grade_text: str) -> float:
    """Wrapper function for normalize_grade to maintain compatibility."""
    return BangladeshiGradingSystem.normalize_grade(grade_text)

def is_valid_bangladeshi_grade(grade_text: str) -> bool:
    """Check if a grade text is valid Bangladeshi grade format."""
    try:
        normalized = normalize_bangladeshi_grade(grade_text)
        return 0.0 <= normalized <= 1.0 and normalized > 0.0
    except:
        return False

class StudentProfileGenerator:
    """Generate realistic Bangladeshi student profiles."""
    
    def __init__(self):
        self.grading_system = BangladeshiGradingSystem()
    
    def generate_realistic_grade_profile(self, 
                                       qualification: BangladeshiQualification) -> GradeProfile:
        """Generate a realistic grade profile for given qualification."""
        
        if qualification in [BangladeshiQualification.SSC, BangladeshiQualification.DAKHIL,
                           BangladeshiQualification.HSC, BangladeshiQualification.ALIM]:
            # 5-point GPA scale
            gpa = round(random.uniform(2.5, 5.0), 2)
            percentage = self.grading_system.gpa_5_to_percentage(gpa)
            scale = "5"
            
        elif qualification == BangladeshiQualification.DIPLOMA:
            # 4-point CGPA scale
            gpa = round(random.uniform(2.0, 4.0), 2)
            percentage = self.grading_system.diploma_cgpa_to_percentage(gpa)
            scale = "4"
            
        else:  # Bachelor, Honours, Masters
            # Can be either percentage or 4-point CGPA
            if random.choice([True, False]):
                # Percentage system
                percentage = round(random.uniform(55.0, 95.0), 1)
                gpa = percentage / 25  # Approximate CGPA
                scale = "100"
            else:
                # 4-point CGPA
                gpa = round(random.uniform(2.0, 4.0), 2)
                percentage = gpa * 25
                scale = "4"
        
        # Calculate Indian equivalents
        indian_equivalent = self.grading_system.QUALIFICATION_MAPPING[qualification]
        indian_cgpa_10 = self.grading_system.percentage_to_indian_cgpa_10(percentage)
        
        # Get letter grade and eligibility
        letter_grade = self.grading_system.get_letter_grade(gpa, scale.replace("100", "4"))
        is_eligible = self.grading_system.is_scholarship_eligible(qualification, gpa, scale.replace("100", "4"))
        performance = self.grading_system.get_performance_category(gpa, scale.replace("100", "4"))
        
        return GradeProfile(
            qualification=qualification,
            gpa_cgpa=gpa,
            percentage=percentage,
            scale=scale,
            indian_equivalent=indian_equivalent,
            indian_cgpa_10=round(indian_cgpa_10, 2),
            grade_letter=letter_grade,
            is_scholarship_eligible=is_eligible,
            performance_category=performance
        )
    
    def generate_diverse_student_profiles(self, count: int = 10) -> List[GradeProfile]:
        """Generate diverse student profiles covering different qualifications."""
        profiles = []
        qualifications = list(BangladeshiQualification)
        
        for i in range(count):
            qual = random.choice(qualifications)
            profile = self.generate_realistic_grade_profile(qual)
            profiles.append(profile)
        
        return profiles
    
    def format_grade_for_question(self, profile: GradeProfile) -> str:
        """Format grade appropriately for question templates."""
        if profile.scale == "5":
            return f"{profile.qualification.value} GPA {profile.gpa_cgpa}"
        elif profile.scale == "4":
            if profile.qualification == BangladeshiQualification.DIPLOMA:
                return f"Diploma CGPA {profile.gpa_cgpa}"
            else:
                return f"{profile.qualification.value} CGPA {profile.gpa_cgpa}"
        else:  # percentage
            return f"{profile.qualification.value} {profile.percentage}%"

class UniversityRequirements:
    """Handle Indian university admission requirements for Bangladeshi students."""
    
    SCHOLARSHIP_THRESHOLDS = {
        "merit_100": {"min_indian_cgpa": 9.0, "percentage": 85.5},
        "merit_75": {"min_indian_cgpa": 8.5, "percentage": 80.75},
        "merit_50": {"min_indian_cgpa": 8.0, "percentage": 76.0},
        "merit_25": {"min_indian_cgpa": 7.5, "percentage": 71.25}
    }
    
    @staticmethod
    def get_eligible_scholarships(grade_profile: GradeProfile) -> List[Dict]:
        """Get eligible scholarships for a grade profile."""
        eligible = []
        
        for scholarship, threshold in UniversityRequirements.SCHOLARSHIP_THRESHOLDS.items():
            if grade_profile.indian_cgpa_10 >= threshold["min_indian_cgpa"]:
                eligible.append({
                    "type": scholarship,
                    "percentage": scholarship.split("_")[1] + "%",
                    "required_cgpa": threshold["min_indian_cgpa"],
                    "student_cgpa": grade_profile.indian_cgpa_10
                })
        
        return eligible
    
    @staticmethod
    def estimate_admission_chances(grade_profile: GradeProfile, 
                                 university_tier: str = "mid") -> Dict:
        """Estimate admission chances based on grades."""
        chances = {
            "high": 90,
            "mid": 70,
            "low": 40
        }
        
        base_chance = chances.get(university_tier, 70)
        
        # Adjust based on performance
        if grade_profile.performance_category == "Excellent":
            adjustment = 20
        elif grade_profile.performance_category == "Very Good":
            adjustment = 10
        elif grade_profile.performance_category == "Good":
            adjustment = 0
        elif grade_profile.performance_category == "Average":
            adjustment = -15
        else:
            adjustment = -30
        
        final_chance = max(10, min(95, base_chance + adjustment))
        
        return {
            "admission_chance": final_chance,
            "recommendation": "Strong candidate" if final_chance >= 80 else 
                           "Good candidate" if final_chance >= 60 else "Consider backup options",
            "grade_category": grade_profile.performance_category,
            "indian_cgpa": grade_profile.indian_cgpa_10
        }

def format_bangladeshi_grade_context(profile: GradeProfile) -> str:
    """Format grade information for context in Q&A generation."""
    context_parts = [
        f"Student has {profile.qualification.value} with {profile.grade_letter} grade",
        f"GPA/CGPA: {profile.gpa_cgpa} on {profile.scale}-point scale",
        f"Equivalent percentage: {profile.percentage:.1f}%",
        f"Indian equivalent: {profile.indian_equivalent.value}",
        f"Indian CGPA (10-point): {profile.indian_cgpa_10}",
        f"Performance category: {profile.performance_category}",
        f"Scholarship eligible: {'Yes' if profile.is_scholarship_eligible else 'No'}"
    ]
    
    return ". ".join(context_parts)

def generate_realistic_grade_entities() -> Dict[str, List[str]]:
    """Generate realistic grade entities for template substitution."""
    generator = StudentProfileGenerator()
    profiles = generator.generate_diverse_student_profiles(50)
    
    entities = {
        'grade_types': [],
        'grades': [],
        'grade_contexts': [],
        'qualifications': []
    }
    
    for profile in profiles:
        # Grade type and value
        entities['grade_types'].append(profile.qualification.value)
        entities['grades'].append(str(profile.gpa_cgpa))
        entities['qualifications'].append(profile.qualification.value)
        
        # Full grade context
        formatted_grade = generator.format_grade_for_question(profile)
        entities['grade_contexts'].append(formatted_grade)
    
    # Remove duplicates and return unique lists
    for key in entities:
        entities[key] = list(set(entities[key]))
    
    return entities

# Example usage and testing
if __name__ == "__main__":
    # Test the grading system
    generator = StudentProfileGenerator()
    
    print("🎓 Bangladeshi Grading System Test")
    print("=" * 50)
    
    # Generate some sample profiles
    for i in range(5):
        qual = random.choice(list(BangladeshiQualification))
        profile = generator.generate_realistic_grade_profile(qual)
        
        print(f"\nStudent {i+1}:")
        print(f"  Qualification: {profile.qualification.value}")
        print(f"  Grade: {profile.gpa_cgpa} ({profile.grade_letter}) on {profile.scale}-point scale")
        print(f"  Percentage: {profile.percentage:.1f}%")
        print(f"  Indian CGPA: {profile.indian_cgpa_10}/10")
        print(f"  Performance: {profile.performance_category}")
        print(f"  Scholarship Eligible: {profile.is_scholarship_eligible}")
        
        # Show eligible scholarships
        scholarships = UniversityRequirements.get_eligible_scholarships(profile)
        if scholarships:
            print(f"  Eligible Scholarships: {', '.join([s['percentage'] for s in scholarships])}")
        else:
            print(f"  Eligible Scholarships: None")
