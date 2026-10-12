"""
==========================================================
AI Job Copilot - Text Processing Utilities
==========================================================
"""

import re
from typing import List

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_tokens(text: str) -> List[str]:
    cleaned = clean_text(text).lower()
    return re.findall(r"\b[a-zA-Z0-9+#.-]+\b", cleaned)
