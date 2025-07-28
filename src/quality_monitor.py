"""
Enhanced Quality Assurance System for SetForge
Provides real-time quality tracking, monitoring, and alerts
"""

import time
import json
import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
import statistics

logger = logging.getLogger(__name__)


@dataclass
class QualityAlert:
    """Represents a quality alert"""
    timestamp: float
    alert_type: str  # 'low_quality', 'hallucination', 'validation_failure', 'trend_decline'
    severity: str   # 'low', 'medium', 'high', 'critical'
    message: str
    file_path: Optional[str] = None
    qa_pair_id: Optional[str] = None
    metrics: Optional[Dict[str, float]] = None


@dataclass
class QualityTrend:
    """Quality trend information"""
    time_window_minutes: int
    samples_count: int
    average_score: float
    trend_direction: str  # 'improving', 'declining', 'stable'
    slope: float
    confidence: float


@dataclass
class ValidationMetrics:
    """Detailed validation metrics"""
    extractive_score: float = 0.0
    relevancy_score: float = 0.0
    source_overlap_score: float = 0.0
    coherence_score: float = 0.0
    hallucination_detected: bool = False
    validation_time: float = 0.0
    error_flags: List[str] = None
    
    def __post_init__(self):
        if self.error_flags is None:
            self.error_flags = []


