#!/usr/bin/env python3
"""
Debug script to see actual QA pairs and validation details
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import Config
from src.text_processor import TextProcessor
from src.qa_generator import QAGenerator
from src.validator import QAValidator

async def debug_qa_generation():
    os.environ.setdefault('DIGITALOCEAN_API_KEY', os.environ.get('DIGITALOCEAN_API_KEY', ''))
    
    config = Config()
    config.llm.api_key = os.environ.get('DIGITALOCEAN_API_KEY', '')
    
    text_processor = TextProcessor(config)
    qa_generator = QAGenerator(config)
    validator = QAValidator(config)
    
    # Process the test file
    file_path = Path("test_dir/glossary_of_terms.txt")
    chunks = await text_processor.process_file(file_path)
    
    print(f"=== DEBUGGING QA GENERATION ===")
    print(f"File: {file_path}")
    print(f"Chunks created: {len(chunks)}")
    
    for i, chunk in enumerate(chunks):
        print(f"\n--- CHUNK {i+1} ---")
        print(f"Content length: {len(chunk.content)}")
        print(f"Content preview: {chunk.content[:200]}...")
        
        # Generate QA pairs
        qa_pairs = await qa_generator.generate_qa_pairs(chunk)
        print(f"\nGenerated QA pairs: {len(qa_pairs)}")
        
        for j, qa_pair in enumerate(qa_pairs):
            print(f"\n  QA PAIR {j+1}:")
            print(f"  Question: {qa_pair.question}")
            print(f"  Answer: {qa_pair.answer}")
            print(f"  Type: {qa_pair.question_type}")
            
            # Validate
            validation_result = await validator.validate_qa_pair(qa_pair)
            print(f"  VALIDATION:")
            print(f"    Valid: {validation_result.is_valid}")
            print(f"    Overall Score: {validation_result.overall_score:.3f}")
            print(f"    Extractive Score: {validation_result.extractive_score:.3f}")
            print(f"    Hallucination Score: {validation_result.hallucination_score:.3f}")
            print(f"    Relevancy Score: {validation_result.relevancy_score:.3f}")
            print(f"    Issues: {validation_result.issues}")
            
            # Show detailed validation
            details = validation_result.validation_details
            if 'extractive' in details:
                ext_details = details['extractive']
                print(f"    Extractive Details:")
                print(f"      Word overlap: {ext_details.get('word_overlap', 'N/A')}")
                print(f"      Exact matches: {ext_details.get('exact_matches', 'N/A')}")
    
    await qa_generator.close()

if __name__ == "__main__":
    asyncio.run(debug_qa_generation())
