"""
==========================================================
AI Job Copilot - File Utilities
==========================================================
"""

from pathlib import Path
from typing import Optional

def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path

def safe_read_text(path: Path, encoding: str = "utf-8") -> Optional[str]:
    try:
        return path.read_text(encoding=encoding)
    except Exception:
        return None
