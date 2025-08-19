#!/usr/bin/env python3
"""
SetForge Q&A Validator
"""

import json
from logging import Logger
from typing import Any, Dict

from src.utils.api_client_manager import APIClientManager


class QAEvaluator:
    """
    A class to evaluate the quality of generated Q&A pairs.
    """

    def __init__(self, api_manager: APIClientManager, logger: Logger):
        self.api_manager = api_manager
        self.logger = logger

    async def validate_qa_pair(self, source_content: Dict[str, Any], qa_pair: Dict[str, Any]) -> bool:
        """
        Validates a Q&A pair by checking if each sentence in the answer is a subset of the source content.
        """
        source_text = json.dumps(source_content).lower()
        answer_text = qa_pair.get("answer", "").lower()

        # Split the answer into sentences
        sentences = [s.strip() for s in answer_text.split('.') if s.strip()]

        # Check if each sentence is in the source text
        for sentence in sentences:
            if sentence not in source_text:
                self.logger.warning(f"Q&A pair failed validation. Sentence not found in source: '{sentence}'")
                return False
        
        return True
