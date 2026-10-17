"""
==========================================================
Recruitee ATS Provider Adapter
Captures: careers_url, careers_apply_url, and offer ID.
Documentation: https://docs.recruitee.com/
==========================================================
"""

from typing import Dict, Any, Optional
from services.job_links.normalizer import normalize_job

class RecruiteeAdapter:
    PROVIDER_NAME = "Recruitee"

    @classmethod
    def parse_job(cls, item: Dict[str, Any], company_name: str = "Company") -> Dict[str, Any]:
        """
        Normalize Recruitee offer into standard ATS job format.
        """
        offer_id = str(item.get("id") or item.get("slug") or "")
        official_url = item.get("careers_url") or item.get("url") or ""
        apply_url = item.get("careers_apply_url") or (f"{official_url.rstrip('/')}/apply" if official_url else "")

        title = item.get("title") or "Role"
        location = item.get("location") or item.get("city") or "Remote"

        raw_job = {
            "company_name": company_name,
            "job_title": title,
            "external_job_id": offer_id,
            "official_job_url": official_url,
            "apply_url": apply_url,
            "source_url": official_url,
            "ats_provider": cls.PROVIDER_NAME,
            "location": location,
            "job_status": "open",
            "url_verified": bool(official_url and "recruitee" in official_url.lower())
        }
        return normalize_job(raw_job, provider=cls.PROVIDER_NAME)
