"""
==========================================================
Job Sources - Arbeitnow Provider
==========================================================
"""

from typing import List, Dict, Any
from job_sources.base import BaseJobSource
import requests

class ArbeitnowSource(BaseJobSource):
    @property
    def source_name(self) -> str:
        return "Arbeitnow"

    def fetch_jobs(self, role: str, location: str) -> List[Dict[str, Any]]:
        url = "https://www.arbeitnow.com/api/job-board-api"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("data", [])
        except Exception:
            pass
        return []
