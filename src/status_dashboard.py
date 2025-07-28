"""
Live Status Dashboard for SetForge
Provides real-time visual monitoring and status display
"""

import os
import time
import asyncio
import shutil
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StatusDashboard:
    """
    Live status dashboard with real-time progress monitoring,
    quality metrics display, and performance tracking.
    """
    
    def __init__(self, config: Any = None):
        self.config = config
        self.refresh_rate = getattr(config.progress, 'status_refresh_rate', 2.0) if config else 2.0
        self.display_width = 100
        self.enable_colors = self._check_color_support()
        self.is_running = False
        
        # Display state
        self.last_update_time = 0
        self.update_counter = 0
        
        logger.debug("StatusDashboard initialized")
    
    def _check_color_support(self) -> bool:
        """Check if terminal supports colors"""
        return os.getenv('TERM', '').lower() != 'dumb' and hasattr(os.sys.stdout, 'isatty') and os.sys.stdout.isatty()
    
    def _colorize(self, text: str, color: str) -> str:
        """Add color codes to text if supported"""
        if not self.enable_colors:
            return text
        
        colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'end': '\033[0m'
        }
        
        return f"{colors.get(color, '')}{text}{colors.get('end', '')}"
    
    def _clear_screen(self) -> None:
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _get_terminal_size(self) -> tuple:
        """Get terminal size"""
        try:
            return shutil.get_terminal_size((80, 24))
        except:
            return (80, 24)
    
    def _format_progress_bar(self, percentage: float, width: int = 40, 
                           char_filled: str = '█', char_empty: str = '░') -> str:
        """Create a visual progress bar"""
        filled_length = int(width * percentage / 100)
        bar = char_filled * filled_length + char_empty * (width - filled_length)
        
        if self.enable_colors:
            if percentage >= 90:
                color = 'green'
            elif percentage >= 70:
                color = 'cyan'
            elif percentage >= 50:
                color = 'yellow'
            else:
                color = 'red'
            
            return self._colorize(bar, color)
        
        return bar
    
    def _format_status_line(self, label: str, value: str, width: int = 25) -> str:
        """Format a status line with consistent width"""
        label_formatted = f"{label}:".ljust(width)
        return f"{label_formatted} {value}"
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def _format_number(self, number: float, precision: int = 2) -> str:
        """Format numbers with appropriate precision"""
        if number >= 1000000:
            return f"{number/1000000:.1f}M"
        elif number >= 1000:
            return f"{number/1000:.1f}K"
        else:
            return f"{number:.{precision}f}"
    
    async def display_live_status(self, progress_tracker: Any, quality_monitor: Any = None,
                                cost_monitor: Any = None) -> None:
        """Display live status dashboard"""
        self.is_running = True
        
        try:
            while self.is_running:
                # Get current status
                status = progress_tracker.get_status_summary()
                quality_status = quality_monitor.get_quality_summary() if quality_monitor else None
                
                # Clear screen and display
                self._clear_screen()
                self._display_dashboard(status, quality_status, cost_monitor)
                
                # Update tracking
                self.last_update_time = time.time()
                self.update_counter += 1
                
                # Wait for next refresh
                await asyncio.sleep(self.refresh_rate)
                
        except asyncio.CancelledError:
            self.is_running = False
            logger.debug("Status dashboard cancelled")
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
            self.is_running = False
    
    def _display_dashboard(self, status: Dict[str, Any], quality_status: Optional[Dict[str, Any]] = None,
                          cost_monitor: Any = None) -> None:
        """Display the complete dashboard"""
        terminal_size = self._get_terminal_size()
        width = min(self.display_width, terminal_size.columns - 2)
        
        # Header
        self._print_header(width)
        
        # Progress section
        self._print_progress_section(status, width)
        
        # Performance section
        self._print_performance_section(status, width)
        
        # Quality section
        if quality_status:
            self._print_quality_section(quality_status, width)
        
        # Cost section
        if cost_monitor:
            self._print_cost_section(status.get('cost_metrics', {}), width)
        
        # Status footer
        self._print_footer(width)
    
    def _print_header(self, width: int) -> None:
        """Print dashboard header"""
        title = "SetForge Production Dashboard"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("=" * width)
        print(self._colorize(title.center(width), 'bold'))
        print(f"Last Updated: {timestamp}".center(width))
        print("=" * width)
        print()
    
    def _print_progress_section(self, status: Dict[str, Any], width: int) -> None:
        """Print progress information"""
        progress = status.get('progress', {})
        performance = status.get('performance', {})
        
        print(self._colorize("📊 PROGRESS STATUS", 'cyan'))
        print("-" * width)
        
        # Progress bar
        percentage = progress.get('percentage', 0)
        progress_bar = self._format_progress_bar(percentage, width - 20)
        print(f"Progress: [{progress_bar}] {percentage:.1f}%")
        print()
        
        # Progress details
        print(self._format_status_line("Files Completed", f"{progress.get('files_completed', 0):,}"))
        print(self._format_status_line("Files Failed", f"{progress.get('files_failed', 0):,}"))
        print(self._format_status_line("Files Remaining", f"{progress.get('files_remaining', 0):,}"))
        print(self._format_status_line("Total Files", f"{progress.get('total_files', 0):,}"))
        
        # Current file
        current_file = progress.get('current_file', 'None')
        if current_file and current_file != 'None':
            current_display = current_file.split('/')[-1] if '/' in current_file else current_file
            if len(current_display) > 50:
                current_display = current_display[:47] + "..."
            print(self._format_status_line("Current File", current_display))
        
        # Time information
        elapsed = self._format_duration(performance.get('elapsed_time_seconds', 0))
        remaining = self._format_duration(performance.get('estimated_remaining_seconds', 0))
        print(self._format_status_line("Elapsed Time", elapsed))
        print(self._format_status_line("Estimated Remaining", remaining))
        
        print()
    
    def _print_performance_section(self, status: Dict[str, Any], width: int) -> None:
        """Print performance metrics"""
        performance = status.get('performance', {})
        qa_metrics = status.get('qa_metrics', {})
        
        print(self._colorize("⚡ PERFORMANCE METRICS", 'yellow'))
        print("-" * width)
        
        # Processing speed
        files_per_min = performance.get('files_per_minute', 0)
        qa_per_min = performance.get('qa_pairs_per_minute', 0)
        recent_speed = performance.get('recent_files_per_minute', 0)
        
        print(self._format_status_line("Files/Minute", f"{files_per_min:.2f}"))
        print(self._format_status_line("QA Pairs/Minute", f"{self._format_number(qa_per_min)}"))
        print(self._format_status_line("Recent Speed", f"{recent_speed:.2f} files/min"))
        
        # QA metrics
        total_qa = qa_metrics.get('total_qa_pairs', 0)
        validated_qa = qa_metrics.get('validated_qa_pairs', 0)
        validation_rate = qa_metrics.get('validation_pass_rate', 0) * 100
        
        print(self._format_status_line("Total QA Pairs", f"{total_qa:,}"))
        print(self._format_status_line("Validated QA Pairs", f"{validated_qa:,}"))
        print(self._format_status_line("Validation Rate", f"{validation_rate:.1f}%"))
        
        print()
    
    def _print_quality_section(self, quality_status: Dict[str, Any], width: int) -> None:
        """Print quality metrics"""
        print(self._colorize("🎯 QUALITY METRICS", 'green'))
        print("-" * width)
        
        if quality_status.get('status') == 'no_data':
            print("No quality data available yet")
            print()
            return
        
        # Current quality
        current_quality = quality_status.get('current_average_quality', 0)
        quality_level = quality_status.get('quality_level', 'unknown')
        
        # Color code quality level
        if quality_level == 'excellent':
            quality_color = 'green'
        elif quality_level == 'good':
            quality_color = 'cyan'
        elif quality_level == 'fair':
            quality_color = 'yellow'
        else:
            quality_color = 'red'
        
        quality_display = self._colorize(f"{current_quality:.3f} ({quality_level})", quality_color)
        print(self._format_status_line("Average Quality", quality_display))
        
        # Additional metrics
        total_analyzed = quality_status.get('total_qa_pairs', 0)
        hallucination_rate = quality_status.get('hallucination_rate', 0) * 100
        recent_alerts = quality_status.get('recent_alerts', 0)
        
        print(self._format_status_line("Total Analyzed", f"{total_analyzed:,}"))
        print(self._format_status_line("Hallucination Rate", f"{hallucination_rate:.2f}%"))
        
        alerts_color = 'red' if recent_alerts > 0 else 'green'
        alerts_display = self._colorize(str(recent_alerts), alerts_color)
        print(self._format_status_line("Recent Alerts", alerts_display))
        
        # Trends
        trends = quality_status.get('trends')
        if trends and not trends.get('insufficient_data'):
            trend_direction = trends.get('trend_direction', 'stable')
            trend_confidence = trends.get('confidence', 0)
            
            if trend_direction == 'improving':
                trend_color = 'green'
                trend_symbol = '↗'
            elif trend_direction == 'declining':
                trend_color = 'red'
                trend_symbol = '↘'
            else:
                trend_color = 'cyan'
                trend_symbol = '→'
            
            trend_display = self._colorize(f"{trend_symbol} {trend_direction}", trend_color)
            print(self._format_status_line("Quality Trend", f"{trend_display} ({trend_confidence:.2f})"))
        
        print()
    
    def _print_cost_section(self, cost_metrics: Dict[str, Any], width: int) -> None:
        """Print cost information"""
        print(self._colorize("💰 COST TRACKING", 'purple'))
        print("-" * width)
        
        total_cost = cost_metrics.get('total_cost', 0)
        cost_per_qa = cost_metrics.get('cost_per_qa_pair', 0)
        estimated_final = cost_metrics.get('estimated_final_cost', 0)
        
        print(self._format_status_line("Current Cost", f"${total_cost:.4f}"))
        print(self._format_status_line("Cost per QA Pair", f"${cost_per_qa:.6f}"))
        print(self._format_status_line("Estimated Final", f"${estimated_final:.2f}"))
        
        # Budget warning if available
        if hasattr(self.config, 'budget') and hasattr(self.config.budget, 'max_cost'):
            budget = self.config.budget.max_cost
            utilization = (estimated_final / budget) * 100 if budget > 0 else 0
            
            if utilization > 90:
                budget_color = 'red'
            elif utilization > 75:
                budget_color = 'yellow'
            else:
                budget_color = 'green'
            
            budget_display = self._colorize(f"{utilization:.1f}%", budget_color)
            print(self._format_status_line("Budget Utilization", budget_display))
        
        print()
    
    def _print_footer(self, width: int) -> None:
        """Print dashboard footer"""
        print("-" * width)
        print(f"Dashboard Updates: {self.update_counter} | Refresh Rate: {self.refresh_rate}s".center(width))
        print("Press Ctrl+C to stop".center(width))
        print("=" * width)
    
    def stop(self) -> None:
        """Stop the dashboard"""
        self.is_running = False
    
    def stop_dashboard(self) -> None:
        """Alias for stop method for compatibility"""
        self.stop()
    
    def display_static_summary(self, progress_tracker: Any, quality_monitor: Any = None) -> None:
        """Display a static summary (for non-interactive environments)"""
        status = progress_tracker.get_status_summary()
        quality_status = quality_monitor.get_quality_summary() if quality_monitor else None
        
        print("\n" + "=" * 80)
        print("SetForge Processing Summary".center(80))
        print("=" * 80)
        
        # Progress summary
        progress = status.get('progress', {})
        print(f"\nProgress: {progress.get('files_completed', 0)}/{progress.get('total_files', 0)} files "
              f"({progress.get('percentage', 0):.1f}%)")
        
        # Performance summary
        performance = status.get('performance', {})
        qa_metrics = status.get('qa_metrics', {})
        
        print(f"QA Pairs Generated: {qa_metrics.get('total_qa_pairs', 0):,}")
        print(f"Processing Speed: {performance.get('files_per_minute', 0):.2f} files/min")
        print(f"Elapsed Time: {self._format_duration(performance.get('elapsed_time_seconds', 0))}")
        
        # Quality summary
        if quality_status and quality_status.get('status') != 'no_data':
            print(f"Average Quality: {quality_status.get('current_average_quality', 0):.3f} "
                  f"({quality_status.get('quality_level', 'unknown')})")
            print(f"Hallucination Rate: {quality_status.get('hallucination_rate', 0)*100:.2f}%")
        
        # Cost summary
        cost_metrics = status.get('cost_metrics', {})
        if cost_metrics.get('total_cost', 0) > 0:
            print(f"Total Cost: ${cost_metrics.get('total_cost', 0):.4f}")
            print(f"Est. Final Cost: ${cost_metrics.get('estimated_final_cost', 0):.2f}")
        
        print("=" * 80 + "\n")
    
    def create_status_log_entry(self, progress_tracker: Any, quality_monitor: Any = None) -> Dict[str, Any]:
        """Create a structured log entry for status"""
        status = progress_tracker.get_status_summary()
        quality_status = quality_monitor.get_quality_summary() if quality_monitor else None
        
        log_entry = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'progress': status.get('progress', {}),
            'performance': status.get('performance', {}),
            'qa_metrics': status.get('qa_metrics', {}),
            'cost_metrics': status.get('cost_metrics', {})
        }
        
        if quality_status:
            log_entry['quality_metrics'] = quality_status
        
        return log_entry


