"""
==========================================================
AI Engine Agent - Application Agent
==========================================================
"""

from typing import Dict, Any

class ApplicationAgent:
    """Automates application materials and recruiter follow-up messaging."""

    def draft_followup(self, candidate_name: str, company: str, role: str) -> str:
        from app.services.application_service import application_service
        return application_service.create_followup(candidate_name, company, role, "recent")

application_agent = ApplicationAgent()
