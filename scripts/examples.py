#!/usr/bin/env python3
"""
Example usage script for SetForge

Demonstrates various ways to use SetForge for different scenarios.
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from setforge import SetForge


async def example_basic_usage():
    """Basic usage example."""
    print("=== Basic Usage Example ===")
    
    # Create a temporary directory for this example
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample input file
        sample_file = temp_path / "sample_content.txt"
        sample_content = """# University Information

## Academic Programs

Sharda University offers comprehensive B.Tech programs in Computer Science Engineering.
The programs include specializations in Artificial Intelligence, Machine Learning, and Data Science.

### Admission Requirements

Students must have completed 12th grade with minimum 60% marks in PCM subjects.
The admission process includes entrance exams and counseling sessions.

## Fee Structure

The annual tuition fee for B.Tech programs is $5,000 USD for international students.
Additional charges include hostel fees of $1,200 per year and meal plans at $800 annually.
"""
        
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        
        # Set up configuration for dry run
        config = Config()
        config.dry_run = True  # Don't make actual API calls
        config.qa.questions_per_chunk = 2
        config.log_level = "INFO"
        
        # Initialize SetForge
        setforge = SetForge()
        setforge.config = config
        
        # Process the sample file
        output_file = temp_path / "output.jsonl"
        
        try:
            stats = await setforge.process_directory(str(temp_path), str(output_file))
            
            print(f"✅ Processing completed!")
            print(f"Files processed: {stats['files_processed']}")
            print(f"QA pairs generated: {stats['qa_pairs_generated']}")
            print(f"QA pairs validated: {stats['qa_pairs_validated']}")
            
            # Show sample output
            if output_file.exists():
                print("\n--- Sample Output ---")
                with open(output_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:3]  # Show first 3 lines
                    for line in lines:
                        print(line.strip())
                        
        except Exception as e:
            print(f"❌ Error: {e}")


async def example_custom_config():
    """Example with custom configuration."""
    print("\n=== Custom Configuration Example ===")
    
    # Create custom configuration
    config = Config()
    
    # Customize for high-quality educational content
    config.qa.questions_per_chunk = 4
    config.qa.question_types = ["factual", "definition", "process"]
    config.validation.min_relevancy_score = 0.9
    config.validation.min_source_overlap = 0.8
    config.chunking.max_chunk_size = 1500
    config.dry_run = True
    
    print("Custom configuration created:")
    print(f"- Questions per chunk: {config.qa.questions_per_chunk}")
    print(f"- Question types: {config.qa.question_types}")
    print(f"- Min relevancy score: {config.validation.min_relevancy_score}")
    print(f"- Max chunk size: {config.chunking.max_chunk_size}")


async def example_cost_estimation():
    """Example of cost estimation."""
    print("\n=== Cost Estimation Example ===")
    
    # Get current directory file count and sizes
    current_dir = Path(".")
    txt_files = list(current_dir.glob("*.txt"))
    
    if txt_files:
        total_size = sum(f.stat().st_size for f in txt_files)
        file_count = len(txt_files)
        avg_size_kb = (total_size / file_count) / 1024
        
        config = Config()
        
        # Estimate tokens and cost
        avg_chars = avg_size_kb * 1024
        chunks_per_file = max(1, avg_chars / config.chunking.max_chunk_size)
        total_chunks = file_count * chunks_per_file
        
        tokens_per_chunk = avg_chars / 4  # Rough estimate
        total_tokens = total_chunks * (tokens_per_chunk + 500 + config.llm.max_tokens)
        estimated_cost = (total_tokens / 1000) * config.cost.cost_per_1k_tokens
        
        print(f"Found {file_count} .txt files")
        print(f"Average file size: {avg_size_kb:.1f} KB")
        print(f"Estimated chunks: {total_chunks:.0f}")
        print(f"Estimated cost: ${estimated_cost:.4f}")
        print(f"Budget limit: ${config.cost.max_total_cost_usd}")
        
        if estimated_cost <= config.cost.max_total_cost_usd:
            print("✅ Within budget!")
        else:
            print("⚠️  May exceed budget - consider adjustments")
    else:
        print("No .txt files found in current directory")


async def example_validation_demo():
    """Example of validation features."""
    print("\n=== Validation Demo ===")
    
    from src.qa_generator import QAPair
    from src.validator import QAValidator
    
    config = Config()
    validator = QAValidator(config)
    
    # Create sample QA pairs to validate
    good_qa = QAPair(
        question="What is the annual tuition fee for B.Tech programs?",
        answer="The annual tuition fee for B.Tech programs is $5,000 USD for international students",
        chunk_id="test_1",
        source_text="The annual tuition fee for B.Tech programs is $5,000 USD for international students. Additional charges include hostel fees.",
        question_type="factual"
    )
    
    bad_qa = QAPair(
        question="What might be the future prospects?",
        answer="Students will probably have good career opportunities in the technology sector",
        chunk_id="test_2", 
        source_text="Sharda University offers B.Tech programs in Computer Science.",
        question_type="factual"
    )
    
    # Validate both examples
    print("Validating good QA pair (extractive)...")
    good_result = await validator.validate_qa_pair(good_qa)
    print(f"  Valid: {good_result.is_valid}")
    print(f"  Extractive score: {good_result.extractive_score:.3f}")
    print(f"  Hallucination score: {good_result.hallucination_score:.3f}")
    
    print("\nValidating bad QA pair (has inference)...")
    bad_result = await validator.validate_qa_pair(bad_qa)
    print(f"  Valid: {bad_result.is_valid}")
    print(f"  Extractive score: {bad_result.extractive_score:.3f}")
    print(f"  Hallucination score: {bad_result.hallucination_score:.3f}")
    print(f"  Issues: {bad_result.issues}")


async def main():
    """Run all examples."""
    print("SetForge Examples")
    print("=" * 50)
    
    await example_basic_usage()
    await example_custom_config()
    await example_cost_estimation()
    await example_validation_demo()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nTo run SetForge on your files:")
    print("  python setforge.py input_directory/ output.jsonl")
    print("\nTo create a custom config:")
    print("  python setforge_cli.py create-config my_config.yaml")


if __name__ == "__main__":
    asyncio.run(main())
