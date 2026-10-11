"""
==========================================================
AI Engine Resume - Resume Tailor
==========================================================
"""

from typing import List, Dict, Any
from services.resume.resume_tailorer import tailor_resume_for_job

def tailor_resume(summary: str, target_role: str, target_company: str, job_desc: str, skills: List[str]) -> Any:
    return tailor_resume_for_job(
        original_resume_text=summary,
        target_role=target_role,
        target_company=target_company,
        job_description=job_desc,
        candidate_skills=skills
    )
