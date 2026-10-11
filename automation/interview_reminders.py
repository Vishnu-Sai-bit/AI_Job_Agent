"""
==========================================================
Automation - Interview Reminders
==========================================================
"""

from typing import List, Dict, Any

def get_upcoming_interview_reminders(applications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [a for a in applications if a.get("stage") == "interview"]
