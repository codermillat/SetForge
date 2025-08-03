#!/usr/bin/env python3
"""
SetForge Enhanced CLI
====================

Production-ready command-line interface with integrated validation, 
monitoring, and quality optimization.
"""

import click
import asyncio
import os
import json
import time
from pathlib import Path
from datetime import datetime
import logging

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Continue without dotenv if not available

# Import generator components
from main_generator import SetForgeGenerator, GenerationConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """SetForge - Production Q&A Dataset Generator for Bangladeshi Educational Content."""
    pass

@cli.command()
@click.argument('data_dir', type=click.Path(exists=True, file_okay=False))
@click.argument('output_path', type=click.Path())
@click.option('--target', '-t', default=50000, help='Target number of Q&A pairs (default: 50,000)')
@click.option('--budget', '-b', default=200.0, help='Budget limit in USD')
@click.option('--config', '-c', default='config.yaml', help='Configuration file')
@click.option('--test-first', is_flag=True, help='Run test batch before full generation')
@click.option('--validate', is_flag=True, help='Run validation before generation')
@click.option('--monitor', is_flag=True, default=True, help='Enable real-time monitoring')
def generate(data_dir, output_path, target, budget, config, test_first, validate, monitor):
    """Generate production-scale Q&A dataset with integrated validation and monitoring."""
    click.echo("="*80)
    click.echo("🎯 SETFORGE - PRODUCTION Q&A GENERATION")
    click.echo("="*80)
    click.echo(f"📁 Data directory: {data_dir}")
    click.echo(f"📝 Output path: {output_path}")
    click.echo(f"🎯 Target pairs: {target:,}")
    click.echo(f"💰 Budget: ${budget}")
    click.echo(f"🧪 Test first: {'Yes' if test_first else 'No'}")
    click.echo(f"🔍 Validate: {'Yes' if validate else 'No'}")
    click.echo("="*80)
    
    # Check API key
    api_key = os.getenv('DIGITALOCEAN_API_KEY')
    if not api_key:
        click.echo("❌ Error: DIGITALOCEAN_API_KEY environment variable not set")
        click.echo("Set it with: export DIGITALOCEAN_API_KEY='your_key'")
        return
    
    # Debug: Show API key format for verification
    click.echo(f"🔑 API Key loaded: {api_key[:15]}...{api_key[-5:]} (length: {len(api_key)})")
    
    # Create configuration
    try:
        # Create config
        if Path(config).exists():
            generator_config = GenerationConfig.from_yaml(config)
            # Override with CLI parameters
            generator_config.target_pairs = target
            generator_config.max_cost_usd = budget
        else:
            generator_config = GenerationConfig(
                api_key=api_key,
                target_pairs=target,
                max_cost_usd=budget
            )
        
        # Run generation with integrated features
        asyncio.run(_run_production_generation(
            generator_config, data_dir, output_path, 
            test_first, validate, monitor
        ))
        
    except Exception as e:
        click.echo(f"❌ Generation failed: {e}")
        logger.error(f"Generation error: {e}")

async def _run_production_generation(config, data_dir, output_path, 
                                   test_first, validate, monitor):
    """Run the complete production generation pipeline."""
    
    async with SetForgeGenerator(config) as generator:
        
        # Step 1: Validation (if requested)
        if validate:
            click.echo("\n🔍 VALIDATION PHASE")
            click.echo("-" * 40)
            validation_results = generator.validate_production_readiness()
            
            if validation_results["overall_status"] != "PRODUCTION_READY":
                click.echo(f"❌ Validation failed: {validation_results['overall_status']}")
                return
            click.echo("✅ Validation passed - System ready for production")
        
        # Step 2: Test batch (if requested)
        if test_first:
            click.echo("\n🧪 TEST BATCH PHASE")
            click.echo("-" * 40)
            test_results = await generator.run_test_batch(batch_size=10)
            
            if not test_results["success"]:
                click.echo("❌ Test batch failed - Check configuration")
                return
            
            click.echo(f"✅ Test batch passed: {test_results['pairs_generated']} pairs, "
                      f"quality {test_results['avg_quality']:.3f}")
        
        # Step 3: Full production generation
        click.echo("\n🚀 PRODUCTION GENERATION PHASE")
        click.echo("-" * 40)
        
        start_time = time.time()
        
        try:
            # Run the main generation (convert strings to Path objects)
            await generator.generate_dataset(Path(data_dir), Path(output_path))
            
            # Success summary
            duration = time.time() - start_time
            click.echo("\n" + "="*80)
            click.echo("🎉 GENERATION COMPLETE!")
            click.echo("="*80)
            click.echo(f"⏱️ Duration: {duration/60:.1f} minutes")
            click.echo(f"📊 Pairs Generated: {len(generator.generated_pairs):,}")
            click.echo(f"💰 Total Cost: ${generator.total_cost:.2f}")
            click.echo(f"📁 Output File: {output_path}")
            click.echo("="*80)
            
        except Exception as e:
            click.echo(f"❌ Production generation failed: {e}")
            logger.error(f"Production error: {e}")

