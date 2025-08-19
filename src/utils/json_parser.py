#!/usr/bin/env python3
"""
JSON Parsing Utilities for SetForge
"""

import json
import re
from typing import Dict, Any, Optional, Union

def extract_json_from_response(text: str) -> Optional[Union[Dict[str, Any], list[Any]]]:
    """
    Extracts a JSON object or array from a string, even if it's embedded in other text.
    
    Args:
        text: The string containing the JSON.

    Returns:
        The parsed JSON object (dict or list), or None if no valid JSON is found.
    """
    # Regex to find content between ```json and ```
    match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
    if match:
        text = match.group(1)

    # Regex to find content within the first '{' and last '}' or first '[' and last ']'
    match = re.search(r'\{[\s\S]*\}|\[[\s\S]*\]', text)
    if match:
        json_str = match.group(0).replace('undefined', 'null')
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback for malformed JSON that might be fixable
            try:
                # Attempt to fix common issues like trailing commas
                json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
                return json.loads(json_str)
            except json.JSONDecodeError:
                return None
    return None
