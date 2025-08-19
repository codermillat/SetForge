from dataclasses import dataclass, field
import time
from typing import Any, Dict, Optional

def get_default_metadata() -> Dict[str, Any]:
    """Returns a default metadata dictionary."""
    return {
        "source_file": "unknown",
        "persona": "unknown",
        "difficulty": "unknown",
    }

@dataclass
class QAPair:
    """Enhanced Q&A pair with comprehensive metadata"""
    question: str
    answer: str
    context: str
    model_used: str
    api_account: str
    generation_method: str  # 'template', 'llm', 'hybrid'
    language: str  # 'en', 'bn', 'bn-en'
    quality_score: float
    semantic_score: float
    cultural_relevance: float
    edge_case_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=get_default_metadata)
    timestamp: float = field(default_factory=time.time)
