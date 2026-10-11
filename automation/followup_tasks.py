"""
==========================================================
Automation - Follow-up Tasks
==========================================================
"""

from typing import List, Dict, Any

def check_pending_followups(applications: List[Dict[str, Any]], days_threshold: int = 5) -> List[Dict[str, Any]]:
    due = []
    for app in applications:
        if app.get("stage") in ("saved", "applied"):
            due.append(app)
    return due
