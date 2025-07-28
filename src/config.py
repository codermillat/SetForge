"""
Production-grade configuration management for SetForge.
"""

import os
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path
import yaml
import hashlib
import json

# Environment-based configuration
ENVIRONMENT = os.getenv('SETFORGE_ENV', 'development')
LOG_LEVEL = os.getenv('SETFORGE_LOG_LEVEL', 'INFO')


@dataclass
@dataclass
class ProgressConfig:
    """Configuration for progress tracking and resumability."""
    enabled: bool = True
    checkpoint_interval_files: int = 5
    checkpoint_interval_minutes: int = 10
    status_refresh_rate: float = 2.0
    enable_live_dashboard: bool = True
    dashboard_enabled: bool = True
    save_partial_results: bool = True
    auto_cleanup_checkpoints: bool = True
    max_checkpoint_files: int = 10
    checkpoint_dir: str = "output/checkpoints"


@dataclass
class QualityConfig:
    """Configuration for quality monitoring and alerts."""
    monitoring_enabled: bool = True
    alert_threshold: float = 0.8
    quality_report_interval: int = 100
    enable_quality_trends: bool = True
    save_quality_reports: bool = True
    cache_size: int = 1000
    trend_analysis_enabled: bool = True
    track_validation_details: bool = True
    trend_window_minutes: int = 10
    min_samples_for_trend: int = 10
    excellent_threshold: float = 0.9
    good_threshold: float = 0.8
    fair_threshold: float = 0.7
    poor_threshold: float = 0.0


@dataclass
class InputConfig:
    """Configuration for input file handling."""
    valid_extensions: List[str] = field(default_factory=lambda: ['.txt', '.md'])
    min_file_size_bytes: int = 100
    max_file_size_bytes: int = 10 * 1024 * 1024  # 10MB
    encoding: str = 'utf-8'
    skip_empty_files: bool = True


@dataclass
class ChunkingConfig:
    """Configuration for text chunking with production optimizations."""
    max_chunk_size: int = 2000
    min_chunk_size: int = 500
    overlap_size: int = 200
    chunk_by_sections: bool = True
    section_headers: List[str] = field(default_factory=lambda: ["#", "##", "###", "####"])
    paragraph_split: bool = True
    preserve_structure: bool = True
    enable_optimization: bool = True  # New: Enable chunk optimization
    merge_small_chunks: bool = True   # New: Merge small chunks for efficiency
    # Enhanced chunking for high-volume QA generation
    sentence_split: bool = False      # NEW: Split by sentences for finer chunks
    bullet_split: bool = False        # NEW: Split by bullet points/lists
    max_sentences_per_chunk: int = 4  # NEW: Limit sentences per chunk
    enable_micro_chunks: bool = False # NEW: Create very small chunks for dense QA generation


@dataclass
class LLMConfig:
    """Configuration for LLM API settings with enhanced error handling."""
    provider: str = "digitalocean"
    base_url: str = "https://inference.do-ai.run"
    api_key: str = ""
    model_name: str = "llama3-8b-instruct"
    max_tokens: int = 1024
    temperature: float = 0.1
    timeout: int = 30
    max_retries: int = 5          # Increased from 3
    retry_delay: float = 1.0
    request_per_minute: int = 60  # New: Rate limiting
    max_concurrent: int = 10      # New: Concurrency control


@dataclass
class QAConfig:
    """Configuration for QA generation with quality optimization."""
    questions_per_chunk: int = 3
    min_question_length: int = 10
    max_question_length: int = 200
    min_answer_length: int = 5
    max_answer_length: int = 500
    question_types: List[str] = field(default_factory=lambda: [
        "factual", "definition", "process", "comparison", "list"
    ])
    forbidden_patterns: List[str] = field(default_factory=lambda: [
        "in my opinion", "i think", "probably", "might be", "could be"
    ])
    enable_caching: bool = True        # New: Cache QA generation results
    cache_ttl_hours: int = 24         # New: Cache time-to-live
    # Enhanced QA generation for high volume
    enable_paraphrasing: bool = False  # NEW: Enable question paraphrasing for data augmentation
    paraphrases_per_question: int = 2  # NEW: Generate 2 paraphrased versions per question
    max_total_questions: int = 15      # NEW: Maximum questions if paraphrasing enabled
    enable_multi_question: bool = False # NEW: Multiple questions for same answer when appropriate


@dataclass
class ValidationConfig:
    """Configuration for QA validation with production tuning."""
    min_relevancy_score: float = 0.75
    min_source_overlap: float = 0.6
    max_inference_ratio: float = 0.15
    min_content_quality: float = 0.6  # New: Explicit content quality threshold
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    enable_semantic_validation: bool = True
    enable_extractive_validation: bool = True
    enable_hallucination_detection: bool = True
    enable_result_caching: bool = True # New: Cache validation results
    manual_review_threshold: float = 0.7  # New: Flag for manual review
    # Enhanced validation for deduplication
    enable_deduplication: bool = False    # NEW: Enable deduplication
    similarity_threshold: float = 0.85    # NEW: Threshold for near-duplicate detection
    max_similar_questions: int = 2        # NEW: Max similar questions allowed
    enable_answer_deduplication: bool = False  # NEW: Also deduplicate by answer similarity


