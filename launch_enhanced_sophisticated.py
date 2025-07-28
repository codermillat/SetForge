#!/usr/bin/env python3
"""
🚀 ENHANCED SOPHISTICATED Q&A GENERATOR LAUNCHER
============================================

Simple launcher for the enhanced sophisticated Q&A generation system.
This version is designed to work reliably and generate high-quality datasets.

Features:
✅ Robust error handling
✅ Realistic quality thresholds
✅ Parallel processing with 4 workers
✅ Cultural integration for Bangladeshi students
✅ Multiple generation strategies
✅ Comprehensive quality validation
"""

import asyncio
import logging
import time
from pathlib import Path

# Configure logging for clean output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def launch_enhanced_sophisticated_generator():
    """Launch the enhanced sophisticated Q&A generator"""
    
    print("🚀 ENHANCED SOPHISTICATED Q&A GENERATOR")
    print("=" * 50)
    print("🎯 Target: High-quality Q&A dataset with parallel processing")
    print("🌍 Audience: Bangladeshi students seeking university guidance")
    print("⚡ Features: Real-time quality validation & cultural integration")
    print()
    
    # Configuration
    config = {
        'input_directory': 'data/educational',
        'output_path': 'output/enhanced_sophisticated_dataset.jsonl',
        'target_size': 30,                  # Achievable target
        'quality_threshold': 0.75,          # Realistic threshold
        'max_workers': 4                    # Optimal parallel workers
    }
    
    # Display configuration
    print("📋 CONFIGURATION:")
    for key, value in config.items():
        print(f"   {key}: {value}")
    print()
    
    # Import the generator (after configuration display)
    try:
        from enhanced_sophisticated_qa_generator import EnhancedSophisticatedQAGenerator
        logger.info("✅ Successfully imported enhanced generator")
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return
    
    # Initialize generator
    try:
        generator = EnhancedSophisticatedQAGenerator(max_workers=config['max_workers'])
        logger.info("✅ Enhanced generator initialized")
    except Exception as e:
        logger.error(f"❌ Generator initialization error: {e}")
        return
    
    # Verify input directory
    input_path = Path(config['input_directory'])
    if not input_path.exists():
        logger.error(f"❌ Input directory not found: {input_path}")
        return
    
    txt_files = list(input_path.glob("*.txt"))
    if not txt_files:
        logger.error(f"❌ No .txt files found in {input_path}")
        return
    
    logger.info(f"📖 Found {len(txt_files)} source files")
    
    # Ensure output directory exists
    output_path = Path(config['output_path'])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"📁 Output directory ready: {output_path.parent}")
    
    print()
    print("🚀 STARTING ENHANCED GENERATION...")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Run the enhanced generation
        report = await generator.generate_enhanced_dataset(
            input_directory=config['input_directory'],
            output_path=config['output_path'],
            target_size=config['target_size'],
            quality_threshold=config['quality_threshold']
        )
        
        # Display results
        total_time = time.time() - start_time
        
        print()
        print("🎉 GENERATION COMPLETE!")
        print("=" * 50)
        print(f"📊 Generated pairs: {report['generation_summary']['total_pairs_generated']}")
        print(f"⏱️  Total time: {total_time:.1f} seconds")
        print(f"🚀 Generation rate: {report['performance_stats']['generation_rate']:.2f} pairs/second")
        print(f"🏆 Average quality: {report['performance_stats']['average_quality_achieved']:.3f}")
        print()
        
        # Quality breakdown
        print("📈 QUALITY BREAKDOWN:")
        for level, count in report['quality_distribution'].items():
            print(f"   {level}: {count} pairs")
        print()
        
        # Quality metrics
        print("🎯 AVERAGE QUALITY METRICS:")
        for metric, score in report['quality_metrics'].items():
            if isinstance(score, (int, float)):
                print(f"   {metric}: {score:.3f}")
        
        print()
        print(f"💾 Dataset saved: {config['output_path']}")
        print(f"📋 Validation report: {config['output_path']}.validation.json")
        
        # Success summary
        if report['generation_summary']['total_pairs_generated'] >= config['target_size'] * 0.8:
            print("✅ Generation SUCCESSFUL - Target achieved!")
        else:
            print("⚠️  Generation PARTIAL - Some pairs generated")
        
        return report
        
    except Exception as e:
        logger.error(f"❌ Generation error: {e}")
        print(f"\n❌ ERROR: {e}")
        return None

def main():
    """Main execution function"""
    print("🌟 Enhanced Sophisticated Q&A Generator Launcher")
    print("📅 Created: January 2025")
    print("👥 For: Bangladeshi students seeking university guidance")
    print()
    
    # Run the async generator
    try:
        result = asyncio.run(launch_enhanced_sophisticated_generator())
        
        if result:
            print("\n🎊 SUCCESS: Enhanced dataset generation completed!")
        else:
            print("\n💡 TIP: Check logs above for detailed error information")
            
    except KeyboardInterrupt:
        print("\n⏹️  Generation stopped by user")
    except Exception as e:
        print(f"\n❌ Launcher error: {e}")

if __name__ == "__main__":
    main()
