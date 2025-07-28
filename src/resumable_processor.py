"""
Resumable Processing System for SetForge
Provides checkpoint management, state persistence, and resume capabilities
"""

import json
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import logging
from datetime import datetime

from progress_tracker import ProgressTracker

logger = logging.getLogger(__name__)


class ProcessingState:
    """Manages the current state of processing"""
    
    def __init__(self):
        self.processed_files: Set[str] = set()
        self.failed_files: Set[str] = set()
        self.remaining_files: List[str] = []
        self.current_batch: List[str] = []
        self.total_qa_pairs: int = 0
        self.total_cost: float = 0.0
        self.start_time: float = time.time()
        self.last_checkpoint: Optional[str] = None
        self.processing_metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization"""
        return {
            'processed_files': list(self.processed_files),
            'failed_files': list(self.failed_files),
            'remaining_files': self.remaining_files,
            'current_batch': self.current_batch,
            'total_qa_pairs': self.total_qa_pairs,
            'total_cost': self.total_cost,
            'start_time': self.start_time,
            'last_checkpoint': self.last_checkpoint,
            'processing_metadata': self.processing_metadata
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load state from dictionary"""
        self.processed_files = set(data.get('processed_files', []))
        self.failed_files = set(data.get('failed_files', []))
        self.remaining_files = data.get('remaining_files', [])
        self.current_batch = data.get('current_batch', [])
        self.total_qa_pairs = data.get('total_qa_pairs', 0)
        self.total_cost = data.get('total_cost', 0.0)
        self.start_time = data.get('start_time', time.time())
        self.last_checkpoint = data.get('last_checkpoint')
        self.processing_metadata = data.get('processing_metadata', {})


