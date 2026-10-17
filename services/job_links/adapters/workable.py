"""
==========================================================
Workable ATS Provider Adapter
Captures: url, application_url, and job ID (shortcode).
Documentation: https://workable.readme.io/
==========================================================
"""

import requests
from typing import List, Dict, Any, Optional
from services.job_links.normalizer import normalize_job

class WorkableAdapter:
    PROVIDER_NAME = "Workable"

    @classmethod
    def fetch_jobs(cls, company_subdomain: str, company_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch published job openings from Workable public widget/API feed.
        """
        url = f"https://apply.workable.com/api/v3/accounts/{company_subdomain}/jobs"
        jobs = []
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("results", []):
                    jobs.append(cls.parse_job(item, company_name=company_name or company_subdomain.title(), company_subdomain=company_subdomain))
        except Exception:
            pass
        return jobs

    @classmethod
    def parse_job(cls, item: Dict[str, Any], company_name: str = "Company", company_subdomain: str = "") -> Dict[str, Any]:
        """
        Normalize raw Workable JSON item into standard ATS job format.
        Preserves official job URL and direct application URL separately.
        """
        shortcode = str(item.get("shortcode") or item.get("id") or "")
        subdomain = company_subdomain or item.get("account", {}).get("subdomain") or company_name.lower().replace(" ", "")
        
        official_url = item.get("url") or f"https://apply.workable.com/{subdomain}/j/{shortcode}/"
        apply_url = item.get("application_url") or f"{official_url.rstrip('/')}/apply"

        loc_data = item.get("location") or {}
        location = loc_data.get("city") or item.get("city") or "Remote"

        raw_job = {
            "company_name": company_name,
            "job_title": item.get("title", "Role"),
            "external_job_id": shortcode,
            "official_job_url": official_url,
            "apply_url": apply_url,
            "source_url": official_url,
            "ats_provider": cls.PROVIDER_NAME,
            "location": location,
            "job_status": "open",
            "url_verified": True
        }
        return normalize_job(raw_job, provider=cls.PROVIDER_NAME)
