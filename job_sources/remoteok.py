"""
==========================================================
Job Sources - RemoteOK Provider
==========================================================
"""

from typing import List, Dict, Any
from job_sources.base import BaseJobSource
import requests

class RemoteOKSource(BaseJobSource):
    @property
    def source_name(self) -> str:
        return "RemoteOK"

    def fetch_jobs(self, role: str, location: str) -> List[Dict[str, Any]]:
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            resp = requests.get("https://remoteok.com/api", headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return [d for d in data if isinstance(d, dict) and "position" in d]
        except Exception:
            pass
        return []