@dataclass  
class CostConfig:
    """Configuration for cost optimization with production controls."""
    max_total_cost_usd: float = 50.0
    cost_per_1k_tokens: float = 0.0005
    enable_caching: bool = True
    cache_dir: str = ".setforge_cache"
    batch_size: int = 10           # Increased from 5
    enable_async: bool = True
    cost_alert_threshold: float = 100.0  # Alert when approaching budget limit  
    enable_cost_optimization: bool = True  # New: Dynamic optimization
    # Enhanced cost management for high volume
    max_concurrent_requests: int = 10     # NEW: Higher concurrency for faster processing
    enable_cost_monitoring: bool = True   # NEW: Enhanced cost tracking


@dataclass
class OutputConfig:
    """Configuration for output generation with enhanced metadata."""
    output_format: str = "jsonl"
    include_metadata: bool = True
    include_source_text: bool = True
    include_validation_scores: bool = True
    compress_output: bool = False
    enable_incremental: bool = True     # New: Incremental processing
    backup_interval: int = 100          # New: Backup every N records
    enable_health_checks: bool = True   # New: Output validation
    # Additional output configuration for high volume
    output_file: str = "output/datasets/qa_dataset.jsonl"  # Default output file
    pretty_print: bool = False          # Whether to pretty-print JSON


@dataclass
class MonitoringConfig:
    """Configuration for monitoring and observability."""
    enable_metrics: bool = True
    metrics_interval_seconds: int = 60
    enable_health_endpoint: bool = False  # For future API mode
    log_structured: bool = True if ENVIRONMENT == 'production' else False
    enable_tracing: bool = True
    performance_threshold_seconds: float = 300.0  # Alert if processing takes > 5min per file


