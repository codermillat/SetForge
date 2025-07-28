#!/usr/bin/env python3
"""
Enhanced Grade Scale Detection and Conversion System
Handles GPA (5.0), CGPA (4.0), and Percentage (100) scales for different education levels.
"""

import json
import re
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class EducationLevel(Enum):
    """Education levels with their corresponding grading systems."""
    SSC = "ssc"  # GPA out of 5
    HSC = "hsc"  # GPA out of 5
    DIPLOMA = "diploma"  # CGPA out of 4
    BACHELOR = "bachelor"  # CGPA out of 4


class GradingScale(Enum):
    """Different grading scales used in education."""
    GPA_5 = "gpa_5"  # Out of 5.0 (SSC/HSC)
    CGPA_4 = "cgpa_4"  # Out of 4.0 (Diploma/Bachelor)
    PERCENTAGE = "percentage"  # Out of 100


@dataclass
class GradeInfo:
    """Information about a grade with its scale and converted values."""
    original_value: float
    original_scale: GradingScale
    education_level: EducationLevel
    normalized_gpa_5: float  # Always convert to GPA out of 5 for scholarship calculation
    confidence: float  # How confident we are about the scale detection
    needs_verification: bool  # Whether this needs manual verification


class GradeScaleDetector:
    """Detects and converts between different grading scales."""
    
    # Education level keywords
    SSC_KEYWORDS = ["ssc", "o-levels", "o-level", "madrasa", "technical", "secondary", "dakhil", "class 10", "10th"]
    HSC_KEYWORDS = ["hsc", "higher secondary", "a-levels", "a-level", "madrasah", "alim", "class 12", "12th"]
    DIPLOMA_KEYWORDS = ["diploma", "polytechnic", "technical diploma"]
    BACHELOR_KEYWORDS = ["bachelor", "bachelor's", "bachelors", "b.tech", "btech", "b.sc", "bsc", "b.a", "ba"]
    
    def __init__(self):
        self.grade_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for grade detection."""
        return {
            "grade_with_scale": re.compile(r"(\d+\.?\d*)\s*(?:out of|/)\s*(\d+)", re.IGNORECASE),
            "percentage": re.compile(r"(\d+\.?\d*)%", re.IGNORECASE),
            "gpa_mention": re.compile(r"gpa\s*(\d+\.?\d*)", re.IGNORECASE),
            "cgpa_mention": re.compile(r"cgpa\s*(\d+\.?\d*)", re.IGNORECASE),
            "grade_number": re.compile(r"(\d+\.?\d*)", re.IGNORECASE)
        }
    
    def detect_education_level(self, text: str) -> EducationLevel:
        """Detect education level from text."""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in self.SSC_KEYWORDS):
            return EducationLevel.SSC
        elif any(keyword in text_lower for keyword in self.HSC_KEYWORDS):
            return EducationLevel.HSC
        elif any(keyword in text_lower for keyword in self.DIPLOMA_KEYWORDS):
            return EducationLevel.DIPLOMA
        elif any(keyword in text_lower for keyword in self.BACHELOR_KEYWORDS):
            return EducationLevel.BACHELOR
        
        # Default to HSC if not specified (most common case)
        return EducationLevel.HSC
    
    def detect_grading_scale(self, value: float, text: str, education_level: EducationLevel) -> Tuple[GradingScale, float]:
        """
        Detect grading scale based on value, context, and education level.
        Returns (scale, confidence)
        """
        text_lower = text.lower()
        
        # Explicit scale mentioned
        if "%" in text or "percent" in text_lower:
            return GradingScale.PERCENTAGE, 0.95
        
        if "gpa" in text_lower and "cgpa" not in text_lower:
            return GradingScale.GPA_5, 0.9
        
        if "cgpa" in text_lower:
            return GradingScale.CGPA_4, 0.9
        
        # Scale detection based on value ranges
        if value >= 50:  # Likely percentage
            return GradingScale.PERCENTAGE, 0.8
        elif value <= 4.0:  # Likely CGPA or low GPA
            if education_level in [EducationLevel.DIPLOMA, EducationLevel.BACHELOR]:
                return GradingScale.CGPA_4, 0.7
            else:
                return GradingScale.GPA_5, 0.6  # Could be low GPA out of 5
        elif value <= 5.0:  # Likely GPA out of 5
            return GradingScale.GPA_5, 0.8
        else:
            # Value > 5, likely percentage without % symbol
            return GradingScale.PERCENTAGE, 0.7
    
    def convert_to_gpa_5(self, value: float, scale: GradingScale) -> float:
        """Convert any scale to GPA out of 5 for standardized comparison."""
        if scale == GradingScale.GPA_5:
            return value
        elif scale == GradingScale.CGPA_4:
            return (value / 4.0) * 5.0
        elif scale == GradingScale.PERCENTAGE:
            # Convert percentage to GPA (simplified conversion)
            if value >= 90:
                return 5.0
            elif value >= 80:
                return 4.5
            elif value >= 70:
                return 4.0
            elif value >= 60:
                return 3.5
            elif value >= 50:
                return 3.0
            elif value >= 40:
                return 2.5
            else:
                return 2.0
        
        return value
    
    def parse_grade(self, text: str, context: str = "") -> Optional[GradeInfo]:
        """
        Parse grade from text with context.
        
        Args:
            text: Text containing the grade
            context: Additional context about education level
        
        Returns:
            GradeInfo object or None if parsing fails
        """
        full_text = f"{text} {context}".lower()
        
        # Detect education level
        education_level = self.detect_education_level(full_text)
        
        # Try different patterns
        # Pattern 1: Explicit scale (e.g., "3.5 out of 5", "80/100")
        match = self.grade_patterns["grade_with_scale"].search(text)
        if match:
            value = float(match.group(1))
            scale_max = float(match.group(2))
            
            if scale_max == 100:
                scale = GradingScale.PERCENTAGE
                confidence = 0.95
            elif scale_max == 5:
                scale = GradingScale.GPA_5
                confidence = 0.95
            elif scale_max == 4:
                scale = GradingScale.CGPA_4
                confidence = 0.95
            else:
                # Unknown scale
                scale = GradingScale.GPA_5  # Default
                confidence = 0.3
            
            normalized = self.convert_to_gpa_5(value, scale)
            return GradeInfo(
                original_value=value,
                original_scale=scale,
                education_level=education_level,
                normalized_gpa_5=normalized,
                confidence=confidence,
                needs_verification=confidence < 0.8
            )
        
        # Pattern 2: Percentage with % symbol
        match = self.grade_patterns["percentage"].search(text)
        if match:
            value = float(match.group(1))
            normalized = self.convert_to_gpa_5(value, GradingScale.PERCENTAGE)
            return GradeInfo(
                original_value=value,
                original_scale=GradingScale.PERCENTAGE,
                education_level=education_level,
                normalized_gpa_5=normalized,
                confidence=0.95,
                needs_verification=False
            )
        
        # Pattern 3: Explicit GPA mention
        match = self.grade_patterns["gpa_mention"].search(text)
        if match:
            value = float(match.group(1))
            normalized = self.convert_to_gpa_5(value, GradingScale.GPA_5)
            return GradeInfo(
                original_value=value,
                original_scale=GradingScale.GPA_5,
                education_level=education_level,
                normalized_gpa_5=normalized,
                confidence=0.9,
                needs_verification=False
            )
        
        # Pattern 4: Explicit CGPA mention
        match = self.grade_patterns["cgpa_mention"].search(text)
        if match:
            value = float(match.group(1))
            normalized = self.convert_to_gpa_5(value, GradingScale.CGPA_4)
            return GradeInfo(
                original_value=value,
                original_scale=GradingScale.CGPA_4,
                education_level=education_level,
                normalized_gpa_5=normalized,
                confidence=0.9,
                needs_verification=False
            )
        
        # Pattern 5: Just a number - need to infer scale
        match = self.grade_patterns["grade_number"].search(text)
        if match:
            value = float(match.group(1))
            scale, confidence = self.detect_grading_scale(value, full_text, education_level)
            normalized = self.convert_to_gpa_5(value, scale)
            
            return GradeInfo(
                original_value=value,
                original_scale=scale,
                education_level=education_level,
                normalized_gpa_5=normalized,
                confidence=confidence,
                needs_verification=confidence < 0.8
            )
        
        return None


class EnhancedScholarshipCalculator:
    """Enhanced scholarship calculator with grade scale detection."""
    
    def __init__(self):
        self.grade_detector = GradeScaleDetector()
        
        # Scholarship criteria for different universities and programs
        self.scholarship_criteria = {
            "sharda": {
                "btech": [
                    {"min_gpa": 3.5, "max_gpa": 5.0, "percentage": 50, "tier": "CGPA 3.5-5.0"},
                    {"min_gpa": 3.0, "max_gpa": 3.4, "percentage": 20, "tier": "CGPA 3.0-3.4"}
                ],
                "other": [
                    {"min_gpa": 3.5, "max_gpa": 5.0, "percentage": 40, "tier": "CGPA 3.5-5.0"},
                    {"min_gpa": 3.0, "max_gpa": 3.4, "percentage": 15, "tier": "CGPA 3.0-3.4"}
                ]
            }
        }
    
    def calculate_scholarship(self, ssc_text: str, hsc_text: str, 
                            university: str = "sharda", program: str = "btech") -> Dict[str, Any]:
        """
        Calculate scholarship eligibility with enhanced grade detection.
        
        Args:
            ssc_text: Text containing SSC grade
            hsc_text: Text containing HSC grade
            university: University name
            program: Program name
        
        Returns:
            Scholarship calculation results
        """
        # Parse grades
        ssc_info = self.grade_detector.parse_grade(ssc_text, "ssc secondary")
        hsc_info = self.grade_detector.parse_grade(hsc_text, "hsc higher secondary")
        
        # Get scholarship criteria
        criteria = self.scholarship_criteria.get(university, {}).get(program, [])
        
        # Calculate based on HSC (primary criteria)
        scholarship_result = {"percentage": 0, "tier": "No scholarship eligibility"}
        if hsc_info:
            for criterion in criteria:
                if criterion["min_gpa"] <= hsc_info.normalized_gpa_5 <= criterion["max_gpa"]:
                    scholarship_result = {
                        "percentage": criterion["percentage"],
                        "tier": criterion["tier"]
                    }
                    break
        
        # Check for warnings
        warnings = []
        if ssc_info and ssc_info.normalized_gpa_5 < 3.5:
            warnings.append({
                "type": "low_ssc",
                "message": f"SSC grade ({ssc_info.original_value} {ssc_info.original_scale.value}) is below typical 3.5 requirement"
            })
        
        if ssc_info and ssc_info.needs_verification:
            warnings.append({
                "type": "scale_uncertainty",
                "message": f"SSC grade scale detection uncertain (confidence: {ssc_info.confidence:.1%})"
            })
        
        if hsc_info and hsc_info.needs_verification:
            warnings.append({
                "type": "scale_uncertainty", 
                "message": f"HSC grade scale detection uncertain (confidence: {hsc_info.confidence:.1%})"
            })
        
        return {
            "ssc_info": ssc_info.__dict__ if ssc_info else None,
            "hsc_info": hsc_info.__dict__ if hsc_info else None,
            "scholarship": scholarship_result,
            "warnings": warnings,
            "requires_verification": bool(warnings),
            "contact_required": len(warnings) > 0
        }


# Test cases for the enhanced system
def test_grade_detection():
    """Test the grade detection system with various inputs."""
    detector = GradeScaleDetector()
    calculator = EnhancedScholarshipCalculator()
    
    test_cases = [
        # Different formats for SSC and HSC
        ("My ssc result is 3.17", "My hsc gpa is 3.50"),
        ("SSC: 3.17 out of 5", "HSC: 3.50/5"),
        ("I got 85% in SSC", "HSC result: 90%"),
        ("SSC cgpa 3.2", "HSC cgpa 3.6"),  # Wrong usage but we handle it
        ("My SSC was 3.27", "HSC: 3.8"),  # No scale mentioned
        ("SSC result: 80", "HSC: 85"),  # Numbers without % - should detect as percentage
        ("Secondary school: 3.1", "Higher secondary: 3.7"),
        ("O-levels: 3.4", "A-levels: 3.9"),
        ("Class 10: 75%", "Class 12: 82%"),
        ("Dakhil: 3.3", "Alim: 3.6"),
    ]
    
    print("🧪 TESTING ENHANCED GRADE DETECTION SYSTEM")
    print("=" * 60)
    
    for i, (ssc_text, hsc_text) in enumerate(test_cases, 1):
        print(f"\n📝 TEST CASE {i}:")
        print(f"SSC Input: '{ssc_text}'")
        print(f"HSC Input: '{hsc_text}'")
        
        result = calculator.calculate_scholarship(ssc_text, hsc_text)
        
        # Display results
        if result["ssc_info"]:
            ssc = result["ssc_info"]
            print(f"SSC Detected: {ssc['original_value']} ({ssc['original_scale']}) → GPA {ssc['normalized_gpa_5']:.2f}/5")
        
        if result["hsc_info"]:
            hsc = result["hsc_info"]
            print(f"HSC Detected: {hsc['original_value']} ({hsc['original_scale']}) → GPA {hsc['normalized_gpa_5']:.2f}/5")
        
        print(f"Scholarship: {result['scholarship']['percentage']}% ({result['scholarship']['tier']})")
        
        if result["warnings"]:
            print("⚠️ Warnings:")
            for warning in result["warnings"]:
                print(f"  - {warning['message']}")
        
        print("-" * 40)


if __name__ == "__main__":
    test_grade_detection()
