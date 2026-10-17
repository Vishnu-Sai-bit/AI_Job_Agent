"""
==========================================================
Personio ATS Provider Adapter
Captures: position ID and the published job's career-site URL.
Documentation: https://developer.personio.de/
==========================================================
"""

from typing import Dict, Any, Optional
from services.job_links.normalizer import normalize_job

class PersonioAdapter:
    PROVIDER_NAME = "Personio"

    @classmethod
    def parse_job(cls, item: Dict[str, Any], company_name: str = "Company", company_slug: str = "") -> Dict[str, Any]:
        """
        Normalize Personio position into standard ATS format.
        """
        pos_id = str(item.get("id") or "")
        c_slug = company_slug or company_name.lower().replace(" ", "")

        official_url = item.get("career_url") or item.get("url") or f"https://{c_slug}.jobs.personio.de/job/{pos_id}"
        apply_url = item.get("apply_url") or f"{official_url}#apply"

        title = item.get("name") or item.get("title") or "Role"
        loc_data = item.get("office") or item.get("location") or "Hybrid"

        raw_job = {
            "company_name": company_name,
            "job_title": title,
            "external_job_id": pos_id,
            "official_job_url": official_url,
            "apply_url": apply_url,
            "source_url": official_url,
            "ats_provider": cls.PROVIDER_NAME,
            "location": loc_data,
            "job_status": "open",
            "url_verified": bool("personio" in official_url.lower())
        }
        return normalize_job(raw_job, provider=cls.PROVIDER_NAME)
