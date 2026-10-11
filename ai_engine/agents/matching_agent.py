"""
==========================================================
AI Engine Agent - Matching Agent
==========================================================
"""

from typing import Dict, Any

class MatchingAgent:
    """Calculates match scores and identifies missing skills."""

    def evaluate_fit(self, job: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
        from app.services.matching_service import matching_service
        return matching_service.calculate_match(job, candidate)

matching_agent = MatchingAgent()