@cli.command()
@click.argument('dataset_path', type=click.Path(exists=True))
@click.option('--threshold', '-t', default=0.6, help='Quality threshold')
@click.option('--sample-size', '-s', default=100, help='Sample size for analysis')
@click.option('--output', '-o', help='Output report file')
def validate(dataset_path, threshold, sample_size, output):
    """Validate dataset quality with enhanced Bangladeshi context checking."""
    click.echo(f"🔍 Validating dataset: {dataset_path}")
    click.echo(f"📊 Quality threshold: {threshold}")
    click.echo(f"📋 Sample size: {sample_size}")
    
    try:
        from quality_checker import QualityChecker
        
        checker = QualityChecker()
        results = checker.analyze_dataset(Path(dataset_path))
        
        # Display results
        click.echo("\n📊 QUALITY ANALYSIS RESULTS")
        click.echo("-" * 40)
        click.echo(f"✅ Total pairs analyzed: {results.get('total_pairs', 0):,}")
        click.echo(f"📈 Average overall quality: {results.get('average_scores', {}).get('overall', 0):.3f}")
        click.echo(f"🎯 Bangladeshi focus: {results.get('content_analysis', {}).get('bangladeshi_percentage', 0):.1f}%")
        click.echo(f"📝 Extractive score: {results.get('average_scores', {}).get('extractive', 0):.3f}")
        click.echo(f"🔍 Cultural authenticity: {results.get('average_scores', {}).get('cultural_authenticity', 0):.3f}")
        click.echo(f"📊 High quality pairs: {results.get('quality_distribution', {}).get('high_percentage', 0):.1f}%")
        
        avg_quality = results.get('average_scores', {}).get('overall', 0)
        if avg_quality >= threshold:
            click.echo("✅ Dataset quality PASSED")
        else:
            click.echo("❌ Dataset quality FAILED")
        
        # Save report if requested
        if output:
            with open(output, 'w') as f:
                json.dump(results, f, indent=2)
            click.echo(f"📄 Report saved: {output}")
            
    except Exception as e:
        click.echo(f"❌ Validation failed: {e}")

@cli.command()
@click.argument('data_dir', type=click.Path(exists=True))
@click.option('--target', '-t', default=50000, help='Target pairs')
@click.option('--budget', '-b', default=200.0, help='Budget in USD')
def estimate(data_dir, target, budget):
    """Estimate cost and time for dataset generation."""
    click.echo("💰 COST & TIME ESTIMATION")
    click.echo("-" * 40)
    
    # Count data files
    txt_files = list(Path(data_dir).glob('*.txt'))
    total_chars = sum(f.stat().st_size for f in txt_files)
    
    # Estimation logic (Updated for DigitalOcean Llama 3.1 8B Instruct)
    tokens_per_pair = 1000  # Average tokens per Q&A pair (context + question + answer)
    cost_per_token = 0.0000002  # DigitalOcean pricing: $0.20 per million tokens (accurate)
    pairs_per_hour = 2000  # Estimated generation rate
    
    estimated_cost = target * tokens_per_pair * cost_per_token
    estimated_hours = target / pairs_per_hour
    
    click.echo(f"📁 Data files: {len(txt_files)}")
    click.echo(f"📊 Total data: {total_chars/1024:.1f} KB")
    click.echo(f"🎯 Target pairs: {target:,}")
    click.echo(f"💰 Estimated cost: ${estimated_cost:.2f}")
    click.echo(f"⏱️ Estimated time: {estimated_hours:.1f} hours")
    click.echo(f"💸 Budget utilization: {(estimated_cost/budget)*100:.1f}%")
    
    if estimated_cost <= budget:
        click.echo("✅ Budget sufficient")
    else:
        click.echo("❌ Budget insufficient")
        max_pairs = int((budget / estimated_cost) * target)
        click.echo(f"📉 Max pairs with budget: {max_pairs:,}")

@cli.command()
def status():
    """Check system status and readiness."""
    click.echo("🔍 SETFORGE SYSTEM STATUS")
    click.echo("-" * 40)
    
    # Check API key
    api_key = os.getenv('DIGITALOCEAN_API_KEY')
    click.echo(f"🔑 API Key: {'✅ Configured' if api_key else '❌ Not set'}")
    
    # Check core files
    core_files = [
        'main_generator.py', 'quality_checker.py', 'utils.py', 'config.yaml'
    ]
    
    for file_path in core_files:
        exists = Path(file_path).exists()
        click.echo(f"📁 {file_path}: {'✅ Found' if exists else '❌ Missing'}")
    
    # Check data directory
    data_dir = Path('data/educational')
    if data_dir.exists():
        txt_files = len(list(data_dir.glob('*.txt')))
        click.echo(f"📚 Data files: ✅ {txt_files} files")
    else:
        click.echo("📚 Data directory: ❌ Missing")
    
    # Check Bangladeshi grading system
    try:
        from utils import BangladeshiGradingSystem
        click.echo("🎓 Bangladeshi grading: ✅ Available")
    except ImportError:
        click.echo("🎓 Bangladeshi grading: ❌ Not available")
    
    # Overall status
    all_ready = all([
        api_key,
        all(Path(f).exists() for f in core_files),
        data_dir.exists()
    ])
    
    click.echo("-" * 40)
    if all_ready:
        click.echo("🚀 Status: READY FOR PRODUCTION")
    else:
        click.echo("⚠️ Status: SETUP REQUIRED")

if __name__ == '__main__':
    cli()
