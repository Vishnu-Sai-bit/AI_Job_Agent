"""
==========================================================
AI Engine Agent - Interview Agent
==========================================================
"""

from typing import List, Dict, Any

class InterviewAgent:
    """Generates technical questions and scores mock responses."""

    def generate_questions(self, role: str, skills: List[str], company: str) -> List[Dict[str, Any]]:
        from app.services.interview_service import interview_service
        return interview_service.get_questions(role, skills, company)

interview_agent = InterviewAgent()
