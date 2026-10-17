"""
==========================================================
Ashby ATS Provider Adapter
API Pattern: https://api.ashbyhq.com/posting-api/job-board/{job_board_name}
==========================================================
"""

import requests
from typing import List, Dict, Any, Optional
from services.job_links.normalizer import normalize_job

class AshbyAdapter:
    PROVIDER_NAME = "Ashby"

    @classmethod
    def fetch_jobs(cls, job_board_name: str, company_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch published job openings directly from Ashby Job Board API.
        """
        url = f"https://api.ashbyhq.com/posting-api/job-board/{job_board_name}"
        jobs = []
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("jobs", []):
                    jobs.append(cls.parse_job(item, company_name=company_name or job_board_name.title()))
        except Exception:
            pass
        return jobs

    @classmethod
    def parse_job(cls, item: Dict[str, Any], company_name: str = "Company") -> Dict[str, Any]:
        """
        Normalize raw Ashby JSON response item into standard ATS job format.
        """
        ext_id = str(item.get("id", ""))
        official_url = item.get("jobUrl") or f"https://jobs.ashbyhq.com/{company_name.lower()}/{ext_id}"
        apply_url = item.get("applyUrl") or f"{official_url}/application"

        location = item.get("location") or "Remote"

        raw_job = {
            "company_name": company_name,
            "job_title": item.get("title", "Role"),
            "external_job_id": ext_id,
            "official_job_url": official_url,
            "apply_url": apply_url,
            "source_url": official_url,
            "ats_provider": cls.PROVIDER_NAME,
            "location": location,
            "job_status": "open",
            "url_verified": True
        }
        return normalize_job(raw_job, provider=cls.PROVIDER_NAME)