class QualityMonitor:
    """
    Comprehensive quality monitoring system with real-time tracking,
    alerts, trend analysis, and detailed reporting.
    """
    
    def __init__(self, config: Any, output_dir: str = "output/quality"):
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Quality tracking
        self.quality_history: List[Tuple[float, ValidationMetrics]] = []
        self.quality_alerts: List[QualityAlert] = []
        self.file_quality_scores: Dict[str, List[float]] = {}
        
        # Configuration
        self.alert_threshold = getattr(config.quality, 'alert_threshold', 0.8)
        self.quality_report_interval = getattr(config.quality, 'quality_report_interval', 100)
        self.enable_quality_trends = getattr(config.quality, 'enable_quality_trends', True)
        self.track_validation_details = getattr(config.quality, 'track_validation_details', True)
        self.trend_window_minutes = getattr(config.quality, 'trend_window_minutes', 10)
        self.min_samples_for_trend = getattr(config.quality, 'min_samples_for_trend', 10)
        
        # Thresholds
        self.quality_thresholds = {
            'excellent': getattr(config.validation, 'excellent_threshold', 0.9),
            'good': getattr(config.validation, 'good_threshold', 0.8),
            'fair': getattr(config.validation, 'fair_threshold', 0.7),
            'poor': getattr(config.validation, 'poor_threshold', 0.0)
        }
        
        # Performance tracking
        self.qa_pairs_processed = 0
        self.quality_checks_performed = 0
        self.alerts_generated = 0
        self.last_report_time = time.time()
        
        logger.info(f"QualityMonitor initialized with threshold {self.alert_threshold}")
    
    async def monitor_qa_quality(self, qa_pair: Any, validation_result: Any, 
                               file_path: Optional[str] = None) -> Dict[str, Any]:
        """Monitor quality of a QA pair and generate alerts if needed"""
        timestamp = time.time()
        
        # Extract validation metrics
        metrics = self._extract_validation_metrics(validation_result)
        
        # Calculate overall quality score
        overall_score = self._calculate_overall_quality_score(metrics)
        
        # Track quality history
        self.quality_history.append((timestamp, metrics))
        
        # Track file-specific quality
        if file_path:
            if file_path not in self.file_quality_scores:
                self.file_quality_scores[file_path] = []
            self.file_quality_scores[file_path].append(overall_score)
        
        # Check for quality alerts
        alerts = await self._check_quality_alerts(qa_pair, metrics, overall_score, file_path)
        
        # Update counters
        self.qa_pairs_processed += 1
        self.quality_checks_performed += 1
        
        # Generate periodic reports
        if self._should_generate_report():
            await self._generate_quality_report()
        
        # Return quality assessment
        return {
            'overall_score': overall_score,
            'metrics': asdict(metrics),
            'quality_level': self._get_quality_level(overall_score),
            'alerts': [asdict(alert) for alert in alerts],
            'trends': self._get_current_trends() if self.enable_quality_trends else None
        }
    
    def _extract_validation_metrics(self, validation_result: Any) -> ValidationMetrics:
        """Extract detailed metrics from validation result"""
        metrics = ValidationMetrics()
        
        try:
            # Extract core validation scores
            if hasattr(validation_result, 'extractive_score'):
                metrics.extractive_score = validation_result.extractive_score
            elif hasattr(validation_result, 'source_overlap'):
                metrics.extractive_score = validation_result.source_overlap
            
            if hasattr(validation_result, 'relevancy_score'):
                metrics.relevancy_score = validation_result.relevancy_score
            
            if hasattr(validation_result, 'source_overlap_score'):
                metrics.source_overlap_score = validation_result.source_overlap_score
            elif hasattr(validation_result, 'source_overlap'):
                metrics.source_overlap_score = validation_result.source_overlap
            
            # Check for hallucination detection
            if hasattr(validation_result, 'hallucination_detected'):
                metrics.hallucination_detected = validation_result.hallucination_detected
            elif hasattr(validation_result, 'is_hallucination'):
                metrics.hallucination_detected = validation_result.is_hallucination
            
            # Extract validation time if available
            if hasattr(validation_result, 'validation_time'):
                metrics.validation_time = validation_result.validation_time
            
            # Extract error flags
            if hasattr(validation_result, 'errors'):
                metrics.error_flags = validation_result.errors
            elif hasattr(validation_result, 'warnings'):
                metrics.error_flags = validation_result.warnings
            
            # Calculate coherence score if not directly available
            if not metrics.coherence_score and hasattr(validation_result, 'quality_score'):
                metrics.coherence_score = validation_result.quality_score
            
        except Exception as e:
            logger.warning(f"Failed to extract validation metrics: {e}")
            metrics.error_flags.append(f"metrics_extraction_error: {e}")
        
        return metrics
    
    def _calculate_overall_quality_score(self, metrics: ValidationMetrics) -> float:
        """Calculate overall quality score from individual metrics"""
        # Weighted scoring based on importance
        weights = {
            'extractive': 0.4,      # Most important: must be extractive
            'relevancy': 0.3,       # Important: semantic relevancy
            'source_overlap': 0.2,  # Important: source accuracy
            'coherence': 0.1        # Nice to have: readability
        }
        
        score = (
            metrics.extractive_score * weights['extractive'] +
            metrics.relevancy_score * weights['relevancy'] +
            metrics.source_overlap_score * weights['source_overlap'] +
            metrics.coherence_score * weights['coherence']
        )
        
        # Apply penalty for hallucination
        if metrics.hallucination_detected:
            score *= 0.5  # Heavy penalty for hallucination
        
        # Apply penalty for errors
        if metrics.error_flags:
            error_penalty = min(0.2, len(metrics.error_flags) * 0.05)
            score *= (1.0 - error_penalty)
        
        return max(0.0, min(1.0, score))
    
    def _get_quality_level(self, score: float) -> str:
        """Get quality level description for score"""
        if score >= self.quality_thresholds['excellent']:
            return 'excellent'
        elif score >= self.quality_thresholds['good']:
            return 'good'
        elif score >= self.quality_thresholds['fair']:
            return 'fair'
        else:
            return 'poor'
    
    async def _check_quality_alerts(self, qa_pair: Any, metrics: ValidationMetrics, 
                                  overall_score: float, file_path: Optional[str]) -> List[QualityAlert]:
        """Check for quality issues and generate alerts"""
        alerts = []
        current_time = time.time()
        
        # Low quality alert
        if overall_score < self.alert_threshold:
            severity = 'critical' if overall_score < 0.5 else 'high' if overall_score < 0.7 else 'medium'
            
            alert = QualityAlert(
                timestamp=current_time,
                alert_type='low_quality',
                severity=severity,
                message=f"Low quality QA pair detected: score {overall_score:.3f}",
                file_path=file_path,
                qa_pair_id=getattr(qa_pair, 'id', None),
                metrics={'overall_score': overall_score}
            )
            alerts.append(alert)
        
        # Hallucination alert
        if metrics.hallucination_detected:
            alert = QualityAlert(
                timestamp=current_time,
                alert_type='hallucination',
                severity='critical',
                message="Hallucination detected in QA pair",
                file_path=file_path,
                qa_pair_id=getattr(qa_pair, 'id', None),
                metrics={'extractive_score': metrics.extractive_score}
            )
            alerts.append(alert)
        
        # Validation failure alert
        if metrics.error_flags:
            alert = QualityAlert(
                timestamp=current_time,
                alert_type='validation_failure',
                severity='medium',
                message=f"Validation errors: {', '.join(metrics.error_flags)}",
                file_path=file_path,
                qa_pair_id=getattr(qa_pair, 'id', None),
                metrics={'error_count': len(metrics.error_flags)}
            )
            alerts.append(alert)
        
        # Trend decline alert
        if self.enable_quality_trends:
            trend_alert = self._check_trend_alerts(current_time, overall_score)
            if trend_alert:
                alerts.append(trend_alert)
        
        # Store alerts
        self.quality_alerts.extend(alerts)
        self.alerts_generated += len(alerts)
        
        # Log critical alerts
        for alert in alerts:
            if alert.severity in ['critical', 'high']:
                logger.warning(f"Quality Alert: {alert.message}")
        
        return alerts
    
    def _check_trend_alerts(self, current_time: float, current_score: float) -> Optional[QualityAlert]:
        """Check for declining quality trends"""
        if len(self.quality_history) < self.min_samples_for_trend:
            return None
        
        # Get recent quality scores
        cutoff_time = current_time - (self.trend_window_minutes * 60)
        recent_scores = [
            score for timestamp, metrics in self.quality_history 
            if timestamp >= cutoff_time
            for score in [self._calculate_overall_quality_score(metrics)]
        ]
        
        if len(recent_scores) < self.min_samples_for_trend:
            return None
        
        # Calculate trend
        trend = self._calculate_quality_trend(recent_scores)
        
        # Check for significant decline
        if trend.trend_direction == 'declining' and trend.slope < -0.01 and trend.confidence > 0.7:
            return QualityAlert(
                timestamp=current_time,
                alert_type='trend_decline',
                severity='medium',
                message=f"Quality trend declining: {trend.slope:.4f} per sample over {self.trend_window_minutes}min",
                metrics={
                    'trend_slope': trend.slope,
                    'trend_confidence': trend.confidence,
                    'samples_count': trend.samples_count
                }
            )
        
        return None
    
    def _calculate_quality_trend(self, scores: List[float]) -> QualityTrend:
        """Calculate quality trend from recent scores"""
        if len(scores) < 2:
            return QualityTrend(
                time_window_minutes=self.trend_window_minutes,
                samples_count=len(scores),
                average_score=scores[0] if scores else 0.0,
                trend_direction='stable',
                slope=0.0,
                confidence=0.0
            )
        
        # Calculate linear regression slope
        x_values = list(range(len(scores)))
        n = len(scores)
        
        sum_x = sum(x_values)
        sum_y = sum(scores)
        sum_xy = sum(x * y for x, y in zip(x_values, scores))
        sum_x2 = sum(x * x for x in x_values)
        
        # Linear regression slope
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Calculate correlation coefficient for confidence
        mean_x = sum_x / n
        mean_y = sum_y / n
        
        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, scores))
        denominator_x = sum((x - mean_x) ** 2 for x in x_values)
        denominator_y = sum((y - mean_y) ** 2 for y in scores)
        
        correlation = numerator / (denominator_x * denominator_y) ** 0.5 if denominator_x * denominator_y > 0 else 0
        confidence = abs(correlation)
        
        # Determine trend direction
        if abs(slope) < 0.001:
            direction = 'stable'
        elif slope > 0:
            direction = 'improving'
        else:
            direction = 'declining'
        
        return QualityTrend(
            time_window_minutes=self.trend_window_minutes,
            samples_count=n,
            average_score=mean_y,
            trend_direction=direction,
            slope=slope,
            confidence=confidence
        )
    
    def _get_current_trends(self) -> Dict[str, Any]:
        """Get current quality trends"""
        if len(self.quality_history) < self.min_samples_for_trend:
            return {'insufficient_data': True}
        
        # Get recent scores
        current_time = time.time()
        cutoff_time = current_time - (self.trend_window_minutes * 60)
        
        recent_scores = [
            self._calculate_overall_quality_score(metrics)
            for timestamp, metrics in self.quality_history 
            if timestamp >= cutoff_time
        ]
        
        if not recent_scores:
            return {'no_recent_data': True}
        
        trend = self._calculate_quality_trend(recent_scores)
        
        return {
            'trend_direction': trend.trend_direction,
            'slope': trend.slope,
            'confidence': trend.confidence,
            'average_score': trend.average_score,
            'samples_count': trend.samples_count,
            'time_window_minutes': trend.time_window_minutes
        }
    
    def _should_generate_report(self) -> bool:
        """Check if it's time to generate a quality report"""
        return (self.qa_pairs_processed % self.quality_report_interval == 0) or \
               (time.time() - self.last_report_time > 300)  # Every 5 minutes max
    
    async def _generate_quality_report(self) -> None:
        """Generate periodic quality report"""
        try:
            report = self.generate_quality_report()
            
            # Save report to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.output_dir / f"quality_report_{timestamp}.json"
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.last_report_time = time.time()
            
            logger.info(f"Quality report generated: {report_file}")
            
        except Exception as e:
            logger.error(f"Failed to generate quality report: {e}")
    
    def generate_quality_report(self) -> Dict[str, Any]:
        """Generate comprehensive quality analysis report"""
        current_time = time.time()
        
        # Calculate overall statistics
        all_scores = [
            self._calculate_overall_quality_score(metrics)
            for _, metrics in self.quality_history
        ]
        
        if not all_scores:
            return {
                'timestamp': current_time,
                'status': 'no_data',
                'message': 'No quality data available yet'
            }
        
        # Basic statistics
        avg_score = statistics.mean(all_scores)
        median_score = statistics.median(all_scores)
        std_dev = statistics.stdev(all_scores) if len(all_scores) > 1 else 0.0
        
        # Quality distribution
        distribution = {
            'excellent': len([s for s in all_scores if s >= self.quality_thresholds['excellent']]),
            'good': len([s for s in all_scores if self.quality_thresholds['good'] <= s < self.quality_thresholds['excellent']]),
            'fair': len([s for s in all_scores if self.quality_thresholds['fair'] <= s < self.quality_thresholds['good']]),
            'poor': len([s for s in all_scores if s < self.quality_thresholds['fair']])
        }
        
        # Calculate hallucination rate
        hallucination_count = sum(1 for _, metrics in self.quality_history if metrics.hallucination_detected)
        hallucination_rate = hallucination_count / len(self.quality_history) if self.quality_history else 0.0
        
        # Alert statistics
        alert_counts = {}
        for alert in self.quality_alerts:
            alert_counts[alert.alert_type] = alert_counts.get(alert.alert_type, 0) + 1
        
        # File-specific quality scores
        file_quality = {}
        for file_path, scores in self.file_quality_scores.items():
            if scores:
                file_quality[file_path] = {
                    'average_score': statistics.mean(scores),
                    'score_count': len(scores),
                    'min_score': min(scores),
                    'max_score': max(scores)
                }
        
        return {
            'timestamp': current_time,
            'report_generated_at': datetime.now().isoformat(),
            'summary': {
                'total_qa_pairs_analyzed': len(all_scores),
                'average_quality_score': avg_score,
                'median_quality_score': median_score,
                'quality_std_deviation': std_dev,
                'hallucination_rate': hallucination_rate,
                'total_alerts': len(self.quality_alerts),
                'alerts_by_type': alert_counts
            },
            'quality_distribution': distribution,
            'quality_percentages': {
                'excellent': (distribution['excellent'] / len(all_scores)) * 100,
                'good': (distribution['good'] / len(all_scores)) * 100,
                'fair': (distribution['fair'] / len(all_scores)) * 100,
                'poor': (distribution['poor'] / len(all_scores)) * 100
            },
            'detailed_metrics': {
                'average_extractive_score': statistics.mean([m.extractive_score for _, m in self.quality_history]),
                'average_relevancy_score': statistics.mean([m.relevancy_score for _, m in self.quality_history]),
                'average_source_overlap_score': statistics.mean([m.source_overlap_score for _, m in self.quality_history]),
                'average_coherence_score': statistics.mean([m.coherence_score for _, m in self.quality_history]),
                'average_validation_time': statistics.mean([m.validation_time for _, m in self.quality_history if m.validation_time > 0])
            },
            'trends': self._get_current_trends() if self.enable_quality_trends else None,
            'file_quality_analysis': file_quality,
            'recent_alerts': [asdict(alert) for alert in self.quality_alerts[-10:]],  # Last 10 alerts
            'configuration': {
                'alert_threshold': self.alert_threshold,
                'quality_thresholds': self.quality_thresholds,
                'trend_window_minutes': self.trend_window_minutes
            }
        }
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """Get quick quality summary for dashboard"""
        if not self.quality_history:
            return {'status': 'no_data'}
        
        recent_scores = [
            self._calculate_overall_quality_score(metrics)
            for _, metrics in self.quality_history[-20:]  # Last 20 QA pairs
        ]
        
        current_avg = statistics.mean(recent_scores) if recent_scores else 0.0
        
        return {
            'current_average_quality': current_avg,
            'quality_level': self._get_quality_level(current_avg),
            'total_qa_pairs': len(self.quality_history),
            'recent_alerts': len([a for a in self.quality_alerts if time.time() - a.timestamp < 300]),  # Last 5 min
            'hallucination_rate': sum(1 for _, m in self.quality_history if m.hallucination_detected) / len(self.quality_history),
            'trends': self._get_current_trends() if self.enable_quality_trends else None
        }
    
    def get_alerts_by_severity(self, severity: str) -> List[QualityAlert]:
        """Get alerts by severity level"""
        return [alert for alert in self.quality_alerts if alert.severity == severity]
    
    def get_recent_alerts(self, minutes: int = 10) -> List[QualityAlert]:
        """Get alerts from the last N minutes"""
        cutoff_time = time.time() - (minutes * 60)
        return [alert for alert in self.quality_alerts if alert.timestamp >= cutoff_time]
    
    def clear_old_alerts(self, hours: int = 24) -> int:
        """Clear alerts older than specified hours"""
        cutoff_time = time.time() - (hours * 3600)
        old_count = len(self.quality_alerts)
        
        self.quality_alerts = [alert for alert in self.quality_alerts if alert.timestamp >= cutoff_time]
        
        cleared_count = old_count - len(self.quality_alerts)
        
        if cleared_count > 0:
            logger.info(f"Cleared {cleared_count} old quality alerts")
        
        return cleared_count
    
    def export_quality_data(self, output_file: str) -> None:
        """Export all quality data to file"""
        try:
            export_data = {
                'export_timestamp': time.time(),
                'export_date': datetime.now().isoformat(),
                'quality_history': [
                    {
                        'timestamp': timestamp,
                        'metrics': asdict(metrics)
                    }
                    for timestamp, metrics in self.quality_history
                ],
                'alerts': [asdict(alert) for alert in self.quality_alerts],
                'file_quality_scores': self.file_quality_scores,
                'statistics': {
                    'qa_pairs_processed': self.qa_pairs_processed,
                    'quality_checks_performed': self.quality_checks_performed,
                    'alerts_generated': self.alerts_generated
                },
                'configuration': {
                    'alert_threshold': self.alert_threshold,
                    'quality_thresholds': self.quality_thresholds,
                    'trend_window_minutes': self.trend_window_minutes
                }
            }
            
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Quality data exported to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to export quality data: {e}")
            raise
