#!/usr/bin/env python3
"""
🧪 Test Fixed Production TXT Dataset Generator
===============================================

Quick test to validate the semantic alignment fixes.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from production_txt_dataset_generator_fixed import FixedProductionTxtDatasetGenerator, QuestionType, StudentPersona

async def test_semantic_alignment():
    """Test the semantic alignment validation."""
    
    print("🧪 Testing Fixed Dataset Generator - Semantic Alignment")
    print("=" * 60)
    
    # Initialize the fixed generator
    generator = FixedProductionTxtDatasetGenerator()
    
    # Test cases: Question, Answer, Expected Result
    test_cases = [
        {
            "question": "What scholarship can I get for B.Tech CSE at Sharda University?",
            "answer": "For B.Tech CSE at Sharda University, students with 85%+ marks get 50% scholarship. GPA requirements are strictly enforced.",
            "classification": {"content_type": "financial", "universities": ["sharda"], "programs": ["B.Tech CSE"]},
            "expected": True,
            "description": "✅ Correct: Scholarship question gets scholarship answer"
        },
        {
            "question": "What scholarship can I get for B.Tech CSE at Sharda University?", 
            "answer": "Student visa duration is 12 months with multiple entry facility. Embassy processing takes 15-20 days.",
            "classification": {"content_type": "financial", "universities": ["sharda"], "programs": ["B.Tech CSE"]},
            "expected": False,
            "description": "❌ Incorrect: Scholarship question gets visa answer"
        },
        {
            "question": "What is the admission process for B.Tech at Amity University?",
            "answer": "Step 1: Submit online application. Step 2: Upload documents. Step 3: Pay application fee. Contact admissions@amity.edu",
            "classification": {"content_type": "process", "universities": ["amity"], "programs": ["B.Tech"]},
            "expected": True,
            "description": "✅ Correct: Process question gets process answer"
        },
        {
            "question": "What documents are required for B.Tech admission?",
            "answer": "Required documents: HSC certificate, passport copy, 10th marksheet, birth certificate, medical certificate.",
            "classification": {"content_type": "documents", "universities": ["sharda"], "programs": ["B.Tech"]},
            "expected": True,
            "description": "✅ Correct: Document question gets document answer"
        },
        {
            "question": "What documents are required for B.Tech admission?",
            "answer": "Visa processing time varies. Embassy appointments take 2-3 weeks. Duration depends on document verification.",
            "classification": {"content_type": "documents", "universities": ["sharda"], "programs": ["B.Tech"]},
            "expected": False,
            "description": "❌ Incorrect: Document question gets visa answer"
        }
    ]
    
    # Run tests
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Question: {test_case['question']}")
        print(f"Answer: {test_case['answer'][:100]}...")
        
        # Test semantic alignment
        result = generator._validate_semantic_alignment(
            test_case["question"],
            test_case["answer"], 
            test_case["classification"]
        )
        
        if result == test_case["expected"]:
            print(f"✅ PASSED: Expected {test_case['expected']}, Got {result}")
            passed += 1
        else:
            print(f"❌ FAILED: Expected {test_case['expected']}, Got {result}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"🧪 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Semantic alignment validation working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check semantic alignment logic.")
        return False

async def test_content_extraction():
    """Test content extraction and classification."""
    
    print(f"\n🔍 Testing Content Classification")
    print("=" * 40)
    
    generator = FixedProductionTxtDatasetGenerator()
    
    # Test paragraphs
    test_paragraphs = [
        {
            "content": "Sharda University offers merit scholarships for B.Tech CSE students. Students with 85%+ marks get 50% scholarship. GPA 4.0+ gets additional benefits.",
            "expected_type": "financial"
        },
        {
            "content": "The admission process for B.Tech at Amity University follows these steps: 1) Online application 2) Document submission 3) Interview 4) Fee payment",
            "expected_type": "process"
        },
        {
            "content": "Required documents for B.Tech admission: HSC certificate, passport copy, birth certificate, medical certificate, academic transcripts",
            "expected_type": "documents"
        },
        {
            "content": "Compare Sharda vs Amity University for B.Tech CSE. Sharda offers better ROI with lower fees. Amity has premium facilities but higher cost.",
            "expected_type": "comparison"
        }
    ]
    
    correct = 0
    total = len(test_paragraphs)
    
    for i, test in enumerate(test_paragraphs, 1):
        classification = generator._classify_content_type(test["content"])
        content_type = classification["content_type"]
        
        print(f"Test {i}: {test['content'][:50]}...")
        print(f"Expected: {test['expected_type']}, Got: {content_type}")
        
        if content_type == test['expected_type']:
            print("✅ PASSED")
            correct += 1
        else:
            print("❌ FAILED")
        print()
    
    print(f"🔍 Classification Results: {correct}/{total} correct")
    return correct == total

async def test_quality_metrics():
    """Test enhanced quality metrics calculation."""
    
    print(f"\n📊 Testing Quality Metrics")
    print("=" * 30)
    
    generator = FixedProductionTxtDatasetGenerator()
    
    # Test case: Good quality Q&A
    test_qa = {
        "question": "What scholarship can I get for B.Tech CSE at Sharda University with good grades?",
        "answer": "For B.Tech CSE at Sharda University, students with 85%+ marks are eligible for 50% merit scholarship. Students with 75-84% get 25% scholarship. Minimum GPA requirement is 3.5 for scholarship consideration.",
        "paragraph": "Sharda University merit scholarship policy: B.Tech CSE students with 85% and above marks get 50% scholarship on tuition fees. Students scoring 75-84% receive 25% scholarship. Minimum GPA 3.5 required for all scholarships.",
        "classification": {
            "content_type": "financial",
            "universities": ["sharda"],
            "programs": ["B.Tech CSE"],
            "has_financial_info": True
        }
    }
    
    metrics = generator._calculate_enhanced_quality_metrics(
        test_qa["question"],
        test_qa["answer"],
        test_qa["paragraph"],
        test_qa["classification"]
    )
    
    print(f"📈 Quality Metrics:")
    for metric, value in metrics.items():
        print(f"• {metric}: {value:.3f}")
    
    # Check if metrics meet thresholds
    print(f"\n🎯 Threshold Check:")
    passed_metrics = 0
    total_metrics = len(generator.quality_thresholds)
    
    for metric, threshold in generator.quality_thresholds.items():
        score = metrics.get(metric, 0)
        passed = score >= threshold
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"• {metric}: {score:.3f} >= {threshold} {status}")
        if passed:
            passed_metrics += 1
    
    print(f"\n📊 Quality Check: {passed_metrics}/{total_metrics} metrics passed")
    return passed_metrics == total_metrics

async def main():
    """Run all tests."""
    
    print("🎯 FIXED PRODUCTION TXT DATASET GENERATOR - VALIDATION TESTS")
    print("=" * 70)
    
    # Run tests
    test1 = await test_semantic_alignment()
    test2 = await test_content_extraction() 
    test3 = await test_quality_metrics()
    
    print(f"\n{'='*70}")
    print("🏆 FINAL TEST RESULTS")
    print("=" * 70)
    
    tests = [
        ("Semantic Alignment", test1),
        ("Content Classification", test2), 
        ("Quality Metrics", test3)
    ]
    
    passed_tests = sum(1 for _, result in tests if result)
    total_tests = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"• {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} test suites passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Fixed dataset generator is working correctly")
        print("✅ Semantic alignment validation implemented")
        print("✅ Quality metrics enhanced")
        print("✅ Content classification improved")
        print("\n🚀 Ready to generate high-quality Q&A datasets!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test suite(s) failed")
        print("🔧 Please review the implementation")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
