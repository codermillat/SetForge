#!/usr/bin/env python3
"""
SetForge Production Pipeline
Integrated production system for high-quality dataset generation
"""
from logging import Logger
from pathlib import Path

# Import necessary components
from src.utils.config_manager import ConfigManager
from src.utils.api_client_manager import APIClientManager
from src.pipeline.content_extractor import ContentExtractor
from src.pipeline.data_structuring import DataStructurer

class SetForgeProductionPipeline:
    """
    Main production pipeline for SetForge.
    This version is focused on Part 1: The Knowledge Forge.
    It orchestrates the cleaning of raw data and the creation of a
    structured knowledge base.
    """
    
    def __init__(self, config: ConfigManager, logger: Logger):
        self.config = config
        self.logger = logger
        self.api_manager = APIClientManager(config, logger)

    async def run(self) -> bool:
        """
        Run the complete data processing pipeline (Part 1).
        """
        try:
            self.logger.info("🚀 Starting SetForge Knowledge Forge Pipeline (Part 1)")
            
            # Phase 1: Setup and validation
            if not await self._setup_pipeline():
                return False
            
            # Phase 2: Context processing (Clean and Structure)
            success = await self._load_and_process_contexts()
            
            if success:
                self.logger.info("✅ Knowledge Forge pipeline completed successfully!")
            else:
                self.logger.error("❌ Knowledge Forge pipeline failed.")
                
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Pipeline execution failed: {e}", exc_info=True)
            return False
        finally:
            await self.api_manager.close_session()

    async def _setup_pipeline(self) -> bool:
        """Setup pipeline components and directories."""
        try:
            # Create necessary directories from config
            data_config = self.config.get('data_config', {})
            Path(data_config.get('raw_dir', 'data')).mkdir(parents=True, exist_ok=True)
            Path(data_config.get('cleaned_dir', 'data_cleaned')).mkdir(parents=True, exist_ok=True)
            # The annotated dir is a new requirement for the refactored pipeline
            Path(data_config.get('annotated_dir', 'data_annotated')).mkdir(parents=True, exist_ok=True)
            Path(data_config.get('structured_dir', 'data_structured')).mkdir(parents=True, exist_ok=True)
            self.logger.info("✅ All pipeline directories ensured.")
            return True
        except Exception as e:
            self.logger.error(f"❌ Pipeline setup failed: {e}", exc_info=True)
            return False
    
    async def _load_and_process_contexts(self) -> bool:
        """
        Orchestrates the full data processing pipeline from raw text to
        a structured and validated knowledge base.
        """
        try:
            steps = self.config.get('steps', ['clean', 'structure'])

            if 'clean' in steps:
                self.logger.info("--- Starting Step 1: Content Extraction ---")
                extractor = ContentExtractor(
                    raw_data_dir=str(self.config.data_config.raw_dir),
                    cleaned_data_dir=str(self.config.data_config.cleaned_dir)
                )
                extractor.run()
                self.logger.info("--- Content Extraction Complete ---")

            if 'structure' in steps:
                self.logger.info("--- Starting Step 2: Data Structuring ---")
                structurer = DataStructurer(config=self.config, api_manager=self.api_manager, concurrency=2)
                structurer.cleaned_data_dir = Path(self.config.data_config.cleaned_dir)
                await structurer.run()
                self.logger.info("--- Data Structuring Complete ---")

            return True
            
        except Exception as e:
            self.logger.error(f"❌ An error occurred during pipeline processing: {e}", exc_info=True)
            return False

    async def run_test(self) -> bool:
        """Placeholder for a test run. For now, it just runs the main pipeline."""
        self.logger.info("🧪 Running in Test Mode...")
        # In a real scenario, this would run with a smaller subset of data
        # or specific test cases. For now, it mirrors the main run.
        return await self.run()

    async def validate_setup(self) -> bool:
        """Placeholder for a setup validation run."""
        self.logger.info("🔍 Validating pipeline setup...")
        # This could include checks for API key validity, directory permissions, etc.
        # For now, we'll just check if the directories can be created.
        return await self._setup_pipeline()
