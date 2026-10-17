"""
==========================================================
Teamtailor ATS Provider Adapter
Captures: careersite-job-url, careersite-job-apply-url, and job ID.
Documentation: https://docs.teamtailor.com/
==========================================================
"""

from typing import Dict, Any, Optional
from services.job_links.normalizer import normalize_job

class TeamtailorAdapter:
    PROVIDER_NAME = "Teamtailor"

    @classmethod
    def parse_job(cls, item: Dict[str, Any], company_name: str = "Company") -> Dict[str, Any]:
        """
        Normalize Teamtailor job data into standard ATS format.
        Reads careersite-job-url and careersite-job-apply-url from links/attributes.
        """
        job_id = str(item.get("id") or "")
        links = item.get("links") or {}
        attributes = item.get("attributes") or {}

        official_url = (
            links.get("careersite-job-url")
            or attributes.get("careersite-job-url")
            or item.get("careersite_job_url")
            or item.get("url")
            or ""
        )
        apply_url = (
            links.get("careersite-job-apply-url")
            or attributes.get("careersite-job-apply-url")
            or item.get("careersite_job_apply_url")
            or (f"{official_url.rstrip('/')}/apply" if official_url else "")
        )

        title = attributes.get("title") or item.get("title") or "Role"
        location = attributes.get("location") or item.get("location") or "Remote"

        raw_job = {
            "company_name": company_name,
            "job_title": title,
            "external_job_id": job_id,
            "official_job_url": official_url,
            "apply_url": apply_url,
            "source_url": official_url,
            "ats_provider": cls.PROVIDER_NAME,
            "location": location,
            "job_status": "open",
            "url_verified": bool(official_url and "teamtailor" in official_url.lower())
        }
        return normalize_job(raw_job, provider=cls.PROVIDER_NAME)
