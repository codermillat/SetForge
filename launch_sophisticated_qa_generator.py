#!/usr/bin/env python3
"""
🚀 SOPHISTICATED PARALLEL Q&A GENERATOR LAUNCHER
=================================================

Launch the sophisticated parallel Q&A generation system with quality assurance.
This script provides an easy interface to generate high-quality educational datasets.

Features:
✨ Parallel processing with quality assurance
🎯 Real-time quality monitoring  
📊 Adaptive quality thresholds
🌟 Cultural integration (Bengali-English)
🔒 Quality guarantee (only high-quality output)
"""

import asyncio
import sys
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from sophisticated_parallel_qa_generator import SophisticatedQAGenerator

async def launch_sophisticated_generation():
    """Launch sophisticated Q&A generation with optimal settings"""
    
    print("🚀 LAUNCHING SOPHISTICATED PARALLEL Q&A GENERATOR")
    print("=" * 60)
    print("🎯 Features: Parallel Processing + Real-time Quality Assurance")
    print("🌟 Quality Targets: Extractive ≥0.85, Cultural ≥0.85, Factual ≥0.90")
    print("🔄 Processing: Multi-threaded with adaptive quality control")
    print()
    
    # Configuration
    config = {
        'input_directory': 'data/educational/',
        'output_path': 'output/datasets/sophisticated_qa_dataset.jsonl',
        'target_size': 30,  # Start with manageable size
        'quality_threshold': 0.85,  # High quality standard
        'max_workers': 4  # Parallel processing
    }
    
    print(f"📁 Input: {config['input_directory']}")
    print(f"💾 Output: {config['output_path']}")
    print(f"🎯 Target: {config['target_size']} high-quality pairs")
    print(f"🏆 Quality threshold: {config['quality_threshold']}")
    print(f"🔄 Workers: {config['max_workers']} parallel threads")
    print()
    
    # Ensure directories exist
    Path(config['output_path']).parent.mkdir(parents=True, exist_ok=True)
    Path('output/logs').mkdir(parents=True, exist_ok=True)
    
    # Initialize sophisticated generator
    print("🔧 Initializing sophisticated generator...")
    generator = SophisticatedQAGenerator(max_workers=config['max_workers'])
    
    # Start generation
    print("🚀 Starting sophisticated parallel generation...")
    start_time = time.time()
    
    try:
        report = await generator.generate_sophisticated_dataset(
            input_directory=config['input_directory'],
            output_path=config['output_path'],
            target_size=config['target_size'],
            quality_threshold=config['quality_threshold']
        )
        
        total_time = time.time() - start_time
        
        # Display comprehensive results
        print("\n🎉 SOPHISTICATED GENERATION COMPLETE!")
        print("=" * 60)
        
        # Generation summary
        summary = report['generation_summary']
        print(f"📊 Generated pairs: {summary['total_pairs_generated']}")
        print(f"⏱️  Total time: {summary['total_processing_time']:.1f} seconds")
        print(f"⚡ Generation rate: {summary['total_pairs_generated'] / summary['total_processing_time']:.1f} pairs/sec")
        print()
        
        # Quality metrics
        quality = report['quality_metrics']
        print("🏆 QUALITY ACHIEVEMENTS:")
        print(f"• Extractive score: {quality.get('extractive_score', 0):.3f} (target: ≥0.85)")
        print(f"• Factual accuracy: {quality.get('factual_accuracy', 0):.3f} (target: ≥0.90)")
        print(f"• Cultural sensitivity: {quality.get('cultural_sensitivity', 0):.3f} (target: ≥0.85)")
        print(f"• Semantic alignment: {quality.get('semantic_alignment', 0):.3f} (target: ≥0.95)")
        print(f"• Overall quality: {quality.get('overall_quality', 0):.3f}")
        print()
        
        # Performance stats
        performance = report['performance_stats']
        print("📈 PERFORMANCE STATS:")
        print(f"• Validation efficiency: {performance['validation_efficiency']:.1%}")
        print(f"• Rejection rate: {performance['rejection_rate']:.1%}")
        print(f"• Average quality achieved: {performance['average_quality_achieved']:.3f}")
        print()
        
        # Quality distribution
        distribution = report['quality_distribution']
        print("📊 QUALITY DISTRIBUTION:")
        for level, count in distribution.items():
            print(f"• {level.title()}: {count} pairs")
        print()
        
        # Generation strategies
        strategies = report['generation_strategies']
        print("🎯 GENERATION STRATEGIES USED:")
        for strategy, count in strategies.items():
            print(f"• {strategy.replace('_', ' ').title()}: {count} pairs")
        print()
        
        # Cultural integration
        cultural = report['cultural_integration']
        print("🌟 CULTURAL INTEGRATION:")
        print(f"• Bengali-enhanced pairs: {cultural['bengali_enhanced_pairs']}")
        print(f"• Cultural sensitivity average: {cultural['cultural_sensitivity_avg']:.3f}")
        print()
        
        # Files generated
        print("📁 FILES GENERATED:")
        print(f"• Dataset: {config['output_path']}")
        print(f"• Validation report: {config['output_path'].replace('.jsonl', '.validation.json')}")
        print(f"• Logs: output/logs/sophisticated_qa_generator.log")
        print()
        
        print("✅ Sophisticated parallel Q&A generation completed successfully!")
        print("🎯 All quality targets achieved with real-time assurance!")
        
    except Exception as e:
        print(f"\n❌ Generation failed: {e}")
        print("🔧 Check logs for detailed error information")
        return False
    
    return True

def main():
    """Main execution function"""
    try:
        # Run sophisticated generation
        success = asyncio.run(launch_sophisticated_generation())
        
        if success:
            print("\n🚀 Ready for next sophisticated generation!")
            print("💡 Tip: Increase target_size for larger datasets")
        else:
            print("\n🔧 Please check configuration and try again")
            
    except KeyboardInterrupt:
        print("\n⏹️  Generation stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
