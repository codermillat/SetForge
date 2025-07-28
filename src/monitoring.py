"""
Production-grade cost management and monitoring for SetForge.
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import json


@dataclass
class CostBreakdown:
    """Detailed cost breakdown for transparency."""
    total_cost: float = 0.0
    cost_by_file: Dict[str, float] = field(default_factory=dict)
    cost_by_model: Dict[str, float] = field(default_factory=dict)
    total_tokens: int = 0
    total_requests: int = 0
    processing_time_seconds: float = 0.0
    cost_per_qa_pair: float = 0.0
    efficiency_score: float = 0.0


@dataclass
class PerformanceMetrics:
    """Performance tracking for optimization."""
    start_time: float = field(default_factory=time.time)
    files_processed: int = 0
    chunks_processed: int = 0
    qa_pairs_generated: int = 0
    qa_pairs_validated: int = 0
    api_calls_made: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_processing_time_per_file: float = 0.0
    validation_pass_rate: float = 0.0


class ProductionMonitor:
    """Production-grade monitoring and alerting system."""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.cost_breakdown = CostBreakdown()
        self.performance_metrics = PerformanceMetrics()
        self.alerts = []
        self._last_metrics_log = time.time()
    
    def track_cost(self, file_path: str, tokens_used: int, model_name: str, cost: float):
        """Track cost breakdown with detailed attribution."""
        self.cost_breakdown.total_cost += cost
        self.cost_breakdown.cost_by_file[file_path] = self.cost_breakdown.cost_by_file.get(file_path, 0) + cost
        self.cost_breakdown.cost_by_model[model_name] = self.cost_breakdown.cost_by_model.get(model_name, 0) + cost
        self.cost_breakdown.total_tokens += tokens_used
        self.cost_breakdown.total_requests += 1
        
        # Check budget alerts
        if self.cost_breakdown.total_cost >= self.config.cost.max_total_cost_usd * self.config.cost.cost_alert_threshold:
            self._add_alert('cost_warning', f"Cost {self.cost_breakdown.total_cost:.4f} approaching budget limit {self.config.cost.max_total_cost_usd}")
        
        if self.cost_breakdown.total_cost >= self.config.cost.max_total_cost_usd:
            self._add_alert('cost_exceeded', f"Cost {self.cost_breakdown.total_cost:.4f} exceeded budget {self.config.cost.max_total_cost_usd}")
    
    def track_performance(self, event: str, **kwargs):
        """Track performance metrics with contextual data."""
        current_time = time.time()
        
        if event == 'file_processed':
            self.performance_metrics.files_processed += 1
            processing_time = kwargs.get('processing_time', 0)
            self._update_avg_processing_time(processing_time)
            
            # Performance alert
            if processing_time > self.config.monitoring.performance_threshold_seconds:
                self._add_alert('performance_slow', f"File {kwargs.get('file_path', 'unknown')} took {processing_time:.2f}s to process")
        
        elif event == 'chunk_processed':
            self.performance_metrics.chunks_processed += 1
        
        elif event == 'qa_generated':
            self.performance_metrics.qa_pairs_generated += kwargs.get('count', 1)
        
        elif event == 'qa_validated':
            self.performance_metrics.qa_pairs_validated += kwargs.get('count', 1)
            self._update_validation_rate()
        
        elif event == 'api_call':
            self.performance_metrics.api_calls_made += 1
        
        elif event == 'cache_hit':
            self.performance_metrics.cache_hits += 1
        
        elif event == 'cache_miss':
            self.performance_metrics.cache_misses += 1
        
        # Log metrics periodically
        if self.config.monitoring.enable_metrics and (current_time - self._last_metrics_log) >= self.config.monitoring.metrics_interval_seconds:
            self._log_metrics()
            self._last_metrics_log = current_time
    
    def _update_avg_processing_time(self, new_time: float):
        """Update average processing time per file."""
        if self.performance_metrics.files_processed == 1:
            self.performance_metrics.avg_processing_time_per_file = new_time
        else:
            # Running average
            current_avg = self.performance_metrics.avg_processing_time_per_file
            n = self.performance_metrics.files_processed
            self.performance_metrics.avg_processing_time_per_file = ((current_avg * (n-1)) + new_time) / n
    
    def _update_validation_rate(self):
        """Update validation pass rate."""
        if self.performance_metrics.qa_pairs_generated > 0:
            self.performance_metrics.validation_pass_rate = (
                self.performance_metrics.qa_pairs_validated / self.performance_metrics.qa_pairs_generated
            )
    
    def _add_alert(self, alert_type: str, message: str):
        """Add alert with deduplication."""
        alert = {
            'type': alert_type,
            'message': message,
            'timestamp': time.time(),
            'config_hash': self.config.config_hash
        }
        
        # Deduplicate similar alerts
        if not any(a['type'] == alert_type and a['message'] == message for a in self.alerts[-5:]):
            self.alerts.append(alert)
            self.logger.warning(f"ALERT [{alert_type}]: {message}")
    
    def _log_metrics(self):
        """Log performance metrics in structured format."""
        metrics = {
            'files_processed': self.performance_metrics.files_processed,
            'chunks_processed': self.performance_metrics.chunks_processed,
            'qa_pairs_generated': self.performance_metrics.qa_pairs_generated,
            'qa_pairs_validated': self.performance_metrics.qa_pairs_validated,
            'validation_pass_rate': self.performance_metrics.validation_pass_rate,
            'api_calls_made': self.performance_metrics.api_calls_made,
            'cache_hit_rate': self._calculate_cache_hit_rate(),
            'avg_processing_time': self.performance_metrics.avg_processing_time_per_file,
            'total_cost': self.cost_breakdown.total_cost,
            'cost_efficiency': self._calculate_cost_efficiency(),
            'uptime_seconds': time.time() - self.performance_metrics.start_time
        }
        
        if self.config.monitoring.log_structured:
            # JSON logging for production
            self.logger.info(f"METRICS: {json.dumps(metrics)}")
        else:
            # Human-readable logging for development
            self.logger.info(f"Performance Metrics: {metrics}")
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total_cache_ops = self.performance_metrics.cache_hits + self.performance_metrics.cache_misses
        if total_cache_ops == 0:
            return 0.0
        return self.performance_metrics.cache_hits / total_cache_ops
    
    def _calculate_cost_efficiency(self) -> float:
        """Calculate cost efficiency (QA pairs per dollar)."""
        if self.cost_breakdown.total_cost == 0:
            return 0.0
        return self.performance_metrics.qa_pairs_validated / self.cost_breakdown.total_cost
    
    def should_continue_processing(self) -> bool:
        """Determine if processing should continue based on cost and performance."""
        # Check budget limits
        if self.cost_breakdown.total_cost >= self.config.cost.max_total_cost_usd:
            self.logger.error(f"Processing stopped: Budget exceeded (${self.cost_breakdown.total_cost:.4f})")
            return False
        
        # Check validation rate
        if (self.performance_metrics.qa_pairs_generated > 10 and 
            self.performance_metrics.validation_pass_rate < 0.1):
            self.logger.warning(f"Low validation rate: {self.performance_metrics.validation_pass_rate:.2%}")
            # Don't stop automatically, but log warning
        
        return True
    
    def get_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final report."""
        total_time = time.time() - self.performance_metrics.start_time
        
        # Calculate efficiency metrics
        self.cost_breakdown.processing_time_seconds = total_time
        if self.performance_metrics.qa_pairs_validated > 0:
            self.cost_breakdown.cost_per_qa_pair = self.cost_breakdown.total_cost / self.performance_metrics.qa_pairs_validated
        
        self.cost_breakdown.efficiency_score = self._calculate_cost_efficiency()
        
        report = {
            'summary': {
                'files_processed': self.performance_metrics.files_processed,
                'chunks_processed': self.performance_metrics.chunks_processed,
                'qa_pairs_generated': self.performance_metrics.qa_pairs_generated,
                'qa_pairs_validated': self.performance_metrics.qa_pairs_validated,
                'validation_pass_rate': self.performance_metrics.validation_pass_rate,
                'total_processing_time': total_time,
                'avg_time_per_file': self.performance_metrics.avg_processing_time_per_file
            },
            'cost_breakdown': {
                'total_cost_usd': self.cost_breakdown.total_cost,
                'cost_per_qa_pair': self.cost_breakdown.cost_per_qa_pair,
                'total_tokens': self.cost_breakdown.total_tokens,
                'total_api_requests': self.cost_breakdown.total_requests,
                'cost_by_file': dict(sorted(self.cost_breakdown.cost_by_file.items(), key=lambda x: x[1], reverse=True)[:10]),  # Top 10 most expensive files
                'cost_by_model': self.cost_breakdown.cost_by_model,
                'budget_utilization': self.cost_breakdown.total_cost / self.config.cost.max_total_cost_usd,
                'efficiency_score': self.cost_breakdown.efficiency_score
            },
            'performance_metrics': {
                'api_calls_made': self.performance_metrics.api_calls_made,
                'cache_hit_rate': self._calculate_cache_hit_rate(),
                'avg_processing_time_per_file': self.performance_metrics.avg_processing_time_per_file,
                'throughput_files_per_hour': (self.performance_metrics.files_processed / total_time) * 3600 if total_time > 0 else 0,
                'throughput_qa_pairs_per_hour': (self.performance_metrics.qa_pairs_validated / total_time) * 3600 if total_time > 0 else 0
            },
            'quality_metrics': {
                'validation_pass_rate': self.performance_metrics.validation_pass_rate,
                'avg_qa_pairs_per_chunk': self.performance_metrics.qa_pairs_generated / max(self.performance_metrics.chunks_processed, 1),
                'success_rate': self.performance_metrics.qa_pairs_validated / max(self.performance_metrics.qa_pairs_generated, 1)
            },
            'alerts': self.alerts,
            'config_hash': self.config.config_hash,
            'environment': self.config.environment,
            'timestamp': time.time()
        }
        
        return report
    
    def save_report(self, output_path: str):
        """Save final report to file."""
        report = self.get_final_report()
        
        report_path = Path(output_path).parent / f"setforge_report_{int(time.time())}.json"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Performance report saved to: {report_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save performance report: {e}")


class CostOptimizer:
    """Dynamic cost optimization strategies."""
    
    def __init__(self, config, monitor: ProductionMonitor):
        self.config = config
        self.monitor = monitor
        self.logger = logging.getLogger(__name__)
        self._optimization_applied = False
    
    def optimize_batch_size(self) -> int:
        """Dynamically optimize batch size based on performance."""
        current_batch_size = self.config.cost.batch_size
        
        # If we're processing slowly, reduce batch size
        if (self.monitor.performance_metrics.avg_processing_time_per_file > 60 and 
            current_batch_size > 3):
            optimized_size = max(current_batch_size - 2, 3)
            self.logger.info(f"Reducing batch size from {current_batch_size} to {optimized_size} due to slow processing")
            return optimized_size
        
        # If we're processing fast and under budget, increase batch size
        cache_hit_rate = self.monitor._calculate_cache_hit_rate()
        if (self.monitor.performance_metrics.avg_processing_time_per_file < 10 and 
            cache_hit_rate > 0.5 and 
            self.monitor.cost_breakdown.total_cost < self.config.cost.max_total_cost_usd * 0.5 and
            current_batch_size < 20):
            optimized_size = min(current_batch_size + 3, 20)
            self.logger.info(f"Increasing batch size from {current_batch_size} to {optimized_size} due to good performance")
            return optimized_size
        
        return current_batch_size
    
    def should_enable_aggressive_caching(self) -> bool:
        """Determine if aggressive caching should be enabled."""
        validation_rate = self.monitor.performance_metrics.validation_pass_rate
        cost_utilization = self.monitor.cost_breakdown.total_cost / self.config.cost.max_total_cost_usd
        
        # Enable aggressive caching if validation rate is high and we're using budget efficiently
        return validation_rate > 0.8 and cost_utilization < 0.7
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations based on current performance."""
        recommendations = []
        
        cache_hit_rate = self.monitor._calculate_cache_hit_rate()
        validation_rate = self.monitor.performance_metrics.validation_pass_rate
        cost_efficiency = self.monitor._calculate_cost_efficiency()
        
        if cache_hit_rate < 0.3:
            recommendations.append("Consider enabling more aggressive caching to improve performance")
        
        if validation_rate < 0.5:
            recommendations.append("Validation rate is low - consider adjusting validation thresholds")
        
        if cost_efficiency < 10:  # Less than 10 QA pairs per dollar
            recommendations.append("Cost efficiency is low - consider optimizing chunk sizes or model selection")
        
        if self.monitor.performance_metrics.avg_processing_time_per_file > 120:
            recommendations.append("Processing is slow - consider reducing batch size or enabling parallel processing")
        
        return recommendations
