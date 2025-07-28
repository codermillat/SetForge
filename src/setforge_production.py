"""
Production-grade SetForge orchestrator with health checks and monitoring.
"""

import asyncio
import logging
import time
import signal
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path

from config import Config
from text_processor import TextProcessor
from qa_generator import QAGenerator
from validator_enhanced import ProductionQAValidator
from exporter_enhanced import ProductionExporter
from monitoring import ProductionMonitor, CostOptimizer


class ProductionSetForge:
    """Production-ready SetForge orchestrator with comprehensive monitoring."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = Config(config_path) if config_path else Config()
        self.logger = self._setup_logging()
        
        # Initialize components
        self.text_processor = TextProcessor(self.config)
        self.qa_generator = QAGenerator(self.config)
        self.validator = ProductionQAValidator(self.config)
        self.exporter = ProductionExporter(self.config)
        self.monitor = ProductionMonitor(self.config)
        self.cost_optimizer = CostOptimizer(self.config, self.monitor)
        
        # State management
        self.is_running = False
        self.processed_files = set()
        self.failed_files = set()
        self.shutdown_requested = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info(f"SetForge initialized in {self.config.environment} mode")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup production logging configuration."""
        logger = logging.getLogger('setforge')
        
        if not logger.handlers:  # Avoid duplicate handlers
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
                # Human-readable logging for development
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
            
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, self.config.environment.upper(), logging.INFO))
        
        return logger
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
    
    async def process_directory(self, input_dir: str, output_path: str) -> Dict[str, Any]:
        """Process directory with comprehensive monitoring and error handling."""
        start_time = time.time()
        self.is_running = True
        
        try:
            # Pre-flight checks
            await self._perform_health_checks()
            
            # Get files to process
            files_to_process = self._discover_files(input_dir)
            self.logger.info(f"Found {len(files_to_process)} files to process")
            
            if not files_to_process:
                return {'error': 'No valid files found in input directory'}
            
            # Process files with monitoring
            processing_results = await self._process_files_with_monitoring(
                files_to_process, output_path
            )
            
            # Generate final reports
            await self._generate_final_reports(output_path)
            
            processing_time = time.time() - start_time
            
            # Final summary
            summary = {
                'success': True,
                'total_files': len(files_to_process),
                'processed_files': len(self.processed_files),
                'failed_files': len(self.failed_files),
                'processing_time_seconds': processing_time,
                'cost_breakdown': self.monitor.cost_breakdown,
                'performance_metrics': self.monitor.performance_metrics,
                'export_statistics': self.exporter.get_export_statistics(),
                'validation_statistics': self.validator.get_validation_statistics()
            }
            
            self.logger.info(f"Processing completed: {summary}")
            return summary
            
        except Exception as e:
            self.logger.error(f"Processing failed: {e}", exc_info=True)
            return {'error': str(e), 'success': False}
        
        finally:
            self.is_running = False
    
    async def _perform_health_checks(self):
        """Perform comprehensive health checks before processing."""
        self.logger.info("Performing health checks...")
        
        # Check API connectivity
        try:
            health_check_result = await self.qa_generator.health_check()
            if not health_check_result.get('healthy', False):
                raise RuntimeError(f"API health check failed: {health_check_result}")
            self.logger.info("✓ API connectivity check passed")
        except Exception as e:
            raise RuntimeError(f"API health check failed: {e}")
        
        # Check configuration validity
        try:
            self.config._validate()
            self.logger.info("✓ Configuration validation passed")
        except Exception as e:
            raise RuntimeError(f"Configuration validation failed: {e}")
        
        # Check available disk space
        try:
            import shutil
            free_space_gb = shutil.disk_usage('.').free / (1024**3)
            if free_space_gb < 1:  # Require at least 1GB free
                raise RuntimeError(f"Insufficient disk space: {free_space_gb:.2f}GB available")
            self.logger.info(f"✓ Disk space check passed ({free_space_gb:.2f}GB available)")
        except Exception as e:
            self.logger.warning(f"Disk space check failed: {e}")
        
        # Check memory availability
        try:
            import psutil
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 90:
                self.logger.warning(f"High memory usage: {memory_percent}%")
            else:
                self.logger.info(f"✓ Memory check passed ({memory_percent}% used)")
        except ImportError:
            self.logger.info("psutil not available, skipping memory check")
        except Exception as e:
            self.logger.warning(f"Memory check failed: {e}")
        
        self.logger.info("Health checks completed successfully")
    
    def _discover_files(self, input_dir: str) -> List[str]:
        """Discover and validate input files."""
        input_path = Path(input_dir)
        
        if not input_path.exists():
            raise ValueError(f"Input directory does not exist: {input_dir}")
        
        if input_path.is_file():
            # Single file processing
            return [str(input_path)]
        
        # Directory processing
        valid_extensions = getattr(self.config.input, 'valid_extensions', ['.txt', '.md'])
        files = []
        
        for ext in valid_extensions:
            files.extend(input_path.glob(f"**/*{ext}"))
        
        # Filter out files that are too small or too large
        min_size = getattr(self.config.input, 'min_file_size_bytes', 100)
        max_size = getattr(self.config.input, 'max_file_size_bytes', 10 * 1024 * 1024)  # 10MB
        
        filtered_files = []
        for file_path in files:
            try:
                file_size = file_path.stat().st_size
                if min_size <= file_size <= max_size:
                    filtered_files.append(str(file_path))
                else:
                    self.logger.warning(f"Skipping {file_path}: size {file_size} bytes outside range [{min_size}, {max_size}]")
            except Exception as e:
                self.logger.warning(f"Could not check file size for {file_path}: {e}")
        
        return filtered_files
    
    async def _process_files_with_monitoring(self, files_to_process: List[str], output_path: str) -> Dict[str, Any]:
        """Process files with comprehensive monitoring and optimization."""
        results = {
            'processed': 0,
            'failed': 0,
            'total_qa_pairs': 0,
            'total_cost': 0.0
        }
        
        # Dynamic batch size optimization
        current_batch_size = getattr(self.config.cost, 'batch_size', 5)
        
        for i, file_path in enumerate(files_to_process):
            if self.shutdown_requested:
                self.logger.info("Shutdown requested, stopping processing")
                break
            
            # Check if we should continue processing
            if not self.monitor.should_continue_processing():
                self.logger.warning("Stopping processing due to budget or performance constraints")
                break
            
            # Process single file
            file_start_time = time.time()
            
            try:
                file_results = await self._process_single_file(file_path, output_path)
                
                self.processed_files.add(file_path)
                results['processed'] += 1
                results['total_qa_pairs'] += file_results.get('qa_pairs_generated', 0)
                results['total_cost'] += file_results.get('cost', 0.0)
                
                # Track performance
                processing_time = time.time() - file_start_time
                self.monitor.track_performance('file_processed', 
                                             file_path=file_path, 
                                             processing_time=processing_time)
                
                # Optimize batch size dynamically
                if i % 5 == 0:  # Check every 5 files
                    new_batch_size = self.cost_optimizer.optimize_batch_size()
                    if new_batch_size != current_batch_size:
                        current_batch_size = new_batch_size
                        self.logger.info(f"Adjusted batch size to {current_batch_size}")
                
                # Progress logging
                if (i + 1) % 10 == 0 or (i + 1) == len(files_to_process):
                    progress = (i + 1) / len(files_to_process) * 100
                    self.logger.info(f"Progress: {progress:.1f}% ({i + 1}/{len(files_to_process)} files)")
                
            except Exception as e:
                self.logger.error(f"Failed to process {file_path}: {e}", exc_info=True)
                self.failed_files.add(file_path)
                results['failed'] += 1
                
                # Continue processing other files in production
                if self.config.environment == 'production':
                    continue
                else:
                    # In development, might want to stop on first error
                    if getattr(self.config, 'stop_on_error', False):
                        raise
        
        return results
    
    async def _process_single_file(self, file_path: str, output_path: str) -> Dict[str, Any]:
        """Process a single file with comprehensive error handling."""
        self.logger.debug(f"Processing file: {file_path}")
        
        file_results = {
            'qa_pairs_generated': 0,
            'qa_pairs_validated': 0,
            'cost': 0.0,
            'chunks_processed': 0
        }
        
        try:
            # Step 1: Text processing
            chunks = await self.text_processor.process_file(file_path)
            self.logger.debug(f"Generated {len(chunks)} chunks from {file_path}")
            
            # Step 2: Collect all QA pairs from all chunks
            all_qa_pairs = []
            for chunk in chunks:
                if self.shutdown_requested:
                    break
                
                try:
                    # Generate enhanced QA pairs with paraphrasing and data augmentation
                    if hasattr(self.qa_generator, 'generate_enhanced_qa_pairs'):
                        qa_pairs = await self.qa_generator.generate_enhanced_qa_pairs(chunk)
                    else:
                        qa_pairs = await self.qa_generator.generate_qa_pairs(chunk)
                    
                    self.monitor.track_performance('chunk_processed')
                    
                    file_results['chunks_processed'] += 1
                    file_results['qa_pairs_generated'] += len(qa_pairs)
                    
                    # Add source file metadata to each QA pair
                    for qa_pair in qa_pairs:
                        if not hasattr(qa_pair, 'metadata'):
                            qa_pair.metadata = {}
                        qa_pair.metadata['source_file'] = file_path
                    
                    all_qa_pairs.extend(qa_pairs)
                    self.logger.debug(f"Generated {len(qa_pairs)} QA pairs from chunk {chunk.id}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to process chunk {chunk.id}: {e}")
                    continue
            
            # Step 3: Deduplicate QA pairs at file level
            if getattr(self.config.validation, 'enable_deduplication', False) and all_qa_pairs:
                original_count = len(all_qa_pairs)
                all_qa_pairs = self.validator.deduplicate_qa_pairs(all_qa_pairs)
                deduplicated_count = len(all_qa_pairs)
                self.logger.info(f"Deduplication: {original_count} -> {deduplicated_count} QA pairs for {file_path}")
            
            # Step 4: Validate and export deduplicated QA pairs
            for qa_pair in all_qa_pairs:
                if self.shutdown_requested:
                    break
                    
                try:
                    # Validate QA pair
                    validation_result = await self.validator.validate_qa_pair(qa_pair)
                    
                    if validation_result.is_valid:
                        # Export valid QA pair
                        export_success = await self.exporter.export_qa_pair(
                            qa_pair, 
                            validation_result,
                            {'source_file': file_path}
                        )
                        
                        if export_success:
                            file_results['qa_pairs_validated'] += 1
                            self.monitor.track_performance('qa_validated', count=1)
                        
                        # Track cost
                        cost = getattr(qa_pair, 'generation_cost', 0.0)
                        file_results['cost'] += cost
                        
                        self.monitor.track_cost(
                            file_path=file_path,
                            tokens_used=getattr(qa_pair, 'tokens_used', 0),
                            model_name=self.config.llm.model_name,
                            cost=cost
                        )
                    
                    self.monitor.track_performance('qa_generated', count=1)
                    
                except Exception as e:
                    self.logger.error(f"Failed to validate/export QA pair: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Failed to process file {file_path}: {e}")
            raise
        
        return file_results
    
    async def _generate_final_reports(self, output_path: str):
        """Generate comprehensive final reports."""
        try:
            # Performance report
            performance_report = self.monitor.get_final_report()
            self.monitor.save_report(output_path)
            
            # Dataset manifest
            manifest_path = self.exporter.create_dataset_manifest(output_path)
            
            # Data lineage report
            lineage_path = self.exporter.create_data_lineage_report(output_path)
            
            # Optimization recommendations
            recommendations = self.cost_optimizer.get_optimization_recommendations()
            if recommendations:
                self.logger.info("Optimization Recommendations:")
                for rec in recommendations:
                    self.logger.info(f"  • {rec}")
            
            self.logger.info("Final reports generated successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to generate final reports: {e}")
    
    async def estimate_cost(self, input_dir: str) -> Dict[str, Any]:
        """Estimate processing cost for the given input."""
        try:
            files = self._discover_files(input_dir)
            
            total_size = sum(Path(f).stat().st_size for f in files)
            estimated_chunks = total_size // self.config.chunking.max_chunk_size
            estimated_tokens = estimated_chunks * 500  # Rough estimate
            estimated_cost = estimated_tokens * self.config.cost.cost_per_token
            
            estimate = {
                'files_count': len(files),
                'total_size_bytes': total_size,
                'estimated_chunks': estimated_chunks,
                'estimated_tokens': estimated_tokens,
                'estimated_cost_usd': estimated_cost,
                'estimated_duration_minutes': estimated_chunks * 2,  # Rough estimate
                'budget_utilization': estimated_cost / self.config.cost.max_total_cost_usd * 100
            }
            
            self.logger.info(f"Cost estimate: {estimate}")
            return estimate
            
        except Exception as e:
            self.logger.error(f"Cost estimation failed: {e}")
            return {'error': str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get current processing status."""
        return {
            'is_running': self.is_running,
            'processed_files': len(self.processed_files),
            'failed_files': len(self.failed_files),
            'shutdown_requested': self.shutdown_requested,
            'current_cost': self.monitor.cost_breakdown.total_cost,
            'budget_remaining': max(0, self.config.cost.max_total_cost_usd - self.monitor.cost_breakdown.total_cost),
            'performance_metrics': {
                'files_processed': self.monitor.performance_metrics.files_processed,
                'qa_pairs_generated': self.monitor.performance_metrics.qa_pairs_generated,
                'qa_pairs_validated': self.monitor.performance_metrics.qa_pairs_validated,
                'validation_pass_rate': self.monitor.performance_metrics.validation_pass_rate
            }
        }


# Health check endpoint function for deployment
async def health_check(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Standalone health check function for monitoring."""
    try:
        config = Config(config_path) if config_path else Config()
        qa_generator = QAGenerator(config)
        
        # Basic health checks
        health_result = await qa_generator.health_check()
        
        return {
            'status': 'healthy' if health_result.get('healthy', False) else 'unhealthy',
            'timestamp': time.time(),
            'version': getattr(config, 'version', '2.0'),
            'environment': getattr(config, 'environment', 'unknown'),
            'api_status': health_result
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'timestamp': time.time(),
            'error': str(e)
        }
