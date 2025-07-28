"""
Production-grade dataset exporter with comprehensive traceability and metadata.
"""

import json
import time
import logging
import hashlib
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class ExportMetadata:
    """Comprehensive metadata for exported QA pairs."""
    export_timestamp: float
    source_file: str
    chunk_id: str
    chunk_position: int
    processing_pipeline_version: str
    config_hash: str
    model_used: str
    validation_version: str
    generation_cost_usd: float
    processing_time_seconds: float
    quality_scores: Dict[str, float]
    validation_confidence: str
    export_id: str


class ProductionExporter:
    """Production-grade exporter with traceability and quality tracking."""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Export tracking
        self.export_stats = {
            'total_exported': 0,
            'total_cost': 0.0,
            'exports_by_quality': {'high': 0, 'medium': 0, 'low': 0},
            'exports_by_source': {},
            'start_time': time.time()
        }
        
        # Quality thresholds for different export tiers
        self.quality_thresholds = {
            'premium': 0.9,
            'standard': 0.75,
            'basic': 0.6
        }
        
    async def export_qa_pair(self, qa_pair, validation_result, additional_metadata: Optional[Dict] = None) -> bool:
        """Export QA pair with comprehensive metadata and traceability."""
        try:
            # Generate export metadata
            export_metadata = self._generate_export_metadata(
                qa_pair, validation_result, additional_metadata
            )
            
            # Create export record
            export_record = self._create_export_record(qa_pair, validation_result, export_metadata)
            
            # Determine export path based on quality
            export_path = self._determine_export_path(validation_result.overall_score)
            
            # Write to appropriate output file
            success = await self._write_export_record(export_record, export_path)
            
            if success:
                self._update_export_stats(qa_pair, validation_result, export_metadata)
                
                # Log export for audit trail
                self._log_export_audit(qa_pair, validation_result, export_metadata)
                
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to export QA pair from chunk {qa_pair.chunk_id}: {e}")
            return False
    
    def _generate_export_metadata(self, qa_pair, validation_result, additional_metadata: Optional[Dict]) -> ExportMetadata:
        """Generate comprehensive metadata for the export."""
        export_id = self._generate_export_id(qa_pair, validation_result)
        
        # Extract source file from chunk_id or additional metadata
        source_file = getattr(qa_pair, 'source_file', 'unknown')
        if hasattr(qa_pair, 'metadata') and 'source_file' in qa_pair.metadata:
            source_file = qa_pair.metadata['source_file']
        elif additional_metadata and 'source_file' in additional_metadata:
            source_file = additional_metadata['source_file']
        
        return ExportMetadata(
            export_timestamp=time.time(),
            source_file=source_file,
            chunk_id=qa_pair.chunk_id,
            chunk_position=getattr(qa_pair, 'chunk_position', 0),
            processing_pipeline_version=getattr(self.config, 'version', '2.0'),
            config_hash=getattr(self.config, 'config_hash', 'unknown'),
            model_used=getattr(self.config.llm, 'model', 'unknown'),
            validation_version=getattr(validation_result, 'validator_version', '2.0'),
            generation_cost_usd=getattr(qa_pair, 'generation_cost', 0.0),
            processing_time_seconds=getattr(validation_result, 'processing_time', 0.0),
            quality_scores=validation_result.scores,
            validation_confidence=getattr(validation_result, 'confidence_level', 'medium'),
            export_id=export_id
        )
    
    def _generate_export_id(self, qa_pair, validation_result) -> str:
        """Generate unique export ID for traceability."""
        content_hash = hashlib.md5(
            f"{qa_pair.question}{qa_pair.answer}{qa_pair.chunk_id}".encode()
        ).hexdigest()[:12]
        
        timestamp = int(time.time() * 1000) % 1000000  # Last 6 digits of timestamp
        
        return f"exp_{content_hash}_{timestamp}"
    
    def _create_export_record(self, qa_pair, validation_result, export_metadata: ExportMetadata) -> Dict[str, Any]:
        """Create comprehensive export record with all traceability data."""
        
        # Core QA data
        record = {
            'question': qa_pair.question,
            'answer': qa_pair.answer,
            'source_text': qa_pair.source_text,
            'question_type': getattr(qa_pair, 'question_type', 'unknown'),
        }
        
        # Validation results
        record['validation'] = {
            'is_valid': validation_result.is_valid,
            'overall_score': validation_result.overall_score,
            'detailed_scores': validation_result.scores,
            'issues': validation_result.issues,
            'recommendations': getattr(validation_result, 'recommendations', []),
            'confidence_level': getattr(validation_result, 'confidence_level', 'medium'),
            'processing_time': getattr(validation_result, 'processing_time', 0.0)
        }
        
        # Comprehensive metadata
        record['metadata'] = asdict(export_metadata)
        
        # Additional QA pair metadata if available
        if hasattr(qa_pair, 'metadata') and qa_pair.metadata:
            record['qa_metadata'] = qa_pair.metadata
        
        # Quality assessment
        record['quality_tier'] = self._assess_quality_tier(validation_result.overall_score)
        
        # Traceability information
        record['traceability'] = {
            'pipeline_version': export_metadata.processing_pipeline_version,
            'config_snapshot': self._get_config_snapshot(),
            'processing_environment': {
                'timestamp': export_metadata.export_timestamp,
                'environment': getattr(self.config, 'environment', 'unknown')
            }
        }
        
        return record
    
    def _determine_export_path(self, overall_score: float) -> str:
        """Determine export path based on quality score."""
        base_output = getattr(self.config.output, 'base_path', 'output.jsonl')
        base_path = Path(base_output)
        
        # Create quality-based output files if enabled
        if getattr(self.config.output, 'separate_by_quality', False):
            quality_tier = self._assess_quality_tier(overall_score)
            quality_suffix = f"_{quality_tier}"
            quality_path = base_path.parent / f"{base_path.stem}{quality_suffix}{base_path.suffix}"
            return str(quality_path)
        
        return str(base_path)
    
    def _assess_quality_tier(self, overall_score: float) -> str:
        """Assess quality tier based on score."""
        if overall_score >= self.quality_thresholds['premium']:
            return 'premium'
        elif overall_score >= self.quality_thresholds['standard']:
            return 'standard'
        elif overall_score >= self.quality_thresholds['basic']:
            return 'basic'
        else:
            return 'low_quality'
    
    async def _write_export_record(self, record: Dict[str, Any], export_path: str) -> bool:
        """Write export record to file with error handling."""
        try:
            # Ensure directory exists
            Path(export_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Write in JSONL format
            with open(export_path, 'a', encoding='utf-8') as f:
                json.dump(record, f, ensure_ascii=False, separators=(',', ':'))
                f.write('\\n')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write export record to {export_path}: {e}")
            return False
    
    def _update_export_stats(self, qa_pair, validation_result, export_metadata: ExportMetadata):
        """Update export statistics for monitoring."""
        self.export_stats['total_exported'] += 1
        self.export_stats['total_cost'] += export_metadata.generation_cost_usd
        
        # Update quality distribution
        confidence = export_metadata.validation_confidence
        if confidence in self.export_stats['exports_by_quality']:
            self.export_stats['exports_by_quality'][confidence] += 1
        
        # Update source file distribution
        source_file = export_metadata.source_file
        if source_file not in self.export_stats['exports_by_source']:
            self.export_stats['exports_by_source'][source_file] = 0
        self.export_stats['exports_by_source'][source_file] += 1
    
    def _log_export_audit(self, qa_pair, validation_result, export_metadata: ExportMetadata):
        """Log export for audit trail."""
        audit_info = {
            'export_id': export_metadata.export_id,
            'source_file': export_metadata.source_file,
            'chunk_id': qa_pair.chunk_id,
            'overall_score': validation_result.overall_score,
            'quality_tier': self._assess_quality_tier(validation_result.overall_score),
            'cost': export_metadata.generation_cost_usd,
            'timestamp': export_metadata.export_timestamp
        }
        
        if getattr(self.config.output, 'enable_audit_log', True):
            self.logger.info(f"EXPORT_AUDIT: {json.dumps(audit_info)}")
    
    def _get_config_snapshot(self) -> Dict[str, Any]:
        """Get snapshot of relevant configuration for traceability."""
        return {
            'llm_model': getattr(self.config.llm, 'model', 'unknown'),
            'validation_thresholds': {
                'min_overall_score': getattr(self.config.validation, 'min_overall_score', 0.7),
                'min_source_overlap': getattr(self.config.validation, 'min_source_overlap', 0.6),
                'min_relevancy_score': getattr(self.config.validation, 'min_relevancy_score', 0.75)
            },
            'chunk_settings': {
                'max_chunk_size': getattr(self.config.chunking, 'max_chunk_size', 1000),
                'overlap_size': getattr(self.config.chunking, 'overlap_size', 100)
            },
            'qa_generation': {
                'max_questions_per_chunk': getattr(self.config.qa, 'max_questions_per_chunk', 3)
            }
        }
    
    def create_dataset_manifest(self, output_path: str) -> str:
        """Create dataset manifest with comprehensive metadata."""
        manifest_path = Path(output_path).parent / "dataset_manifest.json"
        
        # Calculate processing duration
        processing_duration = time.time() - self.export_stats['start_time']
        
        # Get quality distribution percentages
        total_exports = self.export_stats['total_exported']
        quality_percentages = {}
        for quality, count in self.export_stats['exports_by_quality'].items():
            quality_percentages[quality] = (count / total_exports * 100) if total_exports > 0 else 0
        
        manifest = {
            'dataset_info': {
                'name': getattr(self.config.output, 'dataset_name', 'SetForge Dataset'),
                'version': getattr(self.config, 'version', '2.0'),
                'creation_timestamp': time.time(),
                'total_qa_pairs': total_exports,
                'processing_duration_seconds': processing_duration,
                'total_generation_cost_usd': self.export_stats['total_cost']
            },
            'quality_distribution': {
                'counts': dict(self.export_stats['exports_by_quality']),
                'percentages': quality_percentages
            },
            'source_distribution': dict(self.export_stats['exports_by_source']),
            'configuration_snapshot': self._get_config_snapshot(),
            'processing_environment': {
                'config_hash': getattr(self.config, 'config_hash', 'unknown'),
                'environment': getattr(self.config, 'environment', 'production'),
                'pipeline_version': getattr(self.config, 'version', '2.0')
            },
            'quality_thresholds': self.quality_thresholds,
            'files_generated': self._get_generated_files(output_path),
            'validation_statistics': self._get_validation_summary()
        }
        
        try:
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Dataset manifest created: {manifest_path}")
            return str(manifest_path)
            
        except Exception as e:
            self.logger.error(f"Failed to create dataset manifest: {e}")
            return ""
    
    def _get_generated_files(self, output_path: str) -> List[Dict[str, Any]]:
        """Get information about generated files."""
        base_path = Path(output_path)
        files = []
        
        # Find all related output files
        pattern = f"{base_path.stem}*{base_path.suffix}"
        for file_path in base_path.parent.glob(pattern):
            if file_path.is_file():
                try:
                    file_size = file_path.stat().st_size
                    
                    # Count lines for JSONL files
                    line_count = 0
                    if file_path.suffix == '.jsonl':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            line_count = sum(1 for _ in f)
                    
                    files.append({
                        'path': str(file_path),
                        'size_bytes': file_size,
                        'qa_pairs': line_count,
                        'quality_tier': self._extract_quality_tier_from_filename(file_path.name)
                    })
                except Exception as e:
                    self.logger.warning(f"Could not get stats for {file_path}: {e}")
        
        return files
    
    def _extract_quality_tier_from_filename(self, filename: str) -> Optional[str]:
        """Extract quality tier from filename if present."""
        for tier in ['premium', 'standard', 'basic', 'low_quality']:
            if tier in filename:
                return tier
        return None
    
    def _get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary if validator is available."""
        # This would be populated by the validator if integrated
        return {
            'note': 'Validation statistics would be populated by validator integration'
        }
    
    def create_data_lineage_report(self, output_path: str) -> str:
        """Create detailed data lineage report for compliance and audit."""
        lineage_path = Path(output_path).parent / "data_lineage_report.json"
        
        lineage_report = {
            'report_metadata': {
                'generated_at': time.time(),
                'report_version': '1.0',
                'pipeline_version': getattr(self.config, 'version', '2.0')
            },
            'data_sources': list(self.export_stats['exports_by_source'].keys()),
            'processing_pipeline': {
                'stages': [
                    'text_processing',
                    'qa_generation', 
                    'validation',
                    'export'
                ],
                'configuration': self._get_config_snapshot(),
                'model_information': {
                    'llm_model': getattr(self.config.llm, 'model', 'unknown'),
                    'embedding_model': getattr(self.config.validation, 'semantic_model', 'all-MiniLM-L6-v2'),
                    'api_endpoint': getattr(self.config.llm, 'api_url', 'unknown')
                }
            },
            'quality_assurance': {
                'validation_criteria': {
                    'extractive_threshold': getattr(self.config.validation, 'min_source_overlap', 0.6),
                    'relevancy_threshold': getattr(self.config.validation, 'min_relevancy_score', 0.75),
                    'overall_score_threshold': getattr(self.config.validation, 'min_overall_score', 0.7)
                },
                'quality_distribution': dict(self.export_stats['exports_by_quality'])
            },
            'cost_tracking': {
                'total_cost_usd': self.export_stats['total_cost'],
                'cost_per_qa_pair': (
                    self.export_stats['total_cost'] / self.export_stats['total_exported']
                    if self.export_stats['total_exported'] > 0 else 0
                )
            },
            'compliance_info': {
                'data_retention_policy': getattr(self.config.output, 'retention_days', 365),
                'privacy_level': getattr(self.config.output, 'privacy_level', 'internal'),
                'audit_enabled': getattr(self.config.output, 'enable_audit_log', True)
            }
        }
        
        try:
            with open(lineage_path, 'w', encoding='utf-8') as f:
                json.dump(lineage_report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Data lineage report created: {lineage_path}")
            return str(lineage_path)
            
        except Exception as e:
            self.logger.error(f"Failed to create data lineage report: {e}")
            return ""
    
    def get_export_statistics(self) -> Dict[str, Any]:
        """Get comprehensive export statistics."""
        processing_duration = time.time() - self.export_stats['start_time']
        
        return {
            'total_exported': self.export_stats['total_exported'],
            'total_cost_usd': self.export_stats['total_cost'],
            'processing_duration_seconds': processing_duration,
            'exports_per_hour': (
                self.export_stats['total_exported'] / (processing_duration / 3600)
                if processing_duration > 0 else 0
            ),
            'cost_per_qa_pair': (
                self.export_stats['total_cost'] / self.export_stats['total_exported']
                if self.export_stats['total_exported'] > 0 else 0
            ),
            'quality_distribution': dict(self.export_stats['exports_by_quality']),
            'source_file_distribution': dict(self.export_stats['exports_by_source'])
        }
