"""
==========================================================
Job Sources - Quality Verification
==========================================================
"""

from typing import Dict, Any

def verify_job_integrity(job: Dict[str, Any]) -> bool:
    has_title = bool(job.get("title"))
    has_company = bool(job.get("company"))
    return has_title and has_company
