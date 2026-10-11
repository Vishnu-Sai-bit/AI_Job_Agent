"""
==========================================================
AI Engine Resume - Parser
==========================================================
"""

from typing import Dict, Any
from services.resume.resume_analyzer import analyze_resume

def parse_resume_content(raw_text: str) -> Any:
    return analyze_resume(raw_text)