class DashboardManager:
    """Manages dashboard lifecycle and integration"""
    
    def __init__(self, config: Any):
        self.config = config
        self.dashboard = StatusDashboard(config)
        self.dashboard_task: Optional[asyncio.Task] = None
        self.enable_live_dashboard = getattr(config.progress, 'enable_live_dashboard', True)
    
    async def start_dashboard(self, progress_tracker: Any, quality_monitor: Any = None,
                            cost_monitor: Any = None) -> None:
        """Start the live dashboard"""
        if not self.enable_live_dashboard:
            logger.info("Live dashboard disabled in configuration")
            return
        
        try:
            self.dashboard_task = asyncio.create_task(
                self.dashboard.display_live_status(progress_tracker, quality_monitor, cost_monitor)
            )
            logger.info("Live dashboard started")
            
        except Exception as e:
            logger.error(f"Failed to start dashboard: {e}")
    
    async def stop_dashboard(self) -> None:
        """Stop the live dashboard"""
        if self.dashboard_task and not self.dashboard_task.done():
            self.dashboard.stop()
            self.dashboard_task.cancel()
            
            try:
                await self.dashboard_task
            except asyncio.CancelledError:
                pass
            
            logger.info("Live dashboard stopped")
    
    def display_summary(self, progress_tracker: Any, quality_monitor: Any = None) -> None:
        """Display static summary"""
        self.dashboard.display_static_summary(progress_tracker, quality_monitor)
