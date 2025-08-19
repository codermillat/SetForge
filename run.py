#!/usr/bin/env python3
"""
SetForge Production Pipeline - Centralized Entry Point
AI Counselor for Bangladeshi Students - MIT License Research Project

Usage:
    python run.py --mode=production
    python run.py --mode=production --target=15000 --quality=8.5
    python run.py --mode=production --multilingual --edge-cases
"""

import os
import sys
from pathlib import Path

# Add project root to path before other imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import asyncio
import argparse
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
dotenv_path = Path(__file__).parent / 'config.env'
load_dotenv(dotenv_path=dotenv_path)

from production_pipeline import SetForgeProductionPipeline
from src.utils.config_manager import ConfigManager
from src.utils.logging_config import setup_logging
from src.utils.environment import validate_environment
from src.utils.checkpoint_manager import CheckpointManager

class SetForgeRunner:
    """Centralized runner for SetForge production pipeline"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.pipeline = None
        self.logger = self.setup_logging()
    
    def setup_logging(self, log_level: str = "INFO"):
        """Setup centralized logging"""
        self.logger = setup_logging(
            log_level=log_level,
            log_file=os.getenv('LOG_FILE', 'setforge_production.log'),
            enable_progress=os.getenv('ENABLE_PROGRESS_TRACKING', 'true').lower() == 'true'
        )
        return self.logger

    def validate_configuration(self) -> bool:
        """Validate all configuration and environment variables"""
        try:
            # Validate environment variables
            if not validate_environment():
                self.logger.error("❌ Environment validation failed")
                return False

            # Validate context files
            context_dir = Path("data")
            if not context_dir.exists():
                self.logger.error("❌ Context directory not found: data/")
                return False
            
            context_files = list(context_dir.rglob("*.txt"))
            if not context_files:
                self.logger.warning("No context files found in data/. This may not be an error if you are only cleaning or structuring data.")

            self.logger.info(f"✅ Found {len(context_files)} context files")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Configuration validation error: {e}")
            return False
    
    def parse_arguments(self) -> Dict[str, Any]:
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description="SetForge Production Pipeline - AI Counselor for Bangladeshi Students",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
    python run.py --mode=production
    python run.py --mode=production --target=15000 --quality=8.5
    python run.py --mode=production --multilingual --edge-cases
    python run.py --mode=production --batch-size=200 --parallel=10
            """
        )
        
        # Mode selection
        parser.add_argument(
            '--mode',
            choices=['production', 'test', 'validate'],
            default='production',
            help='Pipeline mode (default: production)'
        )
        
        parser.add_argument(
            '--steps',
            nargs='+',
            choices=['clean', 'recognize', 'structure', 'validate', 'generate'],
            default=['clean', 'recognize', 'structure', 'validate', 'generate'],
            help='Specify which steps of the pipeline to run (default: all)'
        )
        
        # Dataset generation parameters
        parser.add_argument(
            '--target',
            type=int,
            default=int(os.getenv('TARGET_DATASET_SIZE', 15000)),
            help='Target dataset size (default: 15000)'
        )
        
        parser.add_argument(
            '--quality',
            type=float,
            default=float(os.getenv('QUALITY_THRESHOLD', 8.5)),
            help='Minimum quality threshold (default: 8.5)'
        )
        
        # Feature flags
        parser.add_argument(
            '--multilingual',
            action='store_true',
            help='Enable multilingual generation (Bengali + English)'
        )
        
        parser.add_argument(
            '--edge-cases',
            action='store_true',
            help='Enable comprehensive edge case coverage'
        )
        
        parser.add_argument(
            '--semantic-analysis',
            action='store_true',
            help='Enable advanced semantic analysis'
        )
        
        # Performance settings
        parser.add_argument(
            '--batch-size',
            type=int,
            default=int(os.getenv('BATCH_SIZE', 100)),
            help='Batch size for processing (default: 100)'
        )
        
        parser.add_argument(
            '--parallel',
            type=int,
            default=int(os.getenv('PARALLEL_REQUESTS', 5)),
            help='Number of parallel requests (default: 5)'
        )
        
        # Output settings
        parser.add_argument(
            '--output',
            type=str,
            default='output/production_dataset.jsonl',
            help='Output file path (default: output/production_dataset.jsonl)'
        )
        
        parser.add_argument(
            '--checkpoint-interval',
            type=int,
            default=int(os.getenv('CHECKPOINT_INTERVAL', 50)),
            help='Checkpoint interval (default: 50)'
        )
        
        # API strategy
        parser.add_argument(
            '--hybrid-ratio',
            type=float,
            default=0.6,
            help='Template vs LLM ratio (default: 0.6 for 60% template)'
        )
        
        parser.add_argument(
            '--enable-backup',
            action='store_true',
            default=True,
            help='Enable backup API models (default: True)'
        )
        
        # Logging
        parser.add_argument(
            '--log-level',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            default=os.getenv('LOG_LEVEL', 'INFO'),
            help='Logging level (default: INFO)'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )
        
        # Checkpoint management
        parser.add_argument(
            '--resume',
            action='store_true',
            default=True,
            help='Resume from last checkpoint (default: True)'
        )
        
        parser.add_argument(
            '--no-resume',
            action='store_true',
            help='Force start new session (ignore existing checkpoints)'
        )
        
        parser.add_argument(
            '--list-sessions',
            action='store_true',
            help='List all existing sessions'
        )
        
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up old completed sessions'
        )
        
        parser.add_argument(
            '--force-rebuild',
            action='store_true',
            help='Force rebuild of the local RAG index'
        )
        
        return vars(parser.parse_args())
    
    async def run_production_pipeline(self, args: Dict[str, Any]) -> bool:
        """Run the complete production pipeline"""
        try:
            self.logger.info("🚀 Starting SetForge Production Pipeline")
            self.logger.info("=" * 60)
            
            # Initialize pipeline
            self.pipeline = SetForgeProductionPipeline(
                config=self.config,
                logger=self.logger
            )
            
            # Run pipeline
            success = await self.pipeline.run()
            
            if success:
                self.logger.info("✅ Production pipeline completed successfully!")
                self.logger.info(f"📊 Dataset saved to: {args['output']}")
                return True
            else:
                self.logger.error("❌ Production pipeline failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Pipeline execution error: {e}")
            return False
    
    async def run_test_pipeline(self, args: Dict[str, Any]) -> bool:
        """Run test pipeline with limited scope"""
        try:
            self.logger.info("🧪 Starting SetForge Test Pipeline")
            self.logger.info("=" * 60)
            
            # Modify args for testing
            test_args = args.copy()
            test_args['target'] = min(args['target'], 100)  # Limit test size
            test_args['batch_size'] = min(args['batch_size'], 10)
            test_args['parallel'] = min(args['parallel'], 2)
            
            # Initialize pipeline
            self.pipeline = SetForgeProductionPipeline(
                config=self.config,
                logger=self.logger
            )
            
            # Run test
            success = await self.pipeline.run_test()
            
            if success:
                self.logger.info("✅ Test pipeline completed successfully!")
                return True
            else:
                self.logger.error("❌ Test pipeline failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Test execution error: {e}")
            return False
    
    async def run_validation(self, args: Dict[str, Any]) -> bool:
        """Run validation checks"""
        try:
            self.logger.info("🔍 Starting SetForge Validation")
            self.logger.info("=" * 60)
            
            # Initialize pipeline for validation
            self.pipeline = SetForgeProductionPipeline(
                config=self.config,
                logger=self.logger
            )
            
            # Run validation
            success = await self.pipeline.validate_setup()
            
            if success:
                self.logger.info("✅ Validation completed successfully!")
                return True
            else:
                self.logger.error("❌ Validation failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Validation error: {e}")
            return False
    
    async def list_sessions(self) -> bool:
        """List all existing sessions"""
        try:
            checkpoint_manager = CheckpointManager(self.config, self.logger)
            sessions = await checkpoint_manager.list_sessions()
            
            if not sessions:
                self.logger.info("📋 No existing sessions found")
                return True
            
            self.logger.info("📋 Existing Sessions:")
            self.logger.info("=" * 80)
            
            for session in sessions:
                status = "✅ Completed" if session['completed'] else "🔄 In Progress"
                self.logger.info(f"Session ID: {session['session_id']}")
                self.logger.info(f"  Status: {status}")
                self.logger.info(f"  Target: {session['target_size']} pairs")
                self.logger.info(f"  Progress: {session['current_count']}/{session['target_size']} ({session['progress_percentage']:.1f}%)")
                self.logger.info(f"  Started: {session['start_time']}")
                self.logger.info(f"  Output: {session['output_file']}")
                self.logger.info("-" * 80)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to list sessions: {e}")
            return False
    
    async def cleanup_sessions(self) -> bool:
        """Clean up old completed sessions"""
        try:
            checkpoint_manager = CheckpointManager(self.config, self.logger)
            await checkpoint_manager.cleanup_old_sessions(keep_days=7)
            self.logger.info("🧹 Cleanup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to cleanup sessions: {e}")
            return False
    
    async def main(self):
        """Main execution function"""
        try:
            # Parse arguments
            args = self.parse_arguments()
            
            # Setup logging
            log_level = 'DEBUG' if args.get('verbose') else args.get('log_level', 'INFO')
            if self.logger.level != getattr(logging, log_level.upper()):
                self.setup_logging(log_level)
            
            # Display startup information
            self.logger.info("🎯 SetForge Production Pipeline")
            self.logger.info("AI Counselor for Bangladeshi Students")
            self.logger.info("MIT License - Research Project")
            self.logger.info("=" * 60)
            
            self.config.update_from_args(args)
            
            # Validate configuration after updates
            if not self.validate_configuration():
                return False
            
            # Handle special commands first
            if args.get('list_sessions'):
                return await self.list_sessions()
            
            if args.get('cleanup'):
                return await self.cleanup_sessions()
            
            # Handle no-resume flag
            if args.get('no_resume'):
                args['resume'] = False
            
            # Run based on mode
            if args['mode'] == 'production':
                return await self.run_production_pipeline(args)
            elif args['mode'] == 'test':
                return await self.run_test_pipeline(args)
            elif args['mode'] == 'validate':
                return await self.run_validation(args)
            else:
                self.logger.error(f"❌ Unknown mode: {args['mode']}")
                return False
                
        except KeyboardInterrupt:
            self.logger.info("⚠️ Pipeline interrupted by user")
            return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Unexpected error: {e}")
            else:
                print(f"❌ Unexpected error: {e}")
            return False

def main():
    """Entry point"""
    runner = SetForgeRunner()
    
    try:
        # Run the pipeline
        success = asyncio.run(runner.main())
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
    except Exception as e:
        if runner.logger:
            runner.logger.error(f"❌ A critical error occurred: {e}", exc_info=True)
        else:
            print(f"❌ A critical error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
