import os
import logging
from pathlib import Path

logger = logging.getLogger("SetForge")

def validate_environment() -> bool:
    """
    Validate essential environment variables and directories.
    """
    # Validate API keys
    required_keys = [
        'GEMINI_API_KEY_1',
        'VERTEX_AI_PROJECT',
        'VERTEX_AI_LOCATION',
        'VERTEX_AI_MODEL'
    ]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    if missing_keys:
        logger.error(f"❌ Missing critical API keys: {', '.join(missing_keys)}")
        return False

    # Validate data directories
    raw_dir = Path(os.getenv('RAW_DATA_DIR', 'data_raw'))
    if not raw_dir.exists():
        logger.warning(f"Raw data directory not found at '{raw_dir}'. Creating it.")
        raw_dir.mkdir(parents=True, exist_ok=True)

    return True
