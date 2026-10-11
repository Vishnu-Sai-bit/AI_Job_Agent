"""
==========================================================
Job Sources - Remotive Provider
==========================================================
"""

from typing import List, Dict, Any
from job_sources.base import BaseJobSource
import requests

class RemotiveSource(BaseJobSource):
    @property
    def source_name(self) -> str:
        return "Remotive"

    def fetch_jobs(self, role: str, location: str) -> List[Dict[str, Any]]:
        url = "https://remotive.com/api/remote-jobs"
        try:
            resp = requests.get(url, params={"search": role, "limit": 20}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("jobs", [])
        except Exception:
            pass
        return []
