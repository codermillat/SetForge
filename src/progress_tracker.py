"""
Comprehensive Progress Tracking System for SetForge
Provides real-time monitoring, metrics calculation, and status tracking
"""

import time
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from pathlib import Path
import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class FileProgress:
    """Progress information for a single file"""
    file_path: str
    status: str = "pending"  # pending, processing, completed, failed
    chunks_created: int = 0
    qa_pairs_generated: int = 0
    qa_pairs_validated: int = 0
    processing_time: float = 0.0
    cost: float = 0.0
    quality_score: float = 0.0
    error_message: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None


@dataclass
class ProcessingMetrics:
    """Comprehensive processing metrics"""
    files_processed: int = 0
    files_failed: int = 0
    total_chunks: int = 0
    total_qa_pairs: int = 0
    total_validated_qa_pairs: int = 0
    total_cost: float = 0.0
    average_quality_score: float = 0.0
    processing_speed_files_per_min: float = 0.0
    processing_speed_qa_per_min: float = 0.0
    validation_pass_rate: float = 0.0
    cost_per_qa_pair: float = 0.0
    estimated_time_remaining: float = 0.0


@dataclass
class QualityMetrics:
    """Quality tracking metrics"""
    total_qa_pairs: int = 0
    quality_scores: List[float] = None
    validation_scores: List[float] = None
    hallucination_detections: int = 0
    relevancy_scores: List[float] = None
    source_overlap_scores: List[float] = None
    
    def __post_init__(self):
        if self.quality_scores is None:
            self.quality_scores = []
        if self.validation_scores is None:
            self.validation_scores = []
        if self.relevancy_scores is None:
            self.relevancy_scores = []
        if self.source_overlap_scores is None:
            self.source_overlap_scores = []


