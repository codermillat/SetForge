#!/usr/bin/env python3
"""
Enhanced Dataset Generation CLI - Pure Dataset Creation Tool
Designed to outperform GPT-4 and Gemini 2.5 Pro in educational guidance.

Usage:
    python enhanced_dataset_cli.py generate --size 1000 --output superior_dataset.jsonl
    python enhanced_dataset_cli.py validate --input dataset.jsonl
    python enhanced_dataset_cli.py schema --check dataset.jsonl
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import random

# Import modular components
from modular_dataset_components import (
    QuestionGenerator, AnswerGenerator, MetadataExtractor, 
    QualityValidator, DatasetExporter, DatasetQAPair,
    QuestionType, ToneType, LanguageType
)

class EnhancedDatasetCLI:
    """Command-line interface for enhanced dataset generation."""
    
    def __init__(self):
        self.question_gen = QuestionGenerator()
        self.answer_gen = AnswerGenerator()
        self.metadata_extractor = MetadataExtractor()
        self.validator = QualityValidator()
        self.exporter = DatasetExporter()
        
        # University and program data
        self.universities = [
            "Sharda University", "Amity University", "Galgotias University", 
            "G.L. Bajaj Institute", "Noida International University"
        ]
        
        self.programs = [
            "B.Tech CSE", "B.Tech Mechanical", "B.Tech Civil", "BCA", "BBA", 
            "MBA", "MCA", "B.Sc IT", "B.Com", "LLB"
        ]
        
        self.grade_samples = [
            {"value": "3.5", "type": "GPA"}, {"value": "4.2", "type": "GPA"},
            {"value": "85%", "type": "percentage"}, {"value": "78%", "type": "percentage"},
            {"value": "3.8", "type": "CGPA"}, {"value": "90%", "type": "percentage"}
        ]
    
    def generate_balanced_contexts(self, target_size: int) -> List[Dict[str, Any]]:
        """Generate balanced contexts for diverse dataset."""
        contexts = []
        
        # Calculate distribution
        per_university = target_size // len(self.universities)
        per_question_type = target_size // len(QuestionType)
        
        for i in range(target_size):
            # Cycle through universities and question types for balance
            university = self.universities[i % len(self.universities)]
            question_type = list(QuestionType)[i % len(QuestionType)]
            program = random.choice(self.programs)
            grade_info = random.choice(self.grade_samples)
            
            context = {
                "university": university,
                "program": program,
                "grade_value": grade_info["value"],
                "grade_type": grade_info["type"],
                "question_type": question_type,
                "university1": university,
                "university2": random.choice([u for u in self.universities if u != university]),
                "academic_year": "2025-26",
                "scholarship_rate": str(random.randint(15, 65)),
                "target_audience": random.choice(["student", "parent", "agent"]),
                "tone": random.choice([t.value for t in ToneType]),
                "language": random.choice([l.value for l in LanguageType])
            }
            
            contexts.append(context)
        
        return contexts
    
    def generate_dataset(self, size: int, output_path: str) -> Dict[str, Any]:
        """Generate comprehensive dataset with your metadata structure."""
        print(f"🚀 Generating enhanced dataset with {size} Q&A pairs...")
        print(f"📁 Output: {output_path}")
        
        # Create output directory
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Generate balanced contexts
        contexts = self.generate_balanced_contexts(size)
        dataset = []
        generation_stats = {
            "total_generated": 0,
            "high_quality_count": 0,
            "university_distribution": {},
            "question_type_distribution": {},
            "average_quality_score": 0.0,
            "start_time": datetime.now().isoformat()
        }
        
        for i, context in enumerate(contexts):
            try:
                # Generate question
                questions = self.question_gen.generate_questions(
                    context["question_type"], context, 1
                )
                
                if not questions:
                    continue
                
                question = questions[0]
                
                # Generate answer
                answer = self.answer_gen.generate_answer(
                    question, context["question_type"], context
                )
                
                # Extract metadata
                metadata = self.metadata_extractor.extract_metadata(question, answer, context)
                
                # Create QA pair with your specified structure
                qa_pair = DatasetQAPair(
                    question=question,
                    answer=answer,
                    context=context["program"],
                    university=context["university"],
                    type=context["question_type"].value,
                    tone=context["tone"],
                    source="Enhanced SetForge Dataset Generator v2.0",
                    language=context["language"],
                    metadata=metadata
                )
                
                # Validate quality
                is_valid, quality_score, issues = self.validator.validate_qa_pair(qa_pair)
                qa_pair.quality_score = quality_score
                qa_pair.validation_passed = is_valid
                
                # Skip low-quality pairs
                if quality_score < 0.6:
                    continue
                
                dataset.append(qa_pair)
                
                # Update statistics
                generation_stats["total_generated"] += 1
                if quality_score >= 0.8:
                    generation_stats["high_quality_count"] += 1
                
                # Track distributions
                univ = context["university"]
                qtype = context["question_type"].value
                generation_stats["university_distribution"][univ] = generation_stats["university_distribution"].get(univ, 0) + 1
                generation_stats["question_type_distribution"][qtype] = generation_stats["question_type_distribution"].get(qtype, 0) + 1
                
                # Progress reporting
                if (i + 1) % 100 == 0:
                    print(f"📊 Generated {generation_stats['total_generated']} pairs ({i+1}/{size} processed)")
            
            except Exception as e:
                print(f"⚠️ Error generating pair {i+1}: {e}")
                continue
        
        # Calculate final statistics
        if dataset:
            total_quality = sum(pair.quality_score for pair in dataset)
            generation_stats["average_quality_score"] = total_quality / len(dataset)
        
        generation_stats["end_time"] = datetime.now().isoformat()
        generation_stats["final_dataset_size"] = len(dataset)
        
        # Export dataset
        self.exporter.export_jsonl(dataset, output_path)
        
        # Export generation report
        report_path = output_path.replace('.jsonl', '_generation_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(generation_stats, f, indent=2, ensure_ascii=False)
        
        # Get quality metrics
        quality_metrics = self.validator.get_quality_metrics(dataset)
        quality_report_path = output_path.replace('.jsonl', '_quality_report.json')
        self.exporter.export_validation_report(quality_metrics, quality_report_path)
        
        print(f"\n✅ Dataset generation completed!")
        print(f"📊 Generated: {len(dataset)} high-quality Q&A pairs")
        print(f"⭐ Average Quality Score: {generation_stats['average_quality_score']:.3f}")
        print(f"🏆 High Quality Pairs: {generation_stats['high_quality_count']}")
        print(f"📁 Files created:")
        print(f"   • Dataset: {output_path}")
        print(f"   • Generation Report: {report_path}")
        print(f"   • Quality Report: {quality_report_path}")
        
        return generation_stats
    
    def validate_dataset(self, input_path: str) -> Dict[str, Any]:
        """Validate existing dataset quality."""
        print(f"🔍 Validating dataset: {input_path}")
        
        if not os.path.exists(input_path):
            print(f"❌ File not found: {input_path}")
            return {}
        
        dataset = []
        
        # Load dataset
        with open(input_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())
                    qa_pair = DatasetQAPair(
                        question=data.get("question", ""),
                        answer=data.get("answer", ""),
                        context=data.get("context", ""),
                        university=data.get("university", ""),
                        type=data.get("type", ""),
                        tone=data.get("tone", ""),
                        source=data.get("source", ""),
                        language=data.get("language", ""),
                        metadata=data.get("metadata", {})
                    )
                    dataset.append(qa_pair)
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON error at line {line_num}: {e}")
                except Exception as e:
                    print(f"⚠️ Error processing line {line_num}: {e}")
        
        # Get quality metrics
        quality_metrics = self.validator.get_quality_metrics(dataset)
        
        print(f"\n📊 Validation Results:")
        print(f"   • Total pairs: {quality_metrics['total_pairs']}")
        print(f"   • Valid pairs: {quality_metrics['valid_pairs']}")
        print(f"   • Validity rate: {quality_metrics['validity_rate']:.1%}")
        print(f"   • Average quality: {quality_metrics['average_quality_score']:.3f}")
        print(f"   • High quality: {quality_metrics['quality_distribution']['high']}")
        print(f"   • Medium quality: {quality_metrics['quality_distribution']['medium']}")
        print(f"   • Low quality: {quality_metrics['quality_distribution']['low']}")
        
        return quality_metrics
    
    def check_schema(self, input_path: str) -> bool:
        """Check dataset schema compliance."""
        print(f"📋 Checking schema compliance: {input_path}")
        
        required_fields = ["question", "answer", "context", "university", "type", "tone", "source", "language"]
        schema_valid = True
        issues = []
        
        with open(input_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())
                    
                    # Check required fields
                    for field in required_fields:
                        if field not in data:
                            issues.append(f"Line {line_num}: Missing required field '{field}'")
                            schema_valid = False
                        elif not data[field] or not isinstance(data[field], str):
                            issues.append(f"Line {line_num}: Invalid value for field '{field}'")
                            schema_valid = False
                
                except json.JSONDecodeError as e:
                    issues.append(f"Line {line_num}: JSON parsing error - {e}")
                    schema_valid = False
        
        if schema_valid:
            print("✅ Schema validation passed!")
        else:
            print(f"❌ Schema validation failed with {len(issues)} issues:")
            for issue in issues[:10]:  # Show first 10 issues
                print(f"   • {issue}")
            if len(issues) > 10:
                print(f"   ... and {len(issues) - 10} more issues")
        
        return schema_valid
    
    def analyze_dataset(self, input_path: str) -> Dict[str, Any]:
        """Provide comprehensive dataset analysis."""
        print(f"📈 Analyzing dataset: {input_path}")
        
        analysis = {
            "total_entries": 0,
            "university_distribution": {},
            "question_type_distribution": {},
            "language_distribution": {},
            "tone_distribution": {},
            "average_question_length": 0,
            "average_answer_length": 0,
            "cultural_sensitivity_score": 0,
            "metadata_completeness": 0
        }
        
        total_q_length = 0
        total_a_length = 0
        cultural_count = 0
        
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    analysis["total_entries"] += 1
                    
                    # Distributions
                    univ = data.get("university", "unknown")
                    qtype = data.get("type", "unknown")
                    lang = data.get("language", "unknown")
                    tone = data.get("tone", "unknown")
                    
                    analysis["university_distribution"][univ] = analysis["university_distribution"].get(univ, 0) + 1
                    analysis["question_type_distribution"][qtype] = analysis["question_type_distribution"].get(qtype, 0) + 1
                    analysis["language_distribution"][lang] = analysis["language_distribution"].get(lang, 0) + 1
                    analysis["tone_distribution"][tone] = analysis["tone_distribution"].get(tone, 0) + 1
                    
                    # Length analysis
                    total_q_length += len(data.get("question", ""))
                    total_a_length += len(data.get("answer", ""))
                    
                    # Cultural sensitivity
                    answer = data.get("answer", "")
                    if any(char in answer for char in "এই আরও বিস্তারিত টাকা"):
                        cultural_count += 1
                
                except json.JSONDecodeError:
                    continue
        
        # Calculate averages
        if analysis["total_entries"] > 0:
            analysis["average_question_length"] = total_q_length / analysis["total_entries"]
            analysis["average_answer_length"] = total_a_length / analysis["total_entries"]
            analysis["cultural_sensitivity_score"] = cultural_count / analysis["total_entries"]
        
        # Print analysis
        print(f"\n📊 Dataset Analysis Results:")
        print(f"   • Total entries: {analysis['total_entries']}")
        print(f"   • Avg question length: {analysis['average_question_length']:.0f} chars")
        print(f"   • Avg answer length: {analysis['average_answer_length']:.0f} chars")
        print(f"   • Cultural sensitivity: {analysis['cultural_sensitivity_score']:.1%}")
        
        print(f"\n🏫 University Distribution:")
        for univ, count in sorted(analysis["university_distribution"].items()):
            percentage = (count / analysis["total_entries"]) * 100
            print(f"   • {univ}: {count} ({percentage:.1f}%)")
        
        print(f"\n❓ Question Type Distribution:")
        for qtype, count in sorted(analysis["question_type_distribution"].items()):
            percentage = (count / analysis["total_entries"]) * 100
            print(f"   • {qtype}: {count} ({percentage:.1f}%)")
        
        return analysis

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Enhanced Dataset Generator - Outperform GPT-4 & Gemini 2.5 Pro",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python enhanced_dataset_cli.py generate --size 1000 --output superior_dataset.jsonl
  python enhanced_dataset_cli.py validate --input dataset.jsonl
  python enhanced_dataset_cli.py schema --check dataset.jsonl
  python enhanced_dataset_cli.py analyze --input dataset.jsonl
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate enhanced dataset')
    generate_parser.add_argument('--size', type=int, default=1000, 
                               help='Number of Q&A pairs to generate (default: 1000)')
    generate_parser.add_argument('--output', type=str, 
                               default='output/enhanced_datasets/superior_educational_dataset.jsonl',
                               help='Output file path')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate dataset quality')
    validate_parser.add_argument('--input', type=str, required=True,
                               help='Input dataset file path')
    
    # Schema check command
    schema_parser = subparsers.add_parser('schema', help='Check schema compliance')
    schema_parser.add_argument('--check', type=str, required=True,
                             help='Dataset file to check')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze dataset statistics')
    analyze_parser.add_argument('--input', type=str, required=True,
                              help='Input dataset file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = EnhancedDatasetCLI()
    
    try:
        if args.command == 'generate':
            cli.generate_dataset(args.size, args.output)
        
        elif args.command == 'validate':
            cli.validate_dataset(args.input)
        
        elif args.command == 'schema':
            cli.check_schema(args.check)
        
        elif args.command == 'analyze':
            cli.analyze_dataset(args.input)
    
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
