#!/usr/bin/env python3
"""
Provides a centralized and robust way to manage and access prompts.
"""

import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger("SetForge")

class PromptProvider:
    """
    Manages loading, caching, and providing access to prompts.
    """

    def __init__(self, prompt_dir: str = "src/prompts"):
        """
        Initializes the PromptProvider.

        Args:
            prompt_dir: The directory where prompt files are stored.
        """
        self.prompt_dir = Path(prompt_dir)
        self._prompt_cache: Dict[str, str] = {}
        self._load_all_prompts()

    def _load_all_prompts(self):
        """
        Loads all prompts from the specified directory into the cache.
        """
        if not self.prompt_dir.is_dir():
            logger.warning(f"Prompt directory not found: {self.prompt_dir}")
            return

        for prompt_file in self.prompt_dir.glob("*.txt"):
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompt_content = f.read()
                prompt_name = prompt_file.stem
                self._prompt_cache[prompt_name] = prompt_content
                logger.info(f"Loaded prompt: {prompt_name}")
            except Exception as e:
                logger.error(f"Error loading prompt {prompt_file}: {e}")

    def get_prompt(self, name: str) -> Optional[str]:
        """
        Retrieves a prompt by name from the cache.

        Args:
            name: The name of the prompt to retrieve (without the .txt extension).

        Returns:
            The prompt content as a string, or None if not found.
        """
        return self._prompt_cache.get(name)
