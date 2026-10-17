"""
==========================================================
SmartRecruiters ATS Provider Adapter
API Pattern: https://api.smartrecruiters.com/v1/companies/{company}/postings
==========================================================
"""

import requests
from typing import List, Dict, Any, Optional
from services.job_links.normalizer import normalize_job

class SmartRecruitersAdapter:
    PROVIDER_NAME = "SmartRecruiters"

    @classmethod
    def fetch_jobs(cls, company_identifier: str, company_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch published job openings directly from SmartRecruiters Postings API.
        """
        url = f"https://api.smartrecruiters.com/v1/companies/{company_identifier}/postings"
        jobs = []
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("content", []):
                    jobs.append(cls.parse_job(item, company_name=company_name or company_identifier.title(), company_id=company_identifier))
        except Exception:
            pass
        return jobs

    @classmethod
    def parse_job(cls, item: Dict[str, Any], company_name: str = "Company", company_id: str = "") -> Dict[str, Any]:
        """
        Normalize raw SmartRecruiters item into standard ATS job format.
        """
        ext_id = str(item.get("id", ""))
        cid = company_id or company_name.lower().replace(" ", "")
        official_url = item.get("ref") or f"https://jobs.smartrecruiters.com/{cid}/{ext_id}"
        apply_url = f"https://jobs.smartrecruiters.com/{cid}/{ext_id}/apply"

        loc_data = item.get("location") or {}
        location = loc_data.get("city") or "Remote"

        raw_job = {
            "company_name": company_name,
            "job_title": item.get("name", "Role"),
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
