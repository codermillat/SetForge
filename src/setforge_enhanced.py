"""
Enhanced SetForge Production System
Integrates comprehensive tracking, resumability, and quality assurance
"""

import asyncio
import logging
import signal
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import json

from config import Config
from text_processor import TextProcessor
from qa_generator import QAGenerator
from validator_enhanced import ProductionQAValidator
from exporter_enhanced import ProductionExporter
from monitoring import ProductionMonitor, CostOptimizer
from progress_tracker import ProgressTracker
from resumable_processor import ResumableProcessor
from quality_monitor import QualityMonitor
from status_dashboard import StatusDashboard

logger = logging.getLogger(__name__)


class EnhancedSetForgeProduction:
    """
    Enhanced SetForge production system with comprehensive tracking,
    resumability, quality assurance, and real-time monitoring.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        # Core configuration
        self.config = Config(config_path) if config_path else Config()
        self._setup_logging()
        
        # Core components
        self.text_processor = TextProcessor(self.config)
        self.qa_generator = QAGenerator(self.config)
        self.validator = ProductionQAValidator(self.config)
        self.exporter = ProductionExporter(self.config)
        self.monitor = ProductionMonitor(self.config)
        self.cost_optimizer = CostOptimizer(self.config, self.monitor)
        
        # Enhanced tracking components
        self.progress_tracker: Optional[ProgressTracker] = None
        self.resumable_processor = ResumableProcessor(self.config)
        self.quality_monitor = QualityMonitor(self.config)
        self.status_dashboard = StatusDashboard(self.config)
        
        # State management
        self.is_running = False
        self.shutdown_requested = False
        self.processed_files = set()
        self.failed_files = set()
        
        # Performance tracking
        self.start_time = 0
        self.total_qa_pairs_generated = 0
        self.total_cost = 0.0
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Enhanced SetForge Production initialized")
    
    def _setup_logging(self):
        """Setup production logging"""
        logger = logging.getLogger('setforge')
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            
            if getattr(self.config.monitoring, 'log_structured', False):
                # JSON logging for production
                import json
                
                class JSONFormatter(logging.Formatter):
                    def format(self, record):
                        log_entry = {
                            'timestamp': record.created,
                            'level': record.levelname,
                            'module': record.name,
                            'message': record.getMessage(),
                            'config_hash': getattr(self.config, 'config_hash', 'unknown')
                        }
                        if hasattr(record, 'exc_info') and record.exc_info:
                            log_entry['exception'] = str(record.exc_info[1])
                        return json.dumps(log_entry)
                
                handler.setFormatter(JSONFormatter())
            else:
                # Human-readable logging
                formatter = logging.Formatter(
                    '%(asctime)s | %(levelname)8s | %(name)s | %(message)s'
                )
                handler.setFormatter(formatter)
            
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, self.config.log_level.upper(), logging.INFO))
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
    
    async def process_directory_enhanced(self, input_dir: str, output_path: str) -> Dict[str, Any]:
        """
        Enhanced directory processing with full tracking and monitoring
        """
        self.start_time = time.time()
        self.is_running = True
        
        try:
            # Pre-flight checks
            await self._perform_enhanced_health_checks()
            
            # Initialize tracking systems
            files_to_process = await self._initialize_tracking_systems(input_dir)
            
            if not files_to_process:
                return {'error': 'No files to process', 'success': False}
            
            # Start live dashboard if enabled - but in a non-blocking way
            # For now, we'll skip the live dashboard to ensure processing completes
            # TODO: Implement proper background dashboard
            
            # Process files with comprehensive tracking
            results = await self._process_files_enhanced(files_to_process, output_path)
            
            # Generate final reports
            await self._generate_enhanced_reports(output_path)
            
            return results
            
        except Exception as e:
            logger.error(f"Enhanced processing failed: {e}", exc_info=True)
            return {'error': str(e), 'success': False}
            
        finally:
            await self._cleanup_enhanced_systems()
            self.is_running = False
    
    async def _perform_enhanced_health_checks(self):
        """Perform comprehensive health checks with tracking"""
        logger.info("Performing enhanced health checks...")
        
        # Core health checks with relaxed validation
        try:
            health_result = await self.qa_generator.health_check()
            # Accept if API is configured and status is not 'failed'
            if health_result.get('api_configured', False) and health_result.get('status') != 'failed':
                logger.info(f"✓ API connectivity check passed (status: {health_result.get('status')})")
            else:
                logger.warning(f"API health check degraded but proceeding: {health_result}")
        except Exception as e:
            logger.warning(f"Health check failed but proceeding: {e}")
        
        # Configuration validation
        try:
            self.config._validate()
            logger.info("✓ Configuration validation passed")
        except Exception as e:
            raise RuntimeError(f"Configuration validation failed: {e}")
        
        # Check tracking system readiness
        try:
            checkpoint_dir = Path("output/checkpoints")
            checkpoint_dir.mkdir(parents=True, exist_ok=True)
            
            quality_dir = Path("output/quality")
            quality_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info("✓ Tracking systems ready")
        except Exception as e:
            logger.warning(f"Tracking system setup warning: {e}")
        
        # Resource checks
        self._check_system_resources()
        
        logger.info("Enhanced health checks completed successfully")
    
    def _check_system_resources(self):
        """Check system resource availability"""
        try:
            import shutil
            free_space_gb = shutil.disk_usage('.').free / (1024**3)
            if free_space_gb < 1:
                raise RuntimeError(f"Insufficient disk space: {free_space_gb:.2f}GB available")
            logger.info(f"✓ Disk space check passed ({free_space_gb:.2f}GB available)")
        except Exception as e:
            logger.warning(f"Disk space check failed: {e}")
        
        try:
            import psutil
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 90:
                logger.warning(f"High memory usage: {memory_percent}%")
            else:
                logger.info(f"✓ Memory check passed ({memory_percent}% used)")
        except ImportError:
            logger.info("psutil not available, skipping memory check")
        except Exception as e:
            logger.warning(f"Memory check failed: {e}")
    
    async def _initialize_tracking_systems(self, input_dir: str) -> List[str]:
        """Initialize all tracking and monitoring systems"""
        logger.info("Initializing enhanced tracking systems...")
        
        # Initialize resumable processor and get files to process
        files_to_process = await self.resumable_processor.initialize_processing(input_dir)
        
        # Initialize progress tracker
        self.progress_tracker = ProgressTracker(
            total_files=len(self.resumable_processor.discover_files(input_dir)),
            config=self.config
        )
        
        # Connect progress tracker to resumable processor
        self.resumable_processor.set_progress_tracker(self.progress_tracker)
        
        # Load existing progress if resuming
        resume_info = self.resumable_processor.get_resume_info()
        if resume_info.get('has_checkpoint'):
            logger.info(f"Resuming from checkpoint: {resume_info.get('processed_files', 0)} files already processed")
        
        logger.info(f"Tracking systems initialized: {len(files_to_process)} files to process")
        return files_to_process
    
    async def _process_files_enhanced(self, files_to_process: List[str], output_path: str) -> Dict[str, Any]:
        """Process files with enhanced tracking and monitoring"""
        
        async def process_single_file_with_tracking(file_path: str) -> Dict[str, Any]:
            """Process a single file with comprehensive tracking"""
            file_start_time = time.time()
            
            # Start file processing in progress tracker
            self.progress_tracker.start_file_processing(file_path)
            
            try:
                # Process file
                result = await self._process_single_file_enhanced(file_path, output_path)
                
                # Complete file processing tracking
                self.progress_tracker.complete_file_processing(
                    file_path,
                    result.get('chunks_created', 0),
                    result.get('qa_pairs_generated', 0),
                    result.get('qa_pairs_validated', 0),
                    result.get('cost', 0.0),
                    result.get('quality_score', 0.0)
                )
                
                return result
                
            except Exception as e:
                # Fail file processing tracking
                self.progress_tracker.fail_file_processing(file_path, str(e))
                raise
        
        # Use resumable processor for enhanced processing
        return await self.resumable_processor.process_with_resume(
            input_dir="",  # Not used since we already have files_to_process
            output_path=output_path,
            process_file_func=process_single_file_with_tracking
        )
    
    async def _process_single_file_enhanced(self, file_path: str, output_path: str) -> Dict[str, Any]:
        """Process a single file with enhanced quality monitoring"""
        logger.debug(f"Processing file with enhanced tracking: {file_path}")
        
        file_results = {
            'qa_pairs_generated': 0,
            'qa_pairs_validated': 0,
            'cost': 0.0,
            'chunks_created': 0,
            'quality_score': 0.0
        }
        
        try:
            # Step 1: Text processing with progress tracking
            chunks = await self.text_processor.process_file(file_path)
            file_results['chunks_created'] = len(chunks)
            
            logger.debug(f"Generated {len(chunks)} chunks from {file_path}")
            
            # Step 2: Enhanced QA generation with quality monitoring
            all_qa_pairs = []
            quality_scores = []
            
            for chunk in chunks:
                if self.shutdown_requested:
                    break
                
                try:
                    # Generate QA pairs
                    if hasattr(self.qa_generator, 'generate_enhanced_qa_pairs'):
                        qa_pairs = await self.qa_generator.generate_enhanced_qa_pairs(chunk)
                    else:
                        qa_pairs = await self.qa_generator.generate_qa_pairs(chunk)
                    
                    file_results['qa_pairs_generated'] += len(qa_pairs)
                    
                    # Add metadata
                    for qa_pair in qa_pairs:
                        if not hasattr(qa_pair, 'metadata'):
                            qa_pair.metadata = {}
                        qa_pair.metadata['source_file'] = file_path
                    
                    all_qa_pairs.extend(qa_pairs)
                    
                except Exception as e:
                    logger.error(f"Failed to process chunk {chunk.id}: {e}")
                    continue
            
            # Step 3: Enhanced validation with quality monitoring
            validated_qa_pairs = []
            
            for qa_pair in all_qa_pairs:
                if self.shutdown_requested:
                    break
                
                try:
                    # Validate QA pair
                    validation_result = await self.validator.validate_qa_pair(qa_pair)
                    
                    # Monitor quality
                    quality_assessment = await self.quality_monitor.monitor_qa_quality(
                        qa_pair, validation_result, file_path
                    )
                    
                    # Update progress tracker quality metrics
                    self.progress_tracker.update_quality_metrics(
                        validation_result.overall_score if hasattr(validation_result, 'overall_score') else quality_assessment['overall_score'],
                        getattr(validation_result, 'relevancy_score', 0.8),
                        getattr(validation_result, 'source_overlap', 0.9),
                        getattr(validation_result, 'hallucination_detected', False)
                    )
                    
                    if validation_result.is_valid:
                        # Export valid QA pair
                        export_success = await self.exporter.export_qa_pair(
                            qa_pair, 
                            validation_result,
                            {'source_file': file_path}
                        )
                        
                        if export_success:
                            validated_qa_pairs.append(qa_pair)
                            file_results['qa_pairs_validated'] += 1
                            quality_scores.append(quality_assessment['overall_score'])
                        
                        # Track cost
                        cost = getattr(qa_pair, 'generation_cost', 0.0)
                        file_results['cost'] += cost
                        
                        self.monitor.track_cost(
                            file_path=file_path,
                            tokens_used=getattr(qa_pair, 'tokens_used', 0),
                            model_name=self.config.llm.model_name,
                            cost=cost
                        )
                
                except Exception as e:
                    logger.error(f"Failed to validate/export QA pair: {e}")
                    continue
            
            # Calculate average quality score for this file
            if quality_scores:
                file_results['quality_score'] = sum(quality_scores) / len(quality_scores)
            
            # Update totals
            self.total_qa_pairs_generated += file_results['qa_pairs_generated']
            self.total_cost += file_results['cost']
            
            logger.debug(f"Completed {file_path}: {file_results['qa_pairs_validated']} validated QA pairs")
            
            return file_results
            
        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")
            raise
    
    async def _generate_enhanced_reports(self, output_path: str):
        """Generate comprehensive reports with enhanced metrics"""
        try:
            logger.info("Generating enhanced reports...")
            
            # Generate progress report
            if self.progress_tracker:
                progress_report = self.progress_tracker.generate_progress_report()
                
                progress_report_file = Path(output_path).parent / "progress_report.json"
                with open(progress_report_file, 'w') as f:
                    json.dump(progress_report, f, indent=2)
                
                logger.info(f"Progress report saved: {progress_report_file}")
            
            # Generate quality report
            quality_report = self.quality_monitor.generate_quality_report()
            
            quality_report_file = Path(output_path).parent / "quality_report.json"
            with open(quality_report_file, 'w') as f:
                json.dump(quality_report, f, indent=2)
            
            logger.info(f"Quality report saved: {quality_report_file}")
            
            # Export quality data
            quality_data_file = Path(output_path).parent / "quality_data.json"
            self.quality_monitor.export_quality_data(str(quality_data_file))
            
            # Generate traditional reports
            performance_report = self.monitor.get_final_report()
            self.monitor.save_report(str(Path(output_path).parent))
            
            # Dataset manifest
            manifest_path = self.exporter.create_dataset_manifest(str(Path(output_path).parent))
            
            # Data lineage report
            lineage_path = self.exporter.create_data_lineage_report(str(Path(output_path).parent))
            
            # Optimization recommendations
            recommendations = self.cost_optimizer.get_optimization_recommendations()
            if recommendations:
                logger.info("Optimization Recommendations:")
                for rec in recommendations:
                    logger.info(f"  • {rec}")
            
            logger.info("Enhanced reports generated successfully")
            
        except Exception as e:
            logger.error(f"Failed to generate enhanced reports: {e}")
    
    async def _cleanup_enhanced_systems(self):
        """Clean up enhanced tracking systems"""
        try:
            # Stop dashboard
            await self.status_dashboard.stop_dashboard()
            
            # Final checkpoint save
            if self.progress_tracker:
                self.progress_tracker.save_checkpoint()
            
            # Clean up old alerts
            self.quality_monitor.clear_old_alerts(hours=24)
            
            logger.info("Enhanced systems cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during enhanced cleanup: {e}")
    
    async def estimate_cost_enhanced(self, input_dir: str) -> Dict[str, Any]:
        """Enhanced cost estimation with tracking information"""
        try:
            # Use resumable processor to discover files
            files = self.resumable_processor.discover_files(input_dir)
            
            # Check for existing progress
            resume_info = self.resumable_processor.get_resume_info()
            
            if resume_info.get('has_checkpoint'):
                # Adjust estimation based on existing progress
                processed_files = resume_info.get('processed_files', 0)
                remaining_files = len(files) - processed_files
                existing_cost = resume_info.get('total_cost', 0.0)
                existing_qa_pairs = resume_info.get('total_qa_pairs', 0)
                
                logger.info(f"Found existing progress: {processed_files} files processed, "
                           f"${existing_cost:.4f} spent, {existing_qa_pairs} QA pairs generated")
            else:
                remaining_files = len(files)
                existing_cost = 0.0
                existing_qa_pairs = 0
            
            # Calculate estimates for remaining files
            total_size = sum(Path(f).stat().st_size for f in files)
            avg_chunk_size = self.config.chunking.max_chunk_size
            estimated_chunks = (total_size // avg_chunk_size) * remaining_files // len(files) if files else 0
            
            # Enhanced QA estimation
            questions_per_chunk = self.config.qa.questions_per_chunk
            enable_paraphrasing = getattr(self.config.qa, 'enable_paraphrasing', False)
            paraphrases_per_question = getattr(self.config.qa, 'paraphrases_per_question', 2)
            
            if enable_paraphrasing:
                qa_per_chunk = questions_per_chunk * (1 + paraphrases_per_question)
            else:
                qa_per_chunk = questions_per_chunk
            
            estimated_new_qa_pairs = estimated_chunks * qa_per_chunk
            estimated_tokens = estimated_new_qa_pairs * 150  # tokens per QA pair
            estimated_new_cost = estimated_tokens * getattr(self.config.cost, 'cost_per_token', 0.0000015)
            
            estimate = {
                'total_files': len(files),
                'remaining_files': remaining_files,
                'processed_files': len(files) - remaining_files,
                'existing_cost': existing_cost,
                'existing_qa_pairs': existing_qa_pairs,
                'estimated_new_qa_pairs': estimated_new_qa_pairs,
                'estimated_total_qa_pairs': existing_qa_pairs + estimated_new_qa_pairs,
                'estimated_new_cost': estimated_new_cost,
                'estimated_total_cost': existing_cost + estimated_new_cost,
                'has_checkpoint': resume_info.get('has_checkpoint', False),
                'budget_utilization': ((existing_cost + estimated_new_cost) / 
                                     getattr(self.config.cost, 'max_total_cost_usd', 150)) * 100,
                'configuration': {
                    'questions_per_chunk': questions_per_chunk,
                    'paraphrasing_enabled': enable_paraphrasing,
                    'qa_pairs_per_chunk': qa_per_chunk
                }
            }
            
            logger.info(f"Enhanced cost estimate: {estimate}")
            return estimate
            
        except Exception as e:
            logger.error(f"Enhanced cost estimation failed: {e}")
            return {'error': str(e)}
    
    def get_enhanced_status(self) -> Dict[str, Any]:
        """Get comprehensive enhanced status"""
        status = {
            'is_running': self.is_running,
            'shutdown_requested': self.shutdown_requested,
            'start_time': self.start_time,
            'total_qa_pairs_generated': self.total_qa_pairs_generated,
            'total_cost': self.total_cost
        }
        
        # Add progress tracker status
        if self.progress_tracker:
            status['progress'] = self.progress_tracker.get_status_summary()
        
        # Add quality monitor status
        status['quality'] = self.quality_monitor.get_quality_summary()
        
        # Add resumable processor status
        status['resume_info'] = self.resumable_processor.get_resume_info()
        
        return status
    
    async def resume_processing(self, input_dir: str, output_path: str, 
                              checkpoint_file: Optional[str] = None) -> Dict[str, Any]:
        """Resume processing from a specific checkpoint"""
        logger.info(f"Resuming processing from checkpoint: {checkpoint_file}")
        
        if checkpoint_file and not Path(checkpoint_file).exists():
            raise ValueError(f"Checkpoint file not found: {checkpoint_file}")
        
        # Load checkpoint if specified
        if checkpoint_file:
            await self.resumable_processor.load_checkpoint(checkpoint_file)
        
        # Continue with normal processing
        return await self.process_directory_enhanced(input_dir, output_path)
    
    def display_status_summary(self):
        """Display a comprehensive status summary"""
        if self.progress_tracker:
            self.status_dashboard.display_summary(self.progress_tracker, self.quality_monitor)
        else:
            print("No progress tracking data available")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of all system components"""
        health_status = {
            'timestamp': time.time(),
            'overall_health': 'healthy',
            'components': {}
        }
        
        try:
            # Check core components
            health_status['components']['config'] = {
                'status': 'healthy' if self.config else 'failed',
                'details': 'Configuration loaded successfully'
            }
            
            health_status['components']['text_processor'] = {
                'status': 'healthy' if self.text_processor else 'failed',
                'details': 'Text processor initialized'
            }
            
            health_status['components']['qa_generator'] = {
                'status': 'healthy' if self.qa_generator else 'failed',
                'details': 'QA generator initialized'
            }
            
            health_status['components']['validator'] = {
                'status': 'healthy' if self.validator else 'failed',
                'details': 'Validator initialized'
            }
            
            health_status['components']['exporter'] = {
                'status': 'healthy' if self.exporter else 'failed',
                'details': 'Exporter initialized'
            }
            
            # Check enhanced components
            health_status['components']['progress_tracker'] = {
                'status': 'ready' if not self.progress_tracker else 'healthy',
                'details': 'Progress tracker ready for initialization'
            }
            
            health_status['components']['quality_monitor'] = {
                'status': 'healthy' if self.quality_monitor else 'failed',
                'details': 'Quality monitor initialized'
            }
            
            health_status['components']['resumable_processor'] = {
                'status': 'healthy' if self.resumable_processor else 'failed',
                'details': 'Resumable processor initialized'
            }
            
            health_status['components']['status_dashboard'] = {
                'status': 'healthy' if self.status_dashboard else 'failed',
                'details': 'Status dashboard initialized'
            }
            
            # Check file system permissions
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            health_status['components']['filesystem'] = {
                'status': 'healthy' if output_dir.exists() and output_dir.is_dir() else 'failed',
                'details': f'Output directory: {output_dir.absolute()}'
            }
            
            # Check for failed components
            failed_components = [
                name for name, info in health_status['components'].items() 
                if info['status'] == 'failed'
            ]
            
            if failed_components:
                health_status['overall_health'] = 'degraded'
                health_status['failed_components'] = failed_components
            
            return health_status
            
        except Exception as e:
            health_status['overall_health'] = 'failed'
            health_status['error'] = str(e)
            return health_status


# Main execution functions
async def main_enhanced(input_dir: str = "data/educational", 
                       output_path: str = "output/qa_dataset_enhanced.jsonl",
                       config_path: Optional[str] = None) -> Dict[str, Any]:
    """Main enhanced processing function"""
    setforge = EnhancedSetForgeProduction(config_path)
    
    try:
        logger.info("Starting enhanced SetForge processing...")
        results = await setforge.process_directory_enhanced(input_dir, output_path)
        
        if results.get('success', False):
            logger.info("Enhanced processing completed successfully!")
            setforge.display_status_summary()
        else:
            logger.error(f"Enhanced processing failed: {results.get('error', 'Unknown error')}")
        
        return results
        
    except Exception as e:
        logger.error(f"Enhanced processing failed with exception: {e}")
        return {'error': str(e), 'success': False}


if __name__ == "__main__":
    import sys
    
    # Command line arguments
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "data/educational"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "output/qa_dataset_enhanced.jsonl"
    config_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Run enhanced processing
    results = asyncio.run(main_enhanced(input_dir, output_path, config_path))
    
    # Exit with appropriate code
    sys.exit(0 if results.get('success', False) else 1)
