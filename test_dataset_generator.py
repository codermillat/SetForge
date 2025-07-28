#!/usr/bin/env python3
"""
Production TXT Dataset Generator CLI
===================================

Simple CLI interface for testing the production dataset generator.
Processes .txt files into Q&A datasets with rich metadata.

Usage:
    python test_dataset_generator.py [--input data/educational] [--output test_output.jsonl] [--sample 5]
"""

import asyncio
import argparse
import sys
from pathlib import Path
import json
from typing import List

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from production_txt_dataset_generator import ProductionTxtDatasetGenerator
from config import Config


async def test_dataset_generation(
    input_dir: str = "data/educational",
    output_file: str = "test_output.jsonl", 
    sample_files: int = 5,
    dry_run: bool = False
):
    """Test the production dataset generator."""
    
    print("🔧 Production TXT Dataset Generator Test")
    print("="*50)
    
    # Initialize generator
    config = Config()
    generator = ProductionTxtDatasetGenerator(config)
    
    # Find .txt files
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return False
    
    txt_files = list(input_path.glob("*.txt"))
    if not txt_files:
        print(f"❌ No .txt files found in: {input_dir}")
        return False
    
    print(f"📁 Found {len(txt_files)} .txt files")
    
    # Sample files if requested
    if sample_files and sample_files < len(txt_files):
        txt_files = txt_files[:sample_files]
        print(f"🎯 Processing sample of {sample_files} files")
    
    # Process files
    output_path = Path(output_file)
    total_pairs = 0
    
    try:
        print("\n📝 Processing files...")
        
        for i, txt_file in enumerate(txt_files, 1):
            print(f"\n[{i}/{len(txt_files)}] Processing: {txt_file.name}")
            
            if dry_run:
                print("   🔍 DRY RUN - Reading file content...")
                content = txt_file.read_text(encoding='utf-8')
                print(f"   📄 File length: {len(content)} characters")
                
                # Extract paragraphs
                paragraphs = generator._extract_paragraphs(content)
                print(f"   📋 Extracted {len(paragraphs)} paragraphs")
                
                # Estimate Q&A pairs
                estimated_pairs = len(paragraphs) * 2  # Rough estimate
                print(f"   🎯 Estimated Q&A pairs: {estimated_pairs}")
                total_pairs += estimated_pairs
                
            else:
                # Actually generate Q&A pairs
                qa_pairs = await generator.process_file(str(txt_file))
                print(f"   ✅ Generated {len(qa_pairs)} Q&A pairs")
                total_pairs += len(qa_pairs)
                
                # Append to output file
                with open(output_path, 'a', encoding='utf-8') as f:
                    for pair in qa_pairs:
                        f.write(json.dumps(pair, ensure_ascii=False) + '\n')
        
        if dry_run:
            print(f"\n🎯 DRY RUN SUMMARY:")
            print(f"   📊 Total estimated Q&A pairs: {total_pairs}")
            print(f"   💾 Would save to: {output_path}")
        else:
            print(f"\n✅ GENERATION COMPLETE:")
            print(f"   📊 Total Q&A pairs: {total_pairs}")
            print(f"   💾 Saved to: {output_path}")
            
            # Quick validation
            if output_path.exists():
                lines = output_path.read_text(encoding='utf-8').strip().split('\n')
                print(f"   📋 Output file has {len(lines)} lines")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return False


def validate_output(output_file: str):
    """Quick validation of generated output."""
    
    output_path = Path(output_file)
    if not output_path.exists():
        print(f"❌ Output file not found: {output_file}")
        return
    
    print(f"\n🔍 Validating output: {output_file}")
    
    try:
        entries = []
        with open(output_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    entry = json.loads(line)
                    entries.append(entry)
                except json.JSONDecodeError as e:
                    print(f"   ⚠️  Line {line_num}: Invalid JSON - {e}")
        
        print(f"   📊 Valid entries: {len(entries)}")
        
        if entries:
            # Sample entry
            sample = entries[0]
            print(f"   🔍 Sample entry fields: {list(sample.keys())}")
            
            # Check required fields
            required = {"question", "answer", "context", "university", "confidence_level"}
            missing_fields = []
            
            for entry in entries[:5]:  # Check first 5
                missing = required - set(entry.keys())
                if missing:
                    missing_fields.extend(missing)
            
            if missing_fields:
                unique_missing = set(missing_fields)
                print(f"   ⚠️  Some entries missing fields: {unique_missing}")
            else:
                print(f"   ✅ All sampled entries have required fields")
        
    except Exception as e:
        print(f"   ❌ Validation error: {e}")


async def main():
    """CLI interface."""
    
    parser = argparse.ArgumentParser(description="Test production TXT dataset generator")
    parser.add_argument("--input", "-i", default="data/educational", 
                       help="Input directory with .txt files")
    parser.add_argument("--output", "-o", default="test_output.jsonl",
                       help="Output JSONL file")
    parser.add_argument("--sample", "-s", type=int, default=5,
                       help="Number of files to process (0 for all)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Dry run - analyze files without generating Q&A")
    parser.add_argument("--validate", action="store_true", 
                       help="Validate existing output file")
    
    args = parser.parse_args()
    
    # Validate existing output
    if args.validate:
        validate_output(args.output)
        return
    
    # Test generation
    success = await test_dataset_generation(
        input_dir=args.input,
        output_file=args.output,
        sample_files=args.sample if args.sample > 0 else None,
        dry_run=args.dry_run
    )
    
    if success and not args.dry_run:
        print(f"\n🔍 Quick validation:")
        validate_output(args.output)
    
    print(f"\n{'✅ Test completed successfully' if success else '❌ Test failed'}")


if __name__ == "__main__":
    asyncio.run(main())