@dataclass
class Config:
    """Main configuration class with production features."""
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    qa: QAConfig = field(default_factory=QAConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    cost: CostConfig = field(default_factory=CostConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # New configuration sections for enhanced tracking
    progress: ProgressConfig = field(default_factory=ProgressConfig)
    quality: QualityConfig = field(default_factory=QualityConfig)
    input: InputConfig = field(default_factory=InputConfig)
    
    # Global settings
    log_level: str = LOG_LEVEL
    log_file: Optional[str] = None
    debug_mode: bool = ENVIRONMENT == 'development'
    dry_run: bool = False
    environment: str = ENVIRONMENT
    config_hash: Optional[str] = None  # For tracking config changes
    
    def __post_init__(self):
        """Post-initialization setup including validation and environment loading."""
        self._load_environment_variables()
        self._apply_environment_overrides()
        self._validate()
        self._setup_logging()
        self.config_hash = self._generate_config_hash()
    
    def _load_environment_variables(self):
        """Load configuration from environment variables."""
        # LLM API key
        if not self.llm.api_key:
            self.llm.api_key = os.getenv('DIGITALOCEAN_API_KEY', '')
        
        # Cost limits
        if os.getenv('SETFORGE_MAX_COST'):
            try:
                self.cost.max_total_cost_usd = float(os.getenv('SETFORGE_MAX_COST'))
            except ValueError:
                logging.warning(f"Invalid SETFORGE_MAX_COST value: {os.getenv('SETFORGE_MAX_COST')}")
        
        # Debug mode
        if os.getenv('SETFORGE_DEBUG'):
            self.debug_mode = os.getenv('SETFORGE_DEBUG').lower() in ['true', '1', 'yes']
        
        # Dry run mode
        if os.getenv('SETFORGE_DRY_RUN'):
            self.dry_run = os.getenv('SETFORGE_DRY_RUN').lower() in ['true', '1', 'yes']
    
    def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides."""
        if self.environment == 'production':
            # Production optimizations
            self.llm.max_retries = 5
            self.llm.timeout = 60
            self.cost.batch_size = 15
            self.monitoring.log_structured = True
            self.output.enable_incremental = True
            self.output.backup_interval = 50
            
        elif self.environment == 'staging':
            # Staging optimizations
            self.llm.max_retries = 4
            self.cost.batch_size = 8
            self.monitoring.enable_metrics = True
            
        elif self.environment == 'development':
            # Development settings
            self.debug_mode = True
            self.llm.max_retries = 3
            self.cost.batch_size = 3
            self.monitoring.enable_metrics = False
    
    def _validate(self):
        """Validate configuration values with comprehensive checks."""
        errors = []
        
        # LLM configuration
        if not self.llm.api_key and not self.dry_run:
            errors.append("LLM API key is required. Set DIGITALOCEAN_API_KEY environment variable or provide it in the configuration file.")
        
        if self.llm.max_tokens < 50 or self.llm.max_tokens > 4000:
            errors.append(f"max_tokens must be between 50 and 4000, got {self.llm.max_tokens}")
        
        if not 0 <= self.llm.temperature <= 2:
            errors.append(f"temperature must be between 0 and 2, got {self.llm.temperature}")
        
        # Chunking configuration
        if self.chunking.min_chunk_size >= self.chunking.max_chunk_size:
            errors.append("min_chunk_size must be less than max_chunk_size")
        
        if self.chunking.overlap_size >= self.chunking.min_chunk_size:
            errors.append("overlap_size should be less than min_chunk_size")
        
        # QA configuration
        if self.qa.questions_per_chunk < 1 or self.qa.questions_per_chunk > 10:
            errors.append("questions_per_chunk should be between 1 and 10")
        
        # Validation configuration
        if not 0 <= self.validation.min_relevancy_score <= 1:
            errors.append("min_relevancy_score must be between 0 and 1")
        
        if not 0 <= self.validation.min_source_overlap <= 1:
            errors.append("min_source_overlap must be between 0 and 1")
        
        if not 0 <= self.validation.max_inference_ratio <= 1:
            errors.append("max_inference_ratio must be between 0 and 1")
        
        # Cost configuration
        if self.cost.max_total_cost_usd <= 0:
            errors.append("max_total_cost_usd must be positive")
        
        if self.cost.cost_per_1k_tokens <= 0:
            errors.append("cost_per_1k_tokens must be positive")
        
        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors))
    
    def _setup_logging(self):
        """Setup structured logging based on environment."""
        if self.monitoring.log_structured and self.environment == 'production':
            # JSON structured logging for production
            try:
                import json_logging
                json_logging.init_request_instrument()
                json_logging.config_root_logger()
            except ImportError:
                # Fallback to standard logging if json_logging not available
                logging.basicConfig(
                    level=getattr(logging, self.log_level.upper()),
                    format='%(asctime)s | %(levelname)8s | %(name)s | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
        else:
            # Standard logging
            logging.basicConfig(
                level=getattr(logging, self.log_level.upper()),
                format='%(asctime)s | %(levelname)8s | %(name)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        if self.log_file:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(getattr(logging, self.log_level.upper()))
            logging.getLogger().addHandler(file_handler)
    
    def _generate_config_hash(self) -> str:
        """Generate a hash of the current configuration for tracking changes."""
        config_dict = {
            'chunking': vars(self.chunking),
            'llm': {k: v for k, v in vars(self.llm).items() if k != 'api_key'},  # Exclude sensitive data
            'qa': vars(self.qa),
            'validation': vars(self.validation),
            'cost': vars(self.cost),
            'output': vars(self.output),
            'environment': self.environment
        }
        config_str = json.dumps(config_dict, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()[:8]
    
    @classmethod
    def from_yaml(cls, yaml_file: str) -> 'Config':
        """Load configuration from YAML file with environment variable substitution."""
        yaml_path = Path(yaml_file)
        if not yaml_path.exists():
            logging.warning(f"Configuration file {yaml_file} not found, using defaults")
            return cls()
        
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f)
            
            if not config_dict:
                logging.warning(f"Configuration file {yaml_file} is empty, using defaults")
                return cls()
            
            # Environment variable substitution
            config_dict = cls._substitute_env_vars(config_dict)
            
            # Create configuration objects
            config = cls()
            
            # Update with loaded values
            for section, values in config_dict.items():
                if hasattr(config, section) and isinstance(values, dict):
                    section_obj = getattr(config, section)
                    for key, value in values.items():
                        if hasattr(section_obj, key):
                            setattr(section_obj, key, value)
                        else:
                            logging.warning(f"Unknown configuration key: {section}.{key}")
                elif hasattr(config, section):
                    setattr(config, section, values)
                else:
                    logging.warning(f"Unknown configuration section: {section}")
            
            return config
            
        except Exception as e:
            logging.error(f"Failed to load configuration from {yaml_file}: {e}")
            logging.info("Using default configuration")
            return cls()
    
    @staticmethod
    def _substitute_env_vars(obj):
        """Recursively substitute environment variables in configuration."""
        if isinstance(obj, dict):
            return {k: Config._substitute_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [Config._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
            env_var = obj[2:-1]
            default_value = ""
            if ':' in env_var:
                env_var, default_value = env_var.split(':', 1)
            return os.getenv(env_var, default_value)
        else:
            return obj
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics for monitoring."""
        return {
            'config_hash': self.config_hash,
            'environment': self.environment,
            'batch_size': self.cost.batch_size,
            'max_retries': self.llm.max_retries,
            'enable_caching': self.cost.enable_caching,
            'enable_optimization': self.chunking.enable_optimization,
            'validation_thresholds': {
                'min_relevancy_score': self.validation.min_relevancy_score,
                'min_source_overlap': self.validation.min_source_overlap,
                'max_inference_ratio': self.validation.max_inference_ratio
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization."""
        return {
            'chunking': vars(self.chunking),
            'llm': {k: v if k != 'api_key' else '***' for k, v in vars(self.llm).items()},
            'qa': vars(self.qa),
            'validation': vars(self.validation),
            'cost': vars(self.cost),
            'output': vars(self.output),
            'monitoring': vars(self.monitoring),
            'environment': self.environment,
            'config_hash': self.config_hash
        }
