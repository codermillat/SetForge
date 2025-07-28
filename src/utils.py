"""
Utility functions and helpers for SetForge.
"""

import logging
import sys
import time
from contextlib import contextmanager
from typing import Generator, Optional
import os


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Setup logging configuration for SetForge."""
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # Create formatters
    console_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)8s | %(name)s | %(filename)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)


@contextmanager
def progress_tracker(total: int, description: str = "Processing") -> Generator:
    """Simple progress tracker context manager."""
    
    class ProgressTracker:
        def __init__(self, total: int, description: str):
            self.total = total
            self.description = description
            self.current = 0
            self.start_time = time.time()
            self.last_update = 0
            
            print(f"{self.description}: 0/{self.total} (0.0%)")
        
        def update(self, increment: int = 1):
            self.current += increment
            current_time = time.time()
            
            # Update every second or on completion
            if current_time - self.last_update >= 1.0 or self.current >= self.total:
                self.last_update = current_time
                percentage = (self.current / self.total) * 100
                elapsed = current_time - self.start_time
                
                if self.current > 0:
                    eta = (elapsed / self.current) * (self.total - self.current)
                    eta_str = f" | ETA: {eta:.0f}s" if eta > 1 else ""
                else:
                    eta_str = ""
                
                print(f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%) | Elapsed: {elapsed:.0f}s{eta_str}")
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                elapsed = time.time() - self.start_time
                print(f"{self.description} completed in {elapsed:.2f}s")
            else:
                print(f"{self.description} failed after {time.time() - self.start_time:.2f}s")
    
    tracker = ProgressTracker(total, description)
    yield tracker


def format_bytes(bytes_value: int) -> str:
    """Format bytes into human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def validate_file_path(file_path: str, must_exist: bool = True, extension: Optional[str] = None) -> bool:
    """Validate file path with optional existence and extension checks."""
    import os
    from pathlib import Path
    
    try:
        path = Path(file_path)
        
        if must_exist and not path.exists():
            return False
        
        if extension and path.suffix.lower() != extension.lower():
            return False
        
        # Check if parent directory exists (for output files)
        if not must_exist and not path.parent.exists():
            return False
        
        return True
        
    except Exception:
        return False


def estimate_processing_time(file_count: int, avg_file_size_kb: float) -> float:
    """Estimate processing time based on file count and average size."""
    # Rough estimates based on typical processing rates
    # These would be calibrated based on actual performance data
    
    base_time_per_file = 2.0  # seconds
    size_factor = max(avg_file_size_kb / 100, 1.0)  # Larger files take longer
    
    return file_count * base_time_per_file * size_factor


def create_cache_key(content: str, config_hash: str) -> str:
    """Create cache key for content and configuration."""
    import hashlib
    
    combined = f"{content}|{config_hash}"
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()[:16]


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for cross-platform compatibility."""
    import re
    
    # Remove or replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)
    filename = filename.strip('.')
    
    # Limit length
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:190] + ext
    
    return filename


class CostTracker:
    """Utility class for tracking API costs."""
    
    def __init__(self, cost_per_1k_tokens: float, max_cost: float):
        self.cost_per_1k_tokens = cost_per_1k_tokens
        self.max_cost = max_cost
        self.total_cost = 0.0
        self.total_tokens = 0
        self.requests_made = 0
    
    def add_usage(self, tokens_used: int) -> float:
        """Add token usage and return cost for this usage."""
        cost = (tokens_used / 1000) * self.cost_per_1k_tokens
        self.total_cost += cost
        self.total_tokens += tokens_used
        self.requests_made += 1
        return cost
    
    def can_afford(self, estimated_tokens: int) -> bool:
        """Check if we can afford the estimated token usage."""
        estimated_cost = (estimated_tokens / 1000) * self.cost_per_1k_tokens
        return (self.total_cost + estimated_cost) <= self.max_cost
    
    def remaining_budget(self) -> float:
        """Get remaining budget."""
        return max(0, self.max_cost - self.total_cost)
    
    def get_stats(self) -> dict:
        """Get usage statistics."""
        return {
            'total_cost': self.total_cost,
            'total_tokens': self.total_tokens,
            'requests_made': self.requests_made,
            'remaining_budget': self.remaining_budget(),
            'average_tokens_per_request': self.total_tokens / max(self.requests_made, 1),
            'cost_efficiency': self.total_tokens / max(self.total_cost, 0.001)
        }


class ConfigurationError(Exception):
    """Raised when there's a configuration error."""
    pass


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class CostLimitExceededError(Exception):
    """Raised when cost limit is exceeded."""
    pass


class APIError(Exception):
    """Raised when API calls fail."""
    pass
