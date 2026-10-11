"""
==========================================================
AI Engine Resume - ATS Analyzer
==========================================================
"""

from typing import Any
from services.ats.ats_calculator import calculate_ats

def run_ats_diagnostic(resume_data: Any) -> Any:
    return calculate_ats(resume_data)
