import logging
import os
from rich.logging import RichHandler

def setup_logging(log_level: str = "INFO", log_file: str = 'setforge_production.log', enable_progress: bool = True) -> logging.Logger:
    """
    Set up centralized logging with RichHandler for better console output.
    """
    # Determine if progress tracking should be enabled
    progress_enabled = enable_progress and os.getenv('CI') is None

    # Configure RichHandler with or without progress tracking
    handler = RichHandler(
        rich_tracebacks=True,
        show_time=True,
        show_path=False,
        enable_link_path=False,
        markup=True,
        log_time_format="[%X]",
        show_level=True,
    )

    # Set up basic configuration
    logging.basicConfig(
        level=log_level.upper(),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[handler]
    )

    # Get the root logger and add a file handler
    logger = logging.getLogger("SetForge")
    logger.setLevel(log_level.upper())

    # Add file handler to save logs
    if log_file:
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)

    # Set the level for other loggers to WARNING to reduce noise
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return logger
