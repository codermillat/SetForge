#!/usr/bin/env python3
"""
Production-grade SetForge CLI with comprehensive features.
"""

import asyncio
import argparse
import sys
import json
import time
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.setforge_production import ProductionSetForge, health_check
from src.config import Config


def setup_argument_parser():
    """Setup comprehensive argument parser."""
    parser = argparse.ArgumentParser(
        description="SetForge: Production-grade extractive QA dataset generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic processing
  python setforge_cli.py process input_dir/ output.jsonl

  # With custom config
  python setforge_cli.py process input_dir/ output.jsonl --config my_config.yaml

  # Cost estimation
  python setforge_cli.py estimate input_dir/ --config my_config.yaml

  # Health check
  python setforge_cli.py health-check

  # Create sample config
  python setforge_cli.py create-config sample_config.yaml

  # Monitor running process
  python setforge_cli.py status --config my_config.yaml
        """
    )

    # Global options
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to configuration file (YAML)'
    )
    
    parser.add_argument(
        '--log-level', '-l',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform dry run without making API calls'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Process command
    process_parser = subparsers.add_parser(
        'process',
        help='Process input files and generate QA dataset'
    )
    process_parser.add_argument(
        'input_path',
        type=str,
        help='Input file or directory path'
    )
    process_parser.add_argument(
        'output_path',
        type=str,
        help='Output JSONL file path'
    )
    process_parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from previous run (if supported)'
    )
    process_parser.add_argument(
        '--max-files',
        type=int,
        help='Maximum number of files to process'
    )

    # Estimate command
    estimate_parser = subparsers.add_parser(
        'estimate',
        help='Estimate processing cost and time'
    )
    estimate_parser.add_argument(
        'input_path',
        type=str,
        help='Input file or directory path'
    )

    # Health check command
    health_parser = subparsers.add_parser(
        'health-check',
        help='Check system health and API connectivity'
    )

    # Config creation command
    config_parser = subparsers.add_parser(
        'create-config',
        help='Create sample configuration file'
    )
    config_parser.add_argument(
        'config_path',
        type=str,
        help='Path for new configuration file'
    )
    config_parser.add_argument(
        '--environment',
        choices=['development', 'staging', 'production'],
        default='development',
        help='Environment preset'
    )

    # Status command
    status_parser = subparsers.add_parser(
        'status',
        help='Get current processing status'
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate configuration file'
    )
    validate_parser.add_argument(
        '--config-path',
        type=str,
        help='Configuration file to validate'
    )

    return parser


def print_header():
    """Print application header."""
    print("="*70)
    print("SetForge - Production QA Dataset Generator")
    print("Version 2.0 | Production-Ready")
    print("="*70)


def print_summary(results: dict):
    """Print processing summary."""
    print("\n" + "="*50)
    print("PROCESSING SUMMARY")
    print("="*50)
    
    if results.get('success', False):
        print(f"✓ Status: SUCCESS")
        print(f"✓ Files processed: {results.get('processed_files', 0)}/{results.get('total_files', 0)}")
        print(f"✓ QA pairs generated: {results.get('export_statistics', {}).get('total_exported', 0)}")
        print(f"✓ Total cost: ${results.get('cost_breakdown', {}).get('total_cost', 0.0):.4f}")
        print(f"✓ Processing time: {results.get('processing_time_seconds', 0):.1f}s")
        
        # Validation statistics
        val_stats = results.get('validation_statistics', {})
        if val_stats:
            pass_rate = val_stats.get('pass_rate', 0) * 100
            print(f"✓ Validation pass rate: {pass_rate:.1f}%")
        
        # Performance metrics
        perf_metrics = results.get('performance_metrics', {})
        if perf_metrics:
            print(f"✓ Average processing time per file: {perf_metrics.get('avg_processing_time_per_file', 0):.1f}s")
        
    else:
        print(f"✗ Status: FAILED")
        print(f"✗ Error: {results.get('error', 'Unknown error')}")
        
        if 'failed_files' in results:
            print(f"✗ Failed files: {results['failed_files']}")
    
    print("="*50)


async def cmd_process(args):
    """Handle process command."""
    print(f"\nProcessing: {args.input_path} → {args.output_path}")
    
    if args.dry_run:
        print("DRY RUN MODE - No API calls will be made")
    
    try:
        # Initialize SetForge
        setforge = ProductionSetForge(args.config)
        
        # Apply command line overrides
        if args.dry_run:
            setforge.config.cost.dry_run = True
        
        if args.max_files:
            # This would need to be implemented in the processor
            print(f"Note: max_files={args.max_files} (feature needs implementation)")
        
        # Process files
        print("\nStarting processing...")
        results = await setforge.process_directory(args.input_path, args.output_path)
        
        # Print results
        print_summary(results)
        
        return 0 if results.get('success', False) else 1
        
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user")
        return 130
    except Exception as e:
        print(f"\nProcessing failed: {e}")
        return 1


async def cmd_estimate(args):
    """Handle estimate command."""
    print(f"\nEstimating cost for: {args.input_path}")
    
    try:
        setforge = ProductionSetForge(args.config)
        estimate = await setforge.estimate_cost(args.input_path)
        
        if 'error' in estimate:
            print(f"Estimation failed: {estimate['error']}")
            return 1
        
        print("\n" + "="*40)
        print("COST ESTIMATION")
        print("="*40)
        print(f"Files to process: {estimate['files_count']}")
        print(f"Total size: {estimate['total_size_bytes']:,} bytes")
        print(f"Estimated chunks: {estimate['estimated_chunks']:,}")
        print(f"Estimated tokens: {estimate['estimated_tokens']:,}")
        print(f"Estimated cost: ${estimate['estimated_cost_usd']:.4f}")
        print(f"Estimated duration: {estimate['estimated_duration_minutes']:.0f} minutes")
        print(f"Budget utilization: {estimate['budget_utilization']:.1f}%")
        
        if estimate['budget_utilization'] > 100:
            print("\n⚠️  WARNING: Estimated cost exceeds budget!")
        elif estimate['budget_utilization'] > 80:
            print("\n⚠️  WARNING: Estimated cost is close to budget limit")
        else:
            print("\n✓ Estimated cost within budget")
        
        print("="*40)
        
        return 0
        
    except Exception as e:
        print(f"Estimation failed: {e}")
        return 1


async def cmd_health_check(args):
    """Handle health check command."""
    print("\nPerforming health check...")
    
    try:
        health_result = await health_check(args.config)
        
        print("\n" + "="*30)
        print("HEALTH CHECK RESULTS")
        print("="*30)
        print(f"Status: {health_result['status'].upper()}")
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(health_result['timestamp']))}")
        print(f"Version: {health_result.get('version', 'unknown')}")
        print(f"Environment: {health_result.get('environment', 'unknown')}")
        
        api_status = health_result.get('api_status', {})
        if api_status:
            print(f"API Status: {'✓ Healthy' if api_status.get('healthy', False) else '✗ Unhealthy'}")
            if 'response_time_ms' in api_status:
                print(f"API Response Time: {api_status['response_time_ms']:.0f}ms")
        
        if 'error' in health_result:
            print(f"Error: {health_result['error']}")
        
        print("="*30)
        
        return 0 if health_result['status'] == 'healthy' else 1
        
    except Exception as e:
        print(f"Health check failed: {e}")
        return 1


def cmd_create_config(args):
    """Handle config creation command."""
    print(f"\nCreating configuration file: {args.config_path}")
    
    try:
        # Create sample configuration based on environment
        config_content = create_sample_config(args.environment)
        
        # Write to file
        with open(args.config_path, 'w') as f:
            f.write(config_content)
        
        print(f"✓ Configuration file created: {args.config_path}")
        print(f"✓ Environment preset: {args.environment}")
        print("\nNext steps:")
        print("1. Edit the configuration file to match your requirements")
        print("2. Set your DIGITALOCEAN_API_KEY environment variable")
        print("3. Run: python setforge_cli.py validate --config-path your_config.yaml")
        
        return 0
        
    except Exception as e:
        print(f"Failed to create config: {e}")
        return 1


def create_sample_config(environment: str) -> str:
    """Create sample configuration content."""
    if environment == 'production':
        return '''# SetForge Production Configuration
environment: production

# LLM Configuration
llm:
  api_url: "https://inference.do-ai.run/v1/chat/completions"
  model: "llama3-8b-instruct"
  # Set DIGITALOCEAN_API_KEY environment variable
  api_key: "${DIGITALOCEAN_API_KEY}"
  max_retries: 5
  retry_delay: 2.0
  request_timeout: 60

# Text Processing
chunking:
  max_chunk_size: 1000
  min_chunk_size: 200
  overlap_size: 100
  chunk_by_sections: true
  optimize_chunks: true

# QA Generation
qa:
  max_questions_per_chunk: 3
  min_question_length: 10
  max_question_length: 200
  forbidden_patterns:
    - "probably"
    - "might be"
    - "in my opinion"

# Validation (Production settings)
validation:
  min_overall_score: 0.75
  min_source_overlap: 0.65
  min_relevancy_score: 0.75
  enable_semantic: true
  semantic_model: "all-MiniLM-L6-v2"

# Cost Management
cost:
  max_total_cost_usd: 10.0
  cost_per_token: 0.000001
  cost_alert_threshold: 0.8
  batch_size: 5

# Output
output:
  base_path: "output/datasets/output.jsonl"
  separate_by_quality: true
  enable_audit_log: true
  dataset_name: "Production QA Dataset"

# Monitoring
monitoring:
  enable_metrics: true
  log_structured: true
  metrics_interval_seconds: 300
  performance_threshold_seconds: 60
'''

    elif environment == 'staging':
        return '''# SetForge Staging Configuration
environment: staging

# LLM Configuration
llm:
  api_url: "https://inference.do-ai.run/v1/chat/completions"
  model: "llama3-8b-instruct"
  api_key: "${DIGITALOCEAN_API_KEY}"
  max_retries: 3
  retry_delay: 1.0
  request_timeout: 30

# Text Processing
chunking:
  max_chunk_size: 800
  min_chunk_size: 150
  overlap_size: 80
  chunk_by_sections: true
  optimize_chunks: true

# QA Generation
qa:
  max_questions_per_chunk: 2
  min_question_length: 8
  max_question_length: 150

# Validation (Relaxed for testing)
validation:
  min_overall_score: 0.70
  min_source_overlap: 0.60
  min_relevancy_score: 0.70
  enable_semantic: true

# Cost Management
cost:
  max_total_cost_usd: 5.0
  cost_per_token: 0.000001
  batch_size: 3

# Output
output:
  base_path: "output/datasets/staging_output.jsonl"
  separate_by_quality: false
  enable_audit_log: true

# Monitoring
monitoring:
  enable_metrics: true
  log_structured: false
  metrics_interval_seconds: 120
'''

    else:  # development
        return '''# SetForge Development Configuration
environment: development

# LLM Configuration
llm:
  api_url: "https://inference.do-ai.run/v1/chat/completions"
  model: "llama3-8b-instruct"
  api_key: "${DIGITALOCEAN_API_KEY}"
  max_retries: 2
  retry_delay: 0.5
  request_timeout: 20

# Text Processing
chunking:
  max_chunk_size: 600
  min_chunk_size: 100
  overlap_size: 50
  chunk_by_sections: false
  optimize_chunks: false

# QA Generation
qa:
  max_questions_per_chunk: 1
  min_question_length: 5
  max_question_length: 100

# Validation (Lenient for testing)
validation:
  min_overall_score: 0.60
  min_source_overlap: 0.50
  min_relevancy_score: 0.60
  enable_semantic: false

# Cost Management
cost:
  max_total_cost_usd: 1.0
  cost_per_token: 0.000001
  batch_size: 1
  dry_run: false

# Output
output:
  base_path: "output/datasets/dev_output.jsonl"
  separate_by_quality: false
  enable_audit_log: false

# Monitoring
monitoring:
  enable_metrics: false
  log_structured: false
'''


def cmd_validate_config(args):
    """Handle config validation command."""
    config_path = args.config_path or args.config
    
    if not config_path:
        print("Error: No configuration file specified")
        return 1
    
    print(f"\nValidating configuration: {config_path}")
    
    try:
        config = Config(config_path)
        print("✓ Configuration file is valid")
        print(f"✓ Environment: {getattr(config, 'environment', 'unknown')}")
        print(f"✓ Model: {getattr(config.llm, 'model', 'unknown')}")
        print(f"✓ Max cost: ${getattr(config.cost, 'max_total_cost_usd', 0.0)}")
        
        # Check for API key
        if hasattr(config.llm, 'api_key') and config.llm.api_key and not config.llm.api_key.startswith('${'):
            print("✓ API key configured")
        else:
            print("⚠️  API key not set or using environment variable")
        
        return 0
        
    except Exception as e:
        print(f"✗ Configuration validation failed: {e}")
        return 1


async def cmd_status(args):
    """Handle status command."""
    print("\nGetting processing status...")
    
    try:
        setforge = ProductionSetForge(args.config)
        status = setforge.get_status()
        
        print("\n" + "="*40)
        print("PROCESSING STATUS")
        print("="*40)
        print(f"Running: {'Yes' if status['is_running'] else 'No'}")
        print(f"Files processed: {status['processed_files']}")
        print(f"Files failed: {status['failed_files']}")
        print(f"Current cost: ${status['current_cost']:.4f}")
        print(f"Budget remaining: ${status['budget_remaining']:.4f}")
        
        perf_metrics = status.get('performance_metrics', {})
        if perf_metrics:
            print(f"QA pairs generated: {perf_metrics.get('qa_pairs_generated', 0)}")
            print(f"QA pairs validated: {perf_metrics.get('qa_pairs_validated', 0)}")
            print(f"Validation pass rate: {perf_metrics.get('validation_pass_rate', 0):.1%}")
        
        if status['shutdown_requested']:
            print("\n⚠️  Shutdown requested")
        
        print("="*40)
        
        return 0
        
    except Exception as e:
        print(f"Status check failed: {e}")
        return 1


async def main():
    """Main CLI function."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Print header
    print_header()
    
    # Handle missing command
    if not args.command:
        parser.print_help()
        return 1
    
    # Set log level if specified
    if args.log_level:
        import logging
        logging.basicConfig(level=getattr(logging, args.log_level))
    
    # Route to appropriate command handler
    try:
        if args.command == 'process':
            return await cmd_process(args)
        elif args.command == 'estimate':
            return await cmd_estimate(args)
        elif args.command == 'health-check':
            return await cmd_health_check(args)
        elif args.command == 'create-config':
            return cmd_create_config(args)
        elif args.command == 'validate':
            return cmd_validate_config(args)
        elif args.command == 'status':
            return await cmd_status(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
            
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return 1


if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)
