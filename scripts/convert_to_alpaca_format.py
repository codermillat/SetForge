#!/usr/bin/env python3
"""
Convert SetForge JSONL datasets to Alpaca instruction format for fine-tuning.
Supports Mistral 7B with context-rich educational guidance.
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlpacaFormatConverter:
    """Convert SetForge Q&A datasets to Alpaca instruction format."""
    
    def __init__(self):
        self.converted_count = 0
        self.skipped_count = 0
        self.error_count = 0
        
    def create_instruction_prompt(self, qa_pair: Dict[str, Any]) -> Dict[str, str]:
        """Create Alpaca-format instruction from SetForge Q&A pair."""
        
        # Extract context information
        context = qa_pair.get('context', {})
        grade_analysis = qa_pair.get('grade_analysis', {})
        university_info = qa_pair.get('university_info', {})
        
        # Build context-rich instruction
        instruction_parts = []
        
        # Add context if available
        if context:
            university = context.get('university_full_name', context.get('university', ''))
            program = context.get('program', '')
            timeline = context.get('timeline', '')
            
            if university:
                instruction_parts.append(f"University: {university}")
            if program:
                instruction_parts.append(f"Program: {program}")
            if timeline:
                instruction_parts.append(f"Academic Year: {timeline}")
                
        # Add grade information if available
        if grade_analysis and grade_analysis.get('ssc_info') or grade_analysis.get('hsc_info'):
            instruction_parts.append("Student Academic Background: Bangladeshi student with provided grades")
            
        # Create the base instruction
        base_instruction = "You are an expert educational counselor specializing in helping Bangladeshi students with Indian university admissions. Provide accurate, detailed guidance based on official university policies."
        
        # Combine context with question
        if instruction_parts:
            context_str = " | ".join(instruction_parts)
            instruction = f"{base_instruction}\n\nContext: {context_str}\n\nQuestion: {qa_pair['question']}"
        else:
            instruction = f"{base_instruction}\n\nQuestion: {qa_pair['question']}"
            
        # Clean and format the answer
        answer = qa_pair['answer'].strip()
        
        # Create input field (can be empty for instruction-following format)
        input_text = ""
        
        return {
            "instruction": instruction,
            "input": input_text,
            "output": answer
        }
    
    def should_include_qa_pair(self, qa_pair: Dict[str, Any]) -> bool:
        """Determine if Q&A pair should be included in training set."""
        
        # Check for required fields
        if not qa_pair.get('question') or not qa_pair.get('answer'):
            return False
            
        # Check validation score if available
        validation = qa_pair.get('validation', {})
        if validation.get('overall_score', 0) < 0.7:  # Quality threshold
            return False
            
        # Check answer length (avoid too short answers)
        if len(qa_pair['answer']) < 50:
            return False
            
        return True
    
    def convert_dataset(self, input_file: str, output_file: str, 
                       quality_threshold: float = 0.7, max_samples: Optional[int] = None) -> Dict[str, int]:
        """Convert SetForge dataset to Alpaca format."""
        
        input_path = Path(input_file)
        output_path = Path(output_file)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
            
        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Converting {input_file} to Alpaca format...")
        logger.info(f"Quality threshold: {quality_threshold}")
        logger.info(f"Max samples: {max_samples or 'unlimited'}")
        
        alpaca_data = []
        
        with open(input_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    line = line.strip()
                    if not line:
                        continue
                        
                    qa_pair = json.loads(line)
                    
                    # Skip metadata entries
                    if qa_pair.get('__type') in ['metadata', 'final_metadata']:
                        continue
                        
                    # Quality filtering
                    if not self.should_include_qa_pair(qa_pair):
                        self.skipped_count += 1
                        continue
                        
                    # Additional quality check
                    validation = qa_pair.get('validation', {})
                    if validation.get('overall_score', 1.0) < quality_threshold:
                        self.skipped_count += 1
                        continue
                        
                    # Convert to Alpaca format
                    alpaca_entry = self.create_instruction_prompt(qa_pair)
                    alpaca_data.append(alpaca_entry)
                    self.converted_count += 1
                    
                    # Check max samples limit
                    if max_samples and self.converted_count >= max_samples:
                        logger.info(f"Reached maximum samples limit: {max_samples}")
                        break
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON decode error on line {line_num}: {e}")
                    self.error_count += 1
                    continue
                except Exception as e:
                    logger.warning(f"Error processing line {line_num}: {e}")
                    self.error_count += 1
                    continue
                    
        # Write Alpaca format dataset
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(alpaca_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Conversion complete!")
        logger.info(f"  Input file: {input_file}")
        logger.info(f"  Output file: {output_file}")
        logger.info(f"  Converted: {self.converted_count}")
        logger.info(f"  Skipped: {self.skipped_count}")
        logger.info(f"  Errors: {self.error_count}")
        
        return {
            'converted': self.converted_count,
            'skipped': self.skipped_count,
            'errors': self.error_count,
            'total_processed': self.converted_count + self.skipped_count + self.error_count
        }

def main():
    parser = argparse.ArgumentParser(
        description='Convert SetForge Q&A dataset to Alpaca instruction format',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        'input_file',
        help='Path to SetForge JSONL dataset file'
    )
    
    parser.add_argument(
        'output_file',
        help='Path for output Alpaca format JSON file'
    )
    
    parser.add_argument(
        '--quality-threshold', '-q',
        type=float,
        default=0.7,
        help='Minimum quality score for inclusion'
    )
    
    parser.add_argument(
        '--max-samples', '-m',
        type=int,
        help='Maximum number of samples to convert'
    )
    
    parser.add_argument(
        '--example-output', '-e',
        action='store_true',
        help='Show example of converted format'
    )
    
    args = parser.parse_args()
    
    # Example output
    if args.example_output:
        print("\n📝 Example Alpaca Format Output:")
        print("-" * 50)
        example = {
            "instruction": "You are an expert educational counselor specializing in helping Bangladeshi students with Indian university admissions. Provide accurate, detailed guidance based on official university policies.\n\nContext: Sharda University | B.Tech CSE | Academic Year: 2025-26\n\nQuestion: What is the annual tuition fee for B.Tech CSE at Sharda University for Bangladeshi students in 2025-26?",
            "input": "",
            "output": "**💰 Sharda University FEE BREAKDOWN for B.Tech CSE (2025-26)**\n\n**📅 YEAR-WISE TUITION FEES:**\n• 1st Year: **₹280,000** (no scholarship)\n• 2nd Year: **₹288,400** (no scholarship)\n• 3rd Year: **₹297,052** (no scholarship)\n• 4th Year: **₹305,964** (no scholarship)\n\n**📊 FINANCIAL SUMMARY:**\n• Original 4-Year Tuition: ₹1,171,416\n• **Your Payable Tuition: ₹1,171,416**\n• **In BDT: ~1,464,270 BDT (~14.6 lakh BDT)**"
        }
        print(json.dumps(example, indent=2, ensure_ascii=False))
        print("-" * 50)
        return
        
    # Convert dataset
    converter = AlpacaFormatConverter()
    try:
        results = converter.convert_dataset(
            args.input_file, 
            args.output_file,
            args.quality_threshold,
            args.max_samples
        )
        
        print(f"\n✅ Successfully converted dataset!")
        print(f"   📁 Output: {args.output_file}")
        print(f"   📊 Statistics: {results['converted']} converted, {results['skipped']} skipped, {results['errors']} errors")
        
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
