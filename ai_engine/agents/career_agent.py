"""
==========================================================
AI Engine Agent - Career Agent
==========================================================
"""

from typing import List, Dict, Any

class CareerAgent:
    """Identifies market deficits and generates learning roadmaps."""

    def build_roadmap(self, role: str, skills: List[str]) -> Dict[str, Any]:
        from app.services.career_service import career_service
        return career_service.get_roadmap(role, skills)

career_agent = CareerAgent()
