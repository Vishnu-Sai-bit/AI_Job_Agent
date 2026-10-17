"""
==========================================================
iCIMS ATS Provider Adapter
Captures: Company career site exact job-detail link and job identifier.
Documentation: https://community.icims.com/
==========================================================
"""

import re
from typing import Dict, Any, Optional
from services.job_links.normalizer import normalize_job, basic_url_check

class ICIMSAdapter:
    PROVIDER_NAME = "iCIMS"

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
        Normalize and verify an iCIMS job posting.
        Extracts job ID from standard iCIMS URL pattern: .../jobs/{job_id}/job
        """
        if not basic_url_check(official_url):
            raise ValueError(f"Invalid iCIMS URL syntax: {official_url}")

        ext_id = job_id
        if not ext_id:
            m = re.search(r'/jobs/(\d+)/', official_url)
            if m:
                ext_id = m.group(1)
            else:
                m_num = re.search(r'(\d{4,})', official_url)
                ext_id = m_num.group(1) if m_num else "ICIMS-JOB"

        apply_url = re.sub(r'/job(?:\?.*)?$', '/apply', official_url)
        if apply_url == official_url:
            apply_url = f"{official_url.rstrip('/')}/apply"

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
            "url_verified": bool("icims" in official_url.lower())
        }
        return normalize_job(raw_job, provider=cls.PROVIDER_NAME)
