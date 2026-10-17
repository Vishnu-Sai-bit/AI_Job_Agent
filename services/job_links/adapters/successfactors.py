"""
==========================================================
SAP SuccessFactors ATS Provider Adapter
Captures: Actual posting URL and requisition ID.
Documentation: https://help.sap.com/docs/SAP_SUCCESSFACTORS_RECRUITING
==========================================================
"""

import re
from typing import Dict, Any, Optional
from services.job_links.normalizer import normalize_job, basic_url_check

class SuccessFactorsAdapter:
    PROVIDER_NAME = "SAP SuccessFactors"

    @classmethod
    def parse_job(
        cls,
        official_url: str,
        company_name: str,
        job_title: str,
        requisition_id: Optional[str] = None,
        location: str = "India"
    ) -> Dict[str, Any]:
        """
        Normalize and verify an SAP SuccessFactors job posting.
        Extracts requisition ID from deep-link or path pattern.
        """
        if not basic_url_check(official_url):
            raise ValueError(f"Invalid SuccessFactors URL syntax: {official_url}")

        req_id = requisition_id
        if not req_id:
            m = re.search(r'-(\d{5,})(?:[/?#]|$)', official_url)
            if m:
                req_id = m.group(1)
            else:
                m_num = re.search(r'(\d{6,})', official_url)
                req_id = m_num.group(1) if m_num else "SF-REQ"

        apply_url = f"{official_url.rstrip('/')}/apply"

        raw_job = {
            "company_name": company_name,
            "job_title": job_title,
            "external_job_id": str(req_id),
            "official_job_url": official_url,
            "apply_url": apply_url,
            "source_url": official_url,
            "ats_provider": cls.PROVIDER_NAME,
            "location": location,
            "job_status": "open",
            "url_verified": bool("successfactors" in official_url.lower() or "career" in official_url.lower())
        }
        return normalize_job(raw_job, provider=cls.PROVIDER_NAME)
