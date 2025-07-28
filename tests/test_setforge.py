#!/usr/bin/env python3
"""
SetForge Test Suite

Comprehensive tests to validate SetForge functionality.
"""

import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Import SetForge modules
from src.config import Config
from src.text_processor import TextProcessor, TextChunk
from src.qa_generator import QAGenerator, QAPair
from src.validator import QAValidator
from src.exporter import DatasetExporter


class TestConfig(unittest.TestCase):
    """Test configuration management."""
    
    def test_default_config(self):
        """Test default configuration creation."""
        config = Config()
        
        # Test basic defaults
        self.assertEqual(config.chunking.max_chunk_size, 2000)
        self.assertEqual(config.qa.questions_per_chunk, 3)
        self.assertEqual(config.validation.min_relevancy_score, 0.85)
        self.assertGreater(config.cost.max_total_cost_usd, 0)
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = Config()
        
        # Test invalid chunking settings
        config.chunking.max_chunk_size = 100
        config.chunking.min_chunk_size = 200
        
        with self.assertRaises(ValueError):
            config._validate()


class TestTextProcessor(unittest.IsolatedAsyncioTestCase):
    """Test text processing and chunking."""
    
    async def test_basic_chunking(self):
        """Test basic text chunking."""
        config = Config()
        config.chunking.max_chunk_size = 500
        config.chunking.min_chunk_size = 100
        
        processor = TextProcessor(config)
        
        # Create test content
        content = """# Test Section

This is a test paragraph with some content that should be processed correctly.

## Subsection

Another paragraph with more content to test the chunking algorithm.
The algorithm should split this appropriately.

### Details

Final section with additional details for comprehensive testing.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            chunks = await processor.process_file(temp_path)
            
            # Verify chunks were created
            self.assertGreater(len(chunks), 0)
            
            # Verify chunk properties
            for chunk in chunks:
                self.assertIsInstance(chunk, TextChunk)
                self.assertGreater(len(chunk.content), 0)
                self.assertGreaterEqual(chunk.char_count, config.chunking.min_chunk_size)
                self.assertEqual(chunk.file_path, str(temp_path))
        
        finally:
            temp_path.unlink()
    
    async def test_section_chunking(self):
        """Test section-based chunking."""
        config = Config()
        config.chunking.chunk_by_sections = True
        
        processor = TextProcessor(config)
        
        content = """# Section 1

Content for section 1.

## Section 2

Content for section 2.

### Section 3

Content for section 3.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            chunks = await processor.process_file(temp_path)
            
            # Should have multiple chunks for different sections
            self.assertGreater(len(chunks), 1)
            
            # Check section titles are captured
            section_titles = [chunk.section_title for chunk in chunks if chunk.section_title]
            self.assertGreater(len(section_titles), 0)
        
        finally:
            temp_path.unlink()


class TestQAGenerator(unittest.IsolatedAsyncioTestCase):
    """Test QA generation functionality."""
    
    async def test_mock_qa_generation(self):
        """Test QA generation in dry run mode."""
        config = Config()
        config.dry_run = True
        
        generator = QAGenerator(config)
        
        # Create test chunk
        chunk = TextChunk(
            id="test_chunk",
            file_path="test.txt",
            content="Sharda University offers B.Tech programs in Computer Science. The programs include AI and ML specializations.",
            start_pos=0,
            end_pos=100,
            section_title="Programs"
        )
        
        qa_pairs = await generator.generate_qa_pairs(chunk)
        
        # Should generate at least one QA pair in mock mode
        self.assertGreater(len(qa_pairs), 0)
        
        for qa_pair in qa_pairs:
            self.assertIsInstance(qa_pair, QAPair)
            self.assertGreater(len(qa_pair.question), 0)
            self.assertGreater(len(qa_pair.answer), 0)
            self.assertEqual(qa_pair.chunk_id, "test_chunk")
    
    def test_basic_validation(self):
        """Test basic QA pair validation."""
        config = Config()
        generator = QAGenerator(config)
        
        # Valid QA pair
        valid_qa = QAPair(
            question="What programs does Sharda University offer?",
            answer="B.Tech programs in Computer Science",
            chunk_id="test",
            source_text="Sharda University offers B.Tech programs in Computer Science and Engineering.",
            question_type="factual"
        )
        
        self.assertTrue(generator._basic_validate_qa_pair(valid_qa))
        
        # Invalid QA pair (too short)
        invalid_qa = QAPair(
            question="What?",
            answer="Yes",
            chunk_id="test",
            source_text="Some content here.",
            question_type="factual"
        )
        
        self.assertFalse(generator._basic_validate_qa_pair(invalid_qa))


