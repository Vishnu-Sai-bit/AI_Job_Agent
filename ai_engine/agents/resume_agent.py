"""
==========================================================
AI Engine Agent - Resume Agent
==========================================================
"""

from pathlib import Path
from typing import Dict, Any

class ResumeAgent:
    """Manages document extraction and 6-dimension ATS quality diagnostics."""

    def analyze_resume(self, file_path: str) -> Dict[str, Any]:
        from app.services.resume_service import resume_service
        return resume_service.process_resume_file(Path(file_path))

resume_agent = ResumeAgent()
