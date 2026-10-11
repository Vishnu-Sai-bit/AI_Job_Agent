"""
==========================================================
Integrations - Calendar Client
==========================================================
"""

from typing import Dict, Any

class CalendarClient:
    def schedule_interview_event(self, title: str, start_iso: str, company: str) -> Dict[str, Any]:
        return {"event": title, "start": start_iso, "company": company, "created": True}

calendar_client = CalendarClient()
