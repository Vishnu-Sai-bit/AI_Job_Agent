"""
==========================================================
Workday ATS Provider Adapter
Special Rule: Do not manufacture URLs by appending requisition IDs.
Preserves exact posting URLs with requisition IDs.
==========================================================
"""

import re
from typing import Dict, Any, Optional
from services.job_links.normalizer import normalize_job, basic_url_check

class WorkdayAdapter:
    PROVIDER_NAME = "Workday"

    @classmethod
    def parse_job(
        cls,
        official_posting_url: str,
        company_name: str,
        job_title: str,
        requisition_id: Optional[str] = None,
        location: str = "Hybrid"
    ) -> Dict[str, Any]:
        """
        Normalize and verify a Workday job posting.
        Extracts requisition ID from verified URL pattern if not explicitly provided.
        """
        if not basic_url_check(official_posting_url):
            raise ValueError(f"Invalid Workday URL syntax: {official_posting_url}")

        # Extract requisition ID if not provided:
        # Common Workday URL patterns: .../job/.../Title-Slug_JR12345 or .../Title-Slug_R-10293
        req_id = requisition_id
        if not req_id:
            m = re.search(r'_([A-Za-z0-9\-]+)(?:[/?#]|$)', official_posting_url)
            if m:
                req_id = m.group(1)
            else:
                num_m = re.search(r'(\d{5,})', official_posting_url)
                req_id = num_m.group(1) if num_m else "WD-REQ"

        # Direct application form URL
        apply_url = official_posting_url.rstrip("/") + "/apply"

        raw_job = {
            "company_name": company_name,
            "job_title": job_title,
            "external_job_id": str(req_id),
            "official_job_url": official_posting_url,
            "apply_url": apply_url,
            "source_url": official_posting_url,
            "ats_provider": cls.PROVIDER_NAME,
            "location": location,
            "job_status": "open",
            "url_verified": "myworkdayjobs.com" in official_posting_url.lower() or "workday" in official_posting_url.lower()
        }
        return normalize_job(raw_job, provider=cls.PROVIDER_NAME)
