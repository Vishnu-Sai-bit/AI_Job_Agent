"""
==========================================================
AI Engine LLM - Output Parser
==========================================================
"""

import json
from typing import Dict, Any, Optional

def parse_json_response(raw_response: str) -> Optional[Dict[str, Any]]:
    cleaned = raw_response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    try:
        return json.loads(cleaned.strip())
    except Exception:
        return None