class TestValidator(unittest.IsolatedAsyncioTestCase):
    """Test QA validation functionality."""
    
    async def test_extractive_validation(self):
        """Test extractive answer validation."""
        config = Config()
        validator = QAValidator(config)
        
        # Highly extractive QA pair
        extractive_qa = QAPair(
            question="What is the tuition fee?",
            answer="The annual tuition fee is $5,000 USD",
            chunk_id="test",
            source_text="The annual tuition fee is $5,000 USD for international students. Additional fees apply.",
            question_type="factual"
        )
        
        result = await validator.validate_qa_pair(extractive_qa)
        
        # Should have high extractive score
        self.assertGreater(result.extractive_score, 0.8)
        self.assertLess(result.hallucination_score, 0.2)
    
    async def test_hallucination_detection(self):
        """Test hallucination detection."""
        config = Config()
        validator = QAValidator(config)
        
        # QA pair with hallucination indicators
        hallucinated_qa = QAPair(
            question="What might be the prospects?",
            answer="Students will probably have good opportunities in the future",
            chunk_id="test",
            source_text="Sharda University offers engineering programs.",
            question_type="factual"
        )
        
        result = await validator.validate_qa_pair(hallucinated_qa)
        
        # Should detect hallucination
        self.assertGreater(result.hallucination_score, 0.1)
        self.assertLess(result.extractive_score, 0.5)


class TestExporter(unittest.IsolatedAsyncioTestCase):
    """Test dataset export functionality."""
    
    async def test_jsonl_export(self):
        """Test JSONL export format."""
        config = Config()
        config.output.include_metadata = True
        config.output.include_validation_scores = True
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            output_path = f.name
        
        try:
            exporter = DatasetExporter(config)
            await exporter.initialize_output(output_path)
            
            # Create test QA pair and validation result
            qa_pair = QAPair(
                question="Test question?",
                answer="Test answer",
                chunk_id="test_chunk",
                source_text="Test source text with answer content",
                question_type="factual",
                metadata={"file_path": "test.txt"}
            )
            
            from src.validator import ValidationResult
            validation_result = ValidationResult(
                is_valid=True,
                relevancy_score=0.9,
                extractive_score=0.95,
                hallucination_score=0.05,
                overall_score=0.92,
                validation_details={},
                issues=[]
            )
            
            await exporter.export_qa_pair(qa_pair, validation_result)
            await exporter.finalize_output()
            
            # Verify file was created and has content
            output_file = Path(output_path)
            self.assertTrue(output_file.exists())
            
            # Read and validate content
            with open(output_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            self.assertGreater(len(lines), 0)
            
            # Parse first non-metadata line
            data_lines = [line for line in lines if not json.loads(line).get('__type')]
            self.assertGreater(len(data_lines), 0)
            
            record = json.loads(data_lines[0])
            self.assertEqual(record['question'], "Test question?")
            self.assertEqual(record['answer'], "Test answer")
            self.assertIn('validation', record)
        
        finally:
            Path(output_path).unlink(missing_ok=True)


class TestIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests for the complete pipeline."""
    
    async def test_end_to_end_processing(self):
        """Test complete end-to-end processing."""
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test input file
            input_file = temp_path / "test_input.txt"
            test_content = """# University Information

## Academic Programs

Sharda University offers comprehensive B.Tech programs in Computer Science Engineering.
The curriculum includes courses in programming, algorithms, and software development.

### Admission Process

Students must complete an application form and provide academic transcripts.
The minimum requirement is 60% marks in 12th grade mathematics and science subjects.

## Fee Structure

The annual tuition fee for international students is $5,000 USD.
Hostel accommodation costs an additional $1,200 per year.
"""
            
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            # Set up configuration for testing
            config = Config()
            config.dry_run = True  # Don't make real API calls
            config.qa.questions_per_chunk = 2
            config.validation.enable_semantic_validation = False  # Skip for testing
            config.log_level = "WARNING"  # Reduce noise
            
            # Import and run SetForge
            from setforge import SetForge
            
            setforge = SetForge()
            setforge.config = config
            
            output_file = temp_path / "test_output.jsonl"
            
            # Process directory
            stats = await setforge.process_directory(str(temp_path), str(output_file))
            
            # Verify results
            self.assertEqual(stats['files_processed'], 1)
            self.assertGreater(stats['chunks_processed'], 0)
            self.assertGreater(stats['qa_pairs_generated'], 0)
            
            # Verify output file exists and has content
            self.assertTrue(output_file.exists())
            
            with open(output_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Should have at least some output
            self.assertGreater(len(lines), 0)


async def run_tests():
    """Run all tests."""
    print("🧪 Running SetForge Test Suite")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestConfig,
        TestTextProcessor,
        TestQAGenerator,
        TestValidator,
        TestExporter,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    exit(0 if success else 1)
