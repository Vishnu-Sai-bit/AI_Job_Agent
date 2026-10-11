"""
==========================================================
AI Engine Job Matching - Matcher
==========================================================
"""

from typing import Dict, Any, List
from app.services.matching_service import matching_service

def match_job_candidate(job: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
    return matching_service.calculate_match(job, candidate)
