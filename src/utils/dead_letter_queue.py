#!/usr/bin/env python3
"""
A simple dead-letter queue for handling failed file processing.
"""

import logging
from pathlib import Path
import shutil

logger = logging.getLogger("SetForge")

class DeadLetterQueue:
    """
    Manages a dead-letter queue for files that fail processing.
    """

    def __init__(self, queue_dir: str = "data/dead_letter_queue"):
        """
        Initializes the DeadLetterQueue.

        Args:
            queue_dir: The directory to store failed files.
        """
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)

    def add(self, filepath: Path, reason: str):
        """
        Adds a file to the dead-letter queue.

        Args:
            filepath: The path to the file that failed processing.
            reason: The reason for the failure.
        """
        try:
            destination = self.queue_dir / filepath.name
            shutil.move(str(filepath), str(destination))
            with open(destination.with_suffix('.txt'), 'w', encoding='utf-8') as f:
                f.write(f"File failed processing.\nReason: {reason}\n")
            logger.warning(f"Moved failed file {filepath.name} to dead-letter queue. Reason: {reason}")
        except Exception as e:
            logger.error(f"Failed to move {filepath.name} to dead-letter queue: {e}", exc_info=True)
