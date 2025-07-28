"""
Dataset exporter module for SetForge.

Handles output generation with full traceability and metadata.
"""

import json
import logging
import gzip
from typing import Dict, List, Optional, TextIO
from pathlib import Path
from datetime import datetime, timezone
import asyncio

from config import Config
from qa_generator import QAPair
from validator import ValidationResult


class DatasetExporter:
    """Dataset exporter with JSONL format and metadata tracking."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.output_file: Optional[TextIO] = None
        self.output_path: Optional[Path] = None
        self.record_count = 0
        self.metadata = {
            'created_at': datetime.now(timezone.utc).isoformat(),
            'setforge_version': '1.0.0',
            'config': self.config.to_dict(),
            'statistics': {
                'total_records': 0,
                'validation_pass_rate': 0.0,
                'average_scores': {}
            }
        }
        
        # Track validation statistics
        self.validation_stats = {
            'total_processed': 0,
            'total_passed': 0,
            'score_sum': {
                'relevancy': 0.0,
                'extractive': 0.0,
                'overall': 0.0
            }
        }
    
    async def initialize_output(self, output_path: str) -> None:
        """Initialize output file and write metadata header."""
        self.output_path = Path(output_path)
        
        # Create output directory if needed
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Open output file
        if self.config.output.compress_output:
            if not self.output_path.suffix == '.gz':
                self.output_path = self.output_path.with_suffix(self.output_path.suffix + '.gz')
            self.output_file = gzip.open(self.output_path, 'wt', encoding='utf-8')
        else:
            self.output_file = open(self.output_path, 'w', encoding='utf-8')
        
        self.logger.info(f"Initialized output file: {self.output_path}")
        
        # Write metadata header if enabled
        if self.config.output.include_metadata:
            metadata_record = {
                '__type': 'metadata',
                '__timestamp': self.metadata['created_at'],
                'setforge_metadata': self.metadata
            }
            await self._write_record(metadata_record)
    
    async def export_qa_pair(self, qa_pair: QAPair, validation_result: ValidationResult) -> None:
        """Export a validated QA pair to the dataset."""
        if not self.output_file:
            raise ValueError("Output file not initialized")
        
        # Update validation statistics
        self._update_validation_stats(validation_result)
        
        # Create output record
        record = {
            'file': qa_pair.metadata.get('file_path', ''),
            'chunk_id': qa_pair.chunk_id,
            'question': qa_pair.question,
            'answer': qa_pair.answer,
            'question_type': qa_pair.question_type
        }
        
        # Add optional fields based on configuration
        if self.config.output.include_source_text:
            record['source_text'] = qa_pair.source_text
        
        if self.config.output.include_validation_scores:
            record['validation'] = {
                'is_valid': validation_result.is_valid,
                'relevancy_score': round(validation_result.relevancy_score, 4),
                'extractive_score': round(validation_result.extractive_score, 4),
                'hallucination_score': round(validation_result.hallucination_score, 4),
                'overall_score': round(validation_result.overall_score, 4)
            }
        
        if self.config.output.include_metadata:
            record['metadata'] = {
                'section_title': qa_pair.metadata.get('section_title'),
                'generation_timestamp': qa_pair.metadata.get('generation_timestamp'),
                'model_used': qa_pair.metadata.get('model_used'),
                'confidence_score': qa_pair.confidence_score,
                'validation_details': validation_result.validation_details if self.config.debug_mode else None
            }
        
        # Add processing timestamps
        record['__exported_at'] = datetime.now(timezone.utc).isoformat()
        
        await self._write_record(record)
        self.record_count += 1
        
        self.logger.debug(f"Exported QA pair {qa_pair.chunk_id} (Record #{self.record_count})")
    
    async def _write_record(self, record: Dict) -> None:
        """Write a single record to the output file."""
        try:
            json_line = json.dumps(record, ensure_ascii=False, separators=(',', ':'))
            self.output_file.write(json_line + '\n')
            
            # Flush periodically for large datasets
            if self.record_count % 100 == 0:
                self.output_file.flush()
                
        except Exception as e:
            self.logger.error(f"Failed to write record: {e}")
            raise
    
    def _update_validation_stats(self, validation_result: ValidationResult) -> None:
        """Update running validation statistics."""
        self.validation_stats['total_processed'] += 1
        
        if validation_result.is_valid:
            self.validation_stats['total_passed'] += 1
        
        # Update score sums for averaging
        self.validation_stats['score_sum']['relevancy'] += validation_result.relevancy_score
        self.validation_stats['score_sum']['extractive'] += validation_result.extractive_score
        self.validation_stats['score_sum']['overall'] += validation_result.overall_score
    
    async def finalize_output(self) -> None:
        """Finalize output file and write summary statistics."""
        if not self.output_file:
            return
        
        # Calculate final statistics
        total_processed = self.validation_stats['total_processed']
        if total_processed > 0:
            self.metadata['statistics'] = {
                'total_records': self.record_count,
                'total_processed': total_processed,
                'total_passed': self.validation_stats['total_passed'],
                'validation_pass_rate': self.validation_stats['total_passed'] / total_processed,
                'average_scores': {
                    'relevancy': self.validation_stats['score_sum']['relevancy'] / total_processed,
                    'extractive': self.validation_stats['score_sum']['extractive'] / total_processed,
                    'overall': self.validation_stats['score_sum']['overall'] / total_processed
                }
            }
        
        # Write final metadata record if enabled
        if self.config.output.include_metadata:
            final_metadata = {
                '__type': 'final_metadata',
                '__timestamp': datetime.now(timezone.utc).isoformat(),
                'setforge_statistics': self.metadata['statistics']
            }
            await self._write_record(final_metadata)
        
        # Close output file
        self.output_file.flush()
        self.output_file.close()
        
        self.logger.info(f"Finalized output: {self.record_count} records written to {self.output_path}")
        self.logger.info(f"Validation pass rate: {self.metadata['statistics'].get('validation_pass_rate', 0):.2%}")
    
    def create_summary_report(self) -> Dict:
        """Create a summary report of the export process."""
        return {
            'export_summary': {
                'output_file': str(self.output_path),
                'total_records': self.record_count,
                'file_size_bytes': self.output_path.stat().st_size if self.output_path.exists() else 0,
                'compressed': self.config.output.compress_output,
                'format': self.config.output.output_format
            },
            'validation_summary': self.metadata['statistics'],
            'configuration': {
                'include_metadata': self.config.output.include_metadata,
                'include_source_text': self.config.output.include_source_text,
                'include_validation_scores': self.config.output.include_validation_scores
            }
        }
    
    async def export_summary_json(self, summary_path: Optional[str] = None) -> str:
        """Export summary report as separate JSON file."""
        if not summary_path:
            summary_path = str(self.output_path.with_suffix('.summary.json'))
        
        summary = self.create_summary_report()
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Summary report saved to: {summary_path}")
        return summary_path


class DatasetValidator:
    """Utility class for validating existing JSONL datasets."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def validate_dataset(self, dataset_path: str) -> Dict:
        """Validate an existing JSONL dataset."""
        dataset_path = Path(dataset_path)
        
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {dataset_path}")
        
        validation_results = {
            'total_records': 0,
            'valid_records': 0,
            'invalid_records': 0,
            'metadata_records': 0,
            'validation_errors': [],
            'schema_errors': [],
            'statistics': {}
        }
        
        # Open file (handle compression)
        if dataset_path.suffix == '.gz':
            file_handle = gzip.open(dataset_path, 'rt', encoding='utf-8')
        else:
            file_handle = open(dataset_path, 'r', encoding='utf-8')
        
        try:
            line_number = 0
            
            async for line in self._read_lines_async(file_handle):
                line_number += 1
                
                try:
                    record = json.loads(line.strip())
                    validation_results['total_records'] += 1
                    
                    # Check if it's a metadata record
                    if record.get('__type') in ['metadata', 'final_metadata']:
                        validation_results['metadata_records'] += 1
                        continue
                    
                    # Validate record schema
                    schema_valid, schema_errors = self._validate_record_schema(record)
                    
                    if schema_valid:
                        validation_results['valid_records'] += 1
                    else:
                        validation_results['invalid_records'] += 1
                        validation_results['schema_errors'].extend([
                            f"Line {line_number}: {error}" for error in schema_errors
                        ])
                
                except json.JSONDecodeError as e:
                    validation_results['invalid_records'] += 1
                    validation_results['validation_errors'].append(
                        f"Line {line_number}: JSON decode error - {e}"
                    )
                
                except Exception as e:
                    validation_results['validation_errors'].append(
                        f"Line {line_number}: Unexpected error - {e}"
                    )
        
        finally:
            file_handle.close()
        
        # Calculate statistics
        total_content_records = validation_results['total_records'] - validation_results['metadata_records']
        if total_content_records > 0:
            validation_results['statistics'] = {
                'content_records': total_content_records,
                'validity_rate': validation_results['valid_records'] / total_content_records,
                'error_rate': validation_results['invalid_records'] / total_content_records
            }
        
        return validation_results
    
    async def _read_lines_async(self, file_handle):
        """Async generator for reading lines from file."""
        for line in file_handle:
            yield line
    
    def _validate_record_schema(self, record: Dict) -> tuple[bool, List[str]]:
        """Validate record against expected schema."""
        errors = []
        required_fields = ['question', 'answer', 'chunk_id']
        
        # Check required fields
        for field in required_fields:
            if field not in record:
                errors.append(f"Missing required field: {field}")
        
        # Validate field types and constraints
        if 'question' in record:
            if not isinstance(record['question'], str) or len(record['question'].strip()) == 0:
                errors.append("Question must be a non-empty string")
        
        if 'answer' in record:
            if not isinstance(record['answer'], str) or len(record['answer'].strip()) == 0:
                errors.append("Answer must be a non-empty string")
        
        if 'chunk_id' in record:
            if not isinstance(record['chunk_id'], str) or len(record['chunk_id'].strip()) == 0:
                errors.append("Chunk ID must be a non-empty string")
        
        # Validate validation scores if present
        if 'validation' in record and isinstance(record['validation'], dict):
            validation_obj = record['validation']
            score_fields = ['relevancy_score', 'extractive_score', 'overall_score']
            
            for score_field in score_fields:
                if score_field in validation_obj:
                    score = validation_obj[score_field]
                    if not isinstance(score, (int, float)) or not 0 <= score <= 1:
                        errors.append(f"Invalid {score_field}: must be number between 0 and 1")
        
        return len(errors) == 0, errors
