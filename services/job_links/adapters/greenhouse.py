"""
==========================================================
Greenhouse ATS Provider Adapter
API Pattern: https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs
==========================================================
"""

import requests
from typing import List, Dict, Any, Optional
from services.job_links.normalizer import normalize_job

class GreenhouseAdapter:
    PROVIDER_NAME = "Greenhouse"

    @classmethod
    def fetch_jobs(cls, board_token: str, company_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch published job openings directly from Greenhouse Job Board API.
        """
        url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
        jobs = []
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("jobs", []):
                    jobs.append(cls.parse_job(item, company_name=company_name or board_token.title()))
        except Exception:
            pass
        return jobs

    @classmethod
    def parse_job(cls, item: Dict[str, Any], company_name: str = "Company") -> Dict[str, Any]:
        """
        Normalize raw Greenhouse JSON response item into standard ATS job format.
        """
        ext_id = str(item.get("id", ""))
        official_url = item.get("absolute_url") or f"https://boards.greenhouse.io/embed/job_app?token={ext_id}"
        apply_url = f"{official_url}#app" if "#" not in official_url else official_url

        loc_data = item.get("location")
        loc_str = loc_data.get("name") if isinstance(loc_data, dict) else (loc_data or "Remote")

        raw_job = {
            "company_name": company_name,
            "job_title": item.get("title", "Role"),
            "external_job_id": ext_id,
            "official_job_url": official_url,
            "apply_url": apply_url,
            "source_url": official_url,
            "ats_provider": cls.PROVIDER_NAME,
            "location": loc_str,
            "job_status": "open",
            "url_verified": True
        }
        return normalize_job(raw_job, provider=cls.PROVIDER_NAME)