class ResumableProcessor:
    """
    Handles resumable processing with checkpoint management,
    error recovery, and state persistence.
    """
    
    def __init__(self, config: Any, checkpoint_dir: str = "output/checkpoints"):
        self.config = config
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # State management
        self.state = ProcessingState()
        self.progress_tracker: Optional[ProgressTracker] = None
        
        # Configuration
        self.checkpoint_interval_files = getattr(config.progress, 'checkpoint_interval_files', 5)
        self.checkpoint_interval_minutes = getattr(config.progress, 'checkpoint_interval_minutes', 10)
        self.save_partial_results = getattr(config.progress, 'save_partial_results', True)
        self.auto_cleanup_checkpoints = getattr(config.progress, 'auto_cleanup_checkpoints', True)
        self.max_checkpoint_files = getattr(config.progress, 'max_checkpoint_files', 10)
        
        # Tracking
        self.last_checkpoint_time = time.time()
        self.files_since_checkpoint = 0
        
        logger.info(f"ResumableProcessor initialized with checkpoint dir: {checkpoint_dir}")
    
    def set_progress_tracker(self, progress_tracker: ProgressTracker) -> None:
        """Set the progress tracker instance"""
        self.progress_tracker = progress_tracker
    
    def has_checkpoint(self, checkpoint_file: Optional[str] = None) -> bool:
        """Check if a checkpoint exists"""
        if checkpoint_file:
            return Path(checkpoint_file).exists()
        
        # Check for latest checkpoint
        latest_file = self.checkpoint_dir / "latest_checkpoint.json"
        return latest_file.exists()
    
    def get_latest_checkpoint(self) -> Optional[str]:
        """Get the path to the latest checkpoint file"""
        latest_file = self.checkpoint_dir / "latest_checkpoint.json"
        
        if latest_file.exists():
            return str(latest_file)
        
        # Look for any checkpoint files
        checkpoint_files = list(self.checkpoint_dir.glob("checkpoint_*.json"))
        if checkpoint_files:
            # Return the most recent one
            return str(max(checkpoint_files, key=lambda p: p.stat().st_mtime))
        
        return None
    
    def discover_files(self, input_dir: str) -> List[str]:
        """Discover all files to process"""
        input_path = Path(input_dir)
        
        if not input_path.exists():
            raise ValueError(f"Input directory does not exist: {input_dir}")
        
        if input_path.is_file():
            return [str(input_path)]
        
        # Find all text files
        valid_extensions = getattr(self.config.input, 'valid_extensions', ['.txt', '.md'])
        files = []
        
        for ext in valid_extensions:
            files.extend(input_path.glob(f"**/*{ext}"))
        
        # Filter by size if configured
        min_size = getattr(self.config.input, 'min_file_size_bytes', 100)
        max_size = getattr(self.config.input, 'max_file_size_bytes', 10 * 1024 * 1024)
        
        filtered_files = []
        for file_path in files:
            try:
                file_size = file_path.stat().st_size
                if min_size <= file_size <= max_size:
                    filtered_files.append(str(file_path))
                else:
                    logger.warning(f"Skipping {file_path}: size {file_size} outside range")
            except Exception as e:
                logger.warning(f"Could not check file size for {file_path}: {e}")
        
        return sorted(filtered_files)  # Consistent ordering
    
    async def initialize_processing(self, input_dir: str) -> List[str]:
        """Initialize processing and return files to process"""
        all_files = self.discover_files(input_dir)
        
        if not all_files:
            raise ValueError(f"No valid files found in {input_dir}")
        
        # Check for resume capability
        latest_checkpoint = self.get_latest_checkpoint()
        
        if latest_checkpoint and self.has_checkpoint(latest_checkpoint):
            logger.info(f"Found existing checkpoint: {latest_checkpoint}")
            await self.load_checkpoint(latest_checkpoint)
            
            # Determine remaining files
            self.state.remaining_files = [
                f for f in all_files 
                if f not in self.state.processed_files and f not in self.state.failed_files
            ]
            
            logger.info(f"Resuming from checkpoint: {len(self.state.remaining_files)} files remaining")
            
            # Initialize progress tracker with resume data
            if self.progress_tracker:
                self.progress_tracker.load_checkpoint(latest_checkpoint.replace('checkpoint_', 'progress_checkpoint_'))
            
        else:
            # Fresh start
            self.state.remaining_files = all_files
            self.state.start_time = time.time()
            
            logger.info(f"Starting fresh processing of {len(all_files)} files")
            
            # Initialize progress tracker
            if self.progress_tracker:
                self.progress_tracker.start_time = time.time()
        
        return self.state.remaining_files
    
    async def process_with_resume(self, input_dir: str, output_path: str, 
                                 process_file_func) -> Dict[str, Any]:
        """
        Main processing function with resume capability
        
        Args:
            input_dir: Directory containing files to process
            output_path: Output file path for results
            process_file_func: Async function to process a single file
        """
        try:
            # Initialize processing
            remaining_files = await self.initialize_processing(input_dir)
            
            if not remaining_files:
                logger.info("No files to process (all already completed)")
                return self._get_final_results()
            
            logger.info(f"Processing {len(remaining_files)} files with resume capability")
            
            # Process files with checkpointing
            results = await self._process_files_with_checkpoints(
                remaining_files, output_path, process_file_func
            )
            
            # Clean up old checkpoints if configured
            if self.auto_cleanup_checkpoints:
                self._cleanup_old_checkpoints()
            
            return results
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            
            # Save emergency checkpoint
            await self._save_emergency_checkpoint()
            
            raise
    
    async def _process_files_with_checkpoints(self, files: List[str], output_path: str,
                                            process_file_func) -> Dict[str, Any]:
        """Process files with regular checkpointing"""
        total_files = len(files)
        processed_count = 0
        
        for i, file_path in enumerate(files):
            try:
                # Process single file
                logger.debug(f"Processing file {i+1}/{total_files}: {file_path}")
                
                result = await process_file_func(file_path)
                
                # Track success
                self.state.processed_files.add(file_path)
                self.state.total_qa_pairs += result.get('qa_pairs_generated', 0)
                self.state.total_cost += result.get('cost', 0.0)
                
                # Update progress tracker if available
                if self.progress_tracker:
                    self.progress_tracker.complete_file_processing(
                        file_path,
                        result.get('chunks_created', 0),
                        result.get('qa_pairs_generated', 0),
                        result.get('qa_pairs_validated', 0),
                        result.get('cost', 0.0),
                        result.get('quality_score', 0.0)
                    )
                
                processed_count += 1
                self.files_since_checkpoint += 1
                
                # Save checkpoint if needed
                if self._should_save_checkpoint():
                    await self.save_checkpoint()
                
                logger.debug(f"Successfully processed {file_path}")
                
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                
                # Track failure
                self.state.failed_files.add(file_path)
                
                # Update progress tracker if available
                if self.progress_tracker:
                    self.progress_tracker.fail_file_processing(file_path, str(e))
                
                # Save checkpoint after failure
                await self.save_checkpoint()
                
                # Continue with next file (resilient processing)
                continue
        
        # Final checkpoint
        await self.save_checkpoint()
        
        return self._get_final_results()
    
    def _should_save_checkpoint(self) -> bool:
        """Check if it's time to save a checkpoint"""
        time_since_checkpoint = time.time() - self.last_checkpoint_time
        
        return (self.files_since_checkpoint >= self.checkpoint_interval_files) or \
               (time_since_checkpoint >= self.checkpoint_interval_minutes * 60)
    
    async def save_checkpoint(self, checkpoint_file: Optional[str] = None) -> str:
        """Save current state to checkpoint"""
        if checkpoint_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            checkpoint_file = str(self.checkpoint_dir / f"checkpoint_{timestamp}.json")
        
        try:
            # Prepare checkpoint data
            checkpoint_data = {
                'version': '1.0',
                'timestamp': time.time(),
                'processing_state': self.state.to_dict(),
                'config_hash': getattr(self.config, 'config_hash', 'unknown'),
                'checkpoint_metadata': {
                    'files_since_last_checkpoint': self.files_since_checkpoint,
                    'total_processed': len(self.state.processed_files),
                    'total_failed': len(self.state.failed_files),
                    'total_remaining': len(self.state.remaining_files)
                }
            }
            
            # Save checkpoint
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            # Update latest checkpoint symlink
            latest_file = self.checkpoint_dir / "latest_checkpoint.json"
            with open(latest_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            # Reset checkpoint counters
            self.last_checkpoint_time = time.time()
            self.files_since_checkpoint = 0
            self.state.last_checkpoint = checkpoint_file
            
            # Save progress tracker checkpoint if available
            if self.progress_tracker:
                progress_checkpoint = checkpoint_file.replace('checkpoint_', 'progress_checkpoint_')
                self.progress_tracker.save_checkpoint(progress_checkpoint)
            
            logger.info(f"Checkpoint saved: {checkpoint_file}")
            return checkpoint_file
            
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            raise
    
    async def load_checkpoint(self, checkpoint_file: str) -> None:
        """Load state from checkpoint"""
        try:
            with open(checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
            
            # Validate checkpoint version
            version = checkpoint_data.get('version', '1.0')
            if version != '1.0':
                logger.warning(f"Loading checkpoint with different version: {version}")
            
            # Load processing state
            state_data = checkpoint_data['processing_state']
            self.state.from_dict(state_data)
            
            # Update tracking
            self.last_checkpoint_time = checkpoint_data.get('timestamp', time.time())
            self.files_since_checkpoint = 0
            
            logger.info(f"Checkpoint loaded: {len(self.state.processed_files)} processed, "
                       f"{len(self.state.failed_files)} failed")
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint from {checkpoint_file}: {e}")
            raise
    
    async def _save_emergency_checkpoint(self) -> None:
        """Save emergency checkpoint on unexpected failure"""
        try:
            emergency_file = str(self.checkpoint_dir / f"emergency_checkpoint_{int(time.time())}.json")
            await self.save_checkpoint(emergency_file)
            logger.info(f"Emergency checkpoint saved: {emergency_file}")
        except Exception as e:
            logger.error(f"Failed to save emergency checkpoint: {e}")
    
    def _cleanup_old_checkpoints(self) -> None:
        """Clean up old checkpoint files"""
        try:
            checkpoint_files = list(self.checkpoint_dir.glob("checkpoint_*.json"))
            progress_files = list(self.checkpoint_dir.glob("progress_checkpoint_*.json"))
            
            # Keep only the most recent checkpoints
            if len(checkpoint_files) > self.max_checkpoint_files:
                # Sort by modification time and remove oldest
                checkpoint_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                for old_file in checkpoint_files[self.max_checkpoint_files:]:
                    old_file.unlink()
                    logger.debug(f"Removed old checkpoint: {old_file}")
            
            if len(progress_files) > self.max_checkpoint_files:
                progress_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                for old_file in progress_files[self.max_checkpoint_files:]:
                    old_file.unlink()
                    logger.debug(f"Removed old progress file: {old_file}")
            
        except Exception as e:
            logger.warning(f"Failed to cleanup old checkpoints: {e}")
    
    def _get_final_results(self) -> Dict[str, Any]:
        """Get final processing results"""
        elapsed_time = time.time() - self.state.start_time
        
        return {
            'success': True,
            'processing_summary': {
                'total_files': len(self.state.processed_files) + len(self.state.failed_files),
                'processed_files': len(self.state.processed_files),
                'failed_files': len(self.state.failed_files),
                'success_rate': len(self.state.processed_files) / max(1, len(self.state.processed_files) + len(self.state.failed_files)),
                'total_qa_pairs': self.state.total_qa_pairs,
                'total_cost': self.state.total_cost,
                'processing_time_seconds': elapsed_time,
                'processing_time_formatted': self._format_duration(elapsed_time)
            },
            'file_details': {
                'processed_files': list(self.state.processed_files),
                'failed_files': list(self.state.failed_files)
            },
            'checkpoint_info': {
                'last_checkpoint': self.state.last_checkpoint,
                'checkpoint_directory': str(self.checkpoint_dir)
            }
        }
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_resume_info(self) -> Dict[str, Any]:
        """Get information about resumable state"""
        latest_checkpoint = self.get_latest_checkpoint()
        
        if not latest_checkpoint:
            return {'has_checkpoint': False}
        
        try:
            with open(latest_checkpoint, 'r') as f:
                checkpoint_data = json.load(f)
            
            state_data = checkpoint_data['processing_state']
            
            return {
                'has_checkpoint': True,
                'checkpoint_file': latest_checkpoint,
                'checkpoint_timestamp': checkpoint_data.get('timestamp'),
                'processed_files': len(state_data.get('processed_files', [])),
                'failed_files': len(state_data.get('failed_files', [])),
                'remaining_files': len(state_data.get('remaining_files', [])),
                'total_qa_pairs': state_data.get('total_qa_pairs', 0),
                'total_cost': state_data.get('total_cost', 0.0)
            }
        
        except Exception as e:
            logger.error(f"Failed to read checkpoint info: {e}")
            return {'has_checkpoint': False, 'error': str(e)}
    
    def clear_checkpoints(self) -> None:
        """Clear all checkpoint files"""
        try:
            checkpoint_files = list(self.checkpoint_dir.glob("*.json"))
            
            for checkpoint_file in checkpoint_files:
                checkpoint_file.unlink()
                logger.debug(f"Removed checkpoint: {checkpoint_file}")
            
            logger.info(f"Cleared {len(checkpoint_files)} checkpoint files")
            
        except Exception as e:
            logger.error(f"Failed to clear checkpoints: {e}")
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get detailed processing statistics"""
        if not self.progress_tracker:
            return {'error': 'No progress tracker available'}
        
        return self.progress_tracker.get_status_summary()