class ProgressTracker:
    """
    Comprehensive progress tracking system with real-time monitoring,
    metrics calculation, and persistence for resumability.
    """
    
    def __init__(self, total_files: int, config: Any, checkpoint_dir: str = "output/checkpoints"):
        self.total_files = total_files
        self.config = config
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Progress state
        self.start_time = time.time()
        self.current_file_index = 0
        self.current_file: Optional[str] = None
        self.file_progress: Dict[str, FileProgress] = {}
        
        # Metrics
        self.metrics = ProcessingMetrics()
        self.quality_metrics = QualityMetrics()
        
        # Tracking
        self.last_update_time = time.time()
        self.update_interval = getattr(config.progress, 'status_refresh_rate', 2.0)
        self.checkpoint_interval_files = getattr(config.progress, 'checkpoint_interval_files', 5)
        self.checkpoint_interval_minutes = getattr(config.progress, 'checkpoint_interval_minutes', 10)
        self.last_checkpoint_time = time.time()
        
        # Performance tracking
        self.recent_processing_times: List[float] = []
        self.recent_qa_counts: List[int] = []
        self.max_recent_samples = 10
        
        logger.info(f"ProgressTracker initialized for {total_files} files")
    
    def start_file_processing(self, file_path: str) -> None:
        """Mark a file as started processing"""
        self.current_file = file_path
        self.current_file_index += 1
        
        if file_path not in self.file_progress:
            self.file_progress[file_path] = FileProgress(file_path=file_path)
        
        self.file_progress[file_path].status = "processing"
        self.file_progress[file_path].start_time = time.time()
        
        logger.debug(f"Started processing file {self.current_file_index}/{self.total_files}: {file_path}")
    
    def complete_file_processing(self, file_path: str, chunks_created: int, 
                                qa_pairs_generated: int, qa_pairs_validated: int,
                                cost: float, quality_score: float) -> None:
        """Mark a file as completed with results"""
        if file_path not in self.file_progress:
            self.file_progress[file_path] = FileProgress(file_path=file_path)
        
        progress = self.file_progress[file_path]
        progress.status = "completed"
        progress.end_time = time.time()
        progress.chunks_created = chunks_created
        progress.qa_pairs_generated = qa_pairs_generated
        progress.qa_pairs_validated = qa_pairs_validated
        progress.cost = cost
        progress.quality_score = quality_score
        
        if progress.start_time:
            progress.processing_time = progress.end_time - progress.start_time
            
            # Update recent performance tracking
            self.recent_processing_times.append(progress.processing_time)
            self.recent_qa_counts.append(qa_pairs_generated)
            
            # Keep only recent samples
            if len(self.recent_processing_times) > self.max_recent_samples:
                self.recent_processing_times.pop(0)
                self.recent_qa_counts.pop(0)
        
        # Update overall metrics
        self._update_metrics()
        
        logger.debug(f"Completed processing {file_path}: {qa_pairs_generated} QA pairs, quality {quality_score:.3f}")
    
    def fail_file_processing(self, file_path: str, error_message: str) -> None:
        """Mark a file as failed with error"""
        if file_path not in self.file_progress:
            self.file_progress[file_path] = FileProgress(file_path=file_path)
        
        progress = self.file_progress[file_path]
        progress.status = "failed"
        progress.end_time = time.time()
        progress.error_message = error_message
        
        if progress.start_time:
            progress.processing_time = progress.end_time - progress.start_time
        
        self._update_metrics()
        
        logger.warning(f"Failed processing {file_path}: {error_message}")
    
    def update_quality_metrics(self, validation_score: float, relevancy_score: float, 
                              source_overlap_score: float, is_hallucination: bool = False) -> None:
        """Update quality tracking metrics"""
        self.quality_metrics.total_qa_pairs += 1
        self.quality_metrics.validation_scores.append(validation_score)
        self.quality_metrics.relevancy_scores.append(relevancy_score)
        self.quality_metrics.source_overlap_scores.append(source_overlap_score)
        
        if is_hallucination:
            self.quality_metrics.hallucination_detections += 1
        
        # Calculate overall quality score
        overall_quality = (validation_score * 0.4 + relevancy_score * 0.3 + source_overlap_score * 0.3)
        self.quality_metrics.quality_scores.append(overall_quality)
    
    def _update_metrics(self) -> None:
        """Update calculated metrics based on current progress"""
        completed_files = [p for p in self.file_progress.values() if p.status == "completed"]
        failed_files = [p for p in self.file_progress.values() if p.status == "failed"]
        
        self.metrics.files_processed = len(completed_files)
        self.metrics.files_failed = len(failed_files)
        
        if completed_files:
            self.metrics.total_chunks = sum(p.chunks_created for p in completed_files)
            self.metrics.total_qa_pairs = sum(p.qa_pairs_generated for p in completed_files)
            self.metrics.total_validated_qa_pairs = sum(p.qa_pairs_validated for p in completed_files)
            self.metrics.total_cost = sum(p.cost for p in completed_files)
            
            # Calculate averages
            if self.metrics.files_processed > 0:
                self.metrics.average_quality_score = sum(p.quality_score for p in completed_files) / self.metrics.files_processed
            
            # Calculate validation pass rate
            if self.metrics.total_qa_pairs > 0:
                self.metrics.validation_pass_rate = self.metrics.total_validated_qa_pairs / self.metrics.total_qa_pairs
            
            # Calculate cost per QA pair
            if self.metrics.total_validated_qa_pairs > 0:
                self.metrics.cost_per_qa_pair = self.metrics.total_cost / self.metrics.total_validated_qa_pairs
        
        # Calculate processing speeds
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            self.metrics.processing_speed_files_per_min = (self.metrics.files_processed / elapsed_time) * 60
            self.metrics.processing_speed_qa_per_min = (self.metrics.total_qa_pairs / elapsed_time) * 60
            
            # Estimate time remaining
            if self.metrics.files_processed > 0:
                avg_time_per_file = elapsed_time / self.metrics.files_processed
                remaining_files = self.total_files - self.metrics.files_processed
                self.metrics.estimated_time_remaining = remaining_files * avg_time_per_file
    
    def get_progress_percentage(self) -> float:
        """Get overall progress percentage"""
        return (self.metrics.files_processed / self.total_files) * 100 if self.total_files > 0 else 0
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary"""
        elapsed_time = time.time() - self.start_time
        
        # Recent performance
        recent_speed = 0.0
        if self.recent_processing_times and len(self.recent_processing_times) > 1:
            recent_avg_time = sum(self.recent_processing_times[-5:]) / min(5, len(self.recent_processing_times))
            if recent_avg_time > 0:
                recent_speed = 60 / recent_avg_time  # files per minute
        
        return {
            'progress': {
                'files_completed': self.metrics.files_processed,
                'files_failed': self.metrics.files_failed,
                'files_remaining': self.total_files - self.metrics.files_processed - self.metrics.files_failed,
                'total_files': self.total_files,
                'percentage': self.get_progress_percentage(),
                'current_file': self.current_file,
                'current_file_index': self.current_file_index
            },
            'performance': {
                'elapsed_time_seconds': elapsed_time,
                'elapsed_time_formatted': self._format_duration(elapsed_time),
                'estimated_remaining_seconds': self.metrics.estimated_time_remaining,
                'estimated_remaining_formatted': self._format_duration(self.metrics.estimated_time_remaining),
                'files_per_minute': self.metrics.processing_speed_files_per_min,
                'qa_pairs_per_minute': self.metrics.processing_speed_qa_per_min,
                'recent_files_per_minute': recent_speed
            },
            'qa_metrics': {
                'total_qa_pairs': self.metrics.total_qa_pairs,
                'validated_qa_pairs': self.metrics.total_validated_qa_pairs,
                'validation_pass_rate': self.metrics.validation_pass_rate,
                'average_quality_score': self.metrics.average_quality_score
            },
            'cost_metrics': {
                'total_cost': self.metrics.total_cost,
                'cost_per_qa_pair': self.metrics.cost_per_qa_pair,
                'estimated_final_cost': self._estimate_final_cost()
            },
            'quality_metrics': self._get_quality_summary()
        }
    
    def _get_quality_summary(self) -> Dict[str, Any]:
        """Get quality metrics summary"""
        if not self.quality_metrics.quality_scores:
            return {'no_data': True}
        
        quality_scores = self.quality_metrics.quality_scores
        validation_scores = self.quality_metrics.validation_scores
        relevancy_scores = self.quality_metrics.relevancy_scores
        source_overlap_scores = self.quality_metrics.source_overlap_scores
        
        return {
            'total_qa_pairs': self.quality_metrics.total_qa_pairs,
            'average_quality_score': sum(quality_scores) / len(quality_scores),
            'average_validation_score': sum(validation_scores) / len(validation_scores),
            'average_relevancy_score': sum(relevancy_scores) / len(relevancy_scores),
            'average_source_overlap_score': sum(source_overlap_scores) / len(source_overlap_scores),
            'hallucination_rate': self.quality_metrics.hallucination_detections / max(1, self.quality_metrics.total_qa_pairs),
            'quality_distribution': self._calculate_quality_distribution(quality_scores)
        }
    
    def _calculate_quality_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate distribution of quality scores"""
        if not scores:
            return {}
        
        distribution = {
            'excellent': len([s for s in scores if s >= 0.9]),
            'good': len([s for s in scores if 0.8 <= s < 0.9]),
            'fair': len([s for s in scores if 0.7 <= s < 0.8]),
            'poor': len([s for s in scores if s < 0.7])
        }
        return distribution
    
    def _estimate_final_cost(self) -> float:
        """Estimate final cost based on current progress"""
        if self.metrics.files_processed == 0:
            return 0.0
        
        avg_cost_per_file = self.metrics.total_cost / self.metrics.files_processed
        return avg_cost_per_file * self.total_files
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds <= 0:
            return "0s"
        
        td = timedelta(seconds=int(seconds))
        parts = []
        
        if td.days > 0:
            parts.append(f"{td.days}d")
        
        hours, remainder = divmod(td.seconds, 3600)
        if hours > 0:
            parts.append(f"{hours}h")
        
        minutes, seconds = divmod(remainder, 60)
        if minutes > 0:
            parts.append(f"{minutes}m")
        
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")
        
        return " ".join(parts)
    
    def should_save_checkpoint(self) -> bool:
        """Check if it's time to save a checkpoint"""
        time_since_checkpoint = time.time() - self.last_checkpoint_time
        files_since_checkpoint = self.metrics.files_processed % self.checkpoint_interval_files
        
        return (files_since_checkpoint == 0 and self.metrics.files_processed > 0) or \
               (time_since_checkpoint >= self.checkpoint_interval_minutes * 60)
    
    def get_checkpoint_data(self) -> Dict[str, Any]:
        """Get data for checkpoint saving"""
        return {
            'version': '1.0',
            'timestamp': time.time(),
            'total_files': self.total_files,
            'current_file_index': self.current_file_index,
            'current_file': self.current_file,
            'start_time': self.start_time,
            'file_progress': {path: asdict(progress) for path, progress in self.file_progress.items()},
            'metrics': asdict(self.metrics),
            'quality_metrics': asdict(self.quality_metrics),
            'recent_processing_times': self.recent_processing_times,
            'recent_qa_counts': self.recent_qa_counts
        }
    
    def load_checkpoint_data(self, checkpoint_data: Dict[str, Any]) -> None:
        """Load data from checkpoint"""
        try:
            self.total_files = checkpoint_data['total_files']
            self.current_file_index = checkpoint_data['current_file_index']
            self.current_file = checkpoint_data['current_file']
            self.start_time = checkpoint_data['start_time']
            
            # Restore file progress
            self.file_progress = {}
            for path, progress_data in checkpoint_data['file_progress'].items():
                self.file_progress[path] = FileProgress(**progress_data)
            
            # Restore metrics
            self.metrics = ProcessingMetrics(**checkpoint_data['metrics'])
            self.quality_metrics = QualityMetrics(**checkpoint_data['quality_metrics'])
            
            # Restore performance tracking
            self.recent_processing_times = checkpoint_data.get('recent_processing_times', [])
            self.recent_qa_counts = checkpoint_data.get('recent_qa_counts', [])
            
            logger.info(f"Checkpoint loaded: {self.metrics.files_processed}/{self.total_files} files processed")
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint data: {e}")
            raise
    
    def save_checkpoint(self, checkpoint_file: Optional[str] = None) -> str:
        """Save current progress to checkpoint file"""
        if checkpoint_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            checkpoint_file = str(self.checkpoint_dir / f"progress_checkpoint_{timestamp}.json")
        
        try:
            checkpoint_data = self.get_checkpoint_data()
            
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            # Also save as latest checkpoint
            latest_file = str(self.checkpoint_dir / "latest_progress.json")
            with open(latest_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            self.last_checkpoint_time = time.time()
            
            logger.info(f"Progress checkpoint saved: {checkpoint_file}")
            return checkpoint_file
            
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            raise
    
    def load_checkpoint(self, checkpoint_file: str) -> None:
        """Load progress from checkpoint file"""
        try:
            with open(checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
            
            self.load_checkpoint_data(checkpoint_data)
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint from {checkpoint_file}: {e}")
            raise
    
    def get_processed_files(self) -> List[str]:
        """Get list of successfully processed files"""
        return [path for path, progress in self.file_progress.items() 
                if progress.status == "completed"]
    
    def get_failed_files(self) -> List[str]:
        """Get list of failed files"""
        return [path for path, progress in self.file_progress.items() 
                if progress.status == "failed"]
    
    def get_remaining_files(self, all_files: List[str]) -> List[str]:
        """Get list of files still to be processed"""
        processed_and_failed = set(self.get_processed_files() + self.get_failed_files())
        return [f for f in all_files if f not in processed_and_failed]
    
    def generate_progress_report(self) -> Dict[str, Any]:
        """Generate comprehensive progress report"""
        status = self.get_status_summary()
        
        # Add detailed file information
        file_details = []
        for file_path, progress in self.file_progress.items():
            file_details.append({
                'file_path': file_path,
                'status': progress.status,
                'qa_pairs_generated': progress.qa_pairs_generated,
                'qa_pairs_validated': progress.qa_pairs_validated,
                'processing_time': progress.processing_time,
                'cost': progress.cost,
                'quality_score': progress.quality_score,
                'error_message': progress.error_message
            })
        
        return {
            'report_timestamp': datetime.now().isoformat(),
            'summary': status,
            'file_details': file_details,
            'configuration': {
                'total_files': self.total_files,
                'checkpoint_interval_files': self.checkpoint_interval_files,
                'checkpoint_interval_minutes': self.checkpoint_interval_minutes
            }
        }
