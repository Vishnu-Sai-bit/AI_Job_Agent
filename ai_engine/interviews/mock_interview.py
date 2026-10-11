"""
==========================================================
AI Engine Interviews - Mock Interview Session
==========================================================
"""

from typing import Dict, Any

class MockInterviewSession:
    def __init__(self, role: str, company: str):
        self.role = role
        self.company = company
        self.current_index = 0

    def start_session(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "company": self.company,
            "status": "in_progress"
        }
