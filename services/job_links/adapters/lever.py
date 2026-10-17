"""
==========================================================
Lever ATS Provider Adapter
API Pattern: https://api.lever.co/v0/postings/{site}?mode=json
==========================================================
"""

import requests
from typing import List, Dict, Any, Optional
from services.job_links.normalizer import normalize_job

class LeverAdapter:
    PROVIDER_NAME = "Lever"

    @classmethod
    def fetch_jobs(cls, site: str, company_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch published job openings directly from Lever Postings API.
        """
        url = f"https://api.lever.co/v0/postings/{site}?mode=json"
        jobs = []
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                postings = resp.json()
                for item in postings:
                    jobs.append(cls.parse_job(item, company_name=company_name or site.title()))
        except Exception:
            pass
        return jobs

    @classmethod
    def parse_job(cls, item: Dict[str, Any], company_name: str = "Company") -> Dict[str, Any]:
        """
        Normalize raw Lever JSON response item into standard ATS job format.
        """
        ext_id = str(item.get("id", ""))
        official_url = item.get("hostedUrl") or f"https://jobs.lever.co/{company_name.lower()}/{ext_id}"
        apply_url = item.get("applyUrl") or f"{official_url}/apply"

        categories = item.get("categories") or {}
        location = categories.get("location") or "Remote"

        raw_job = {
            "company_name": company_name,
            "job_title": item.get("text", "Role"),
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
