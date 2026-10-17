"""
==========================================================
Oracle Taleo ATS Provider Adapter
Captures: Career section and job identifier in supported job-detail or job-application URL.
Documentation: https://docs.oracle.com/en/cloud/saas/talent-management/
==========================================================
"""

import re
from typing import Dict, Any, Optional
from services.job_links.normalizer import normalize_job, basic_url_check

class TaleoAdapter:
    PROVIDER_NAME = "Oracle Taleo"

    @classmethod
    def parse_job(
        cls,
        official_url: str,
        company_name: str,
        job_title: str,
        job_id: Optional[str] = None,
        location: str = "India"
    ) -> Dict[str, Any]:
        """
        Normalize and verify an Oracle Taleo job posting.
        Extracts job ID from URL query parameters (e.g. ?job=12345 or /job/12345).
        """
        if not basic_url_check(official_url):
            raise ValueError(f"Invalid Taleo URL syntax: {official_url}")

        ext_id = job_id
        if not ext_id:
            m = re.search(r'[?&]job=(\d+)', official_url)
            if m:
                ext_id = m.group(1)
            else:
                m_num = re.search(r'/(\d{5,})(?:[/?#]|$)', official_url)
                ext_id = m_num.group(1) if m_num else "TALEO-JOB"

        # Direct application form in Taleo career section
        if "jobdetail.ftl" in official_url:
            apply_url = official_url.replace("jobdetail.ftl", "jobapply.ftl")
        elif official_url.endswith("/"):
            apply_url = f"{official_url}apply"
        else:
            apply_url = f"{official_url}/apply"

        raw_job = {
            "company_name": company_name,
            "job_title": job_title,
            "external_job_id": str(ext_id),
            "official_job_url": official_url,
            "apply_url": apply_url,
            "source_url": official_url,
            "ats_provider": cls.PROVIDER_NAME,
            "location": location,
            "job_status": "open",
            "url_verified": bool("taleo" in official_url.lower() or "oracle" in official_url.lower())
        }
        return normalize_job(raw_job, provider=cls.PROVIDER_NAME)
