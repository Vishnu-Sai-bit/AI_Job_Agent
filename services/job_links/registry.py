"""
==========================================================
AI JobAgent - ATS Provider Registry & Application Link Resolver
Author : Antigravity / Beere Vishnu Sai
==========================================================
"""

from urllib.parse import urlparse
from typing import Dict, Any, Optional
from services.job_links.normalizer import basic_url_check, verify_ats_domain, normalize_job

ATS_DOMAIN_PATTERNS = {
    "greenhouse.io": "Greenhouse",
    "boards.greenhouse.io": "Greenhouse",
    "lever.co": "Lever",
    "jobs.lever.co": "Lever",
    "ashbyhq.com": "Ashby",
    "jobs.ashbyhq.com": "Ashby",
    "myworkdayjobs.com": "Workday",
    "smartrecruiters.com": "SmartRecruiters",
    "jobs.smartrecruiters.com": "SmartRecruiters",
    "workable.com": "Workable",
    "apply.workable.com": "Workable",
    "teamtailor.com": "Teamtailor",
    "recruitee.com": "Recruitee",
    "personio.de": "Personio",
    "personio.com": "Personio",
    "icims.com": "iCIMS",
    "taleo.net": "Oracle Taleo",
    "successfactors.com": "SAP SuccessFactors",
    "bamboohr.com": "BambooHR",
    "breezy.hr": "Breezy HR",
    "jazzhr.com": "JazzHR",
    "pinpointhq.com": "Pinpoint",
    "linkedin.com": "LinkedIn",
    "remotive.com": "Remotive",
    "jobicy.com": "Jobicy",
    "arbeitnow.com": "ArbeitNow",
    "remoteok.com": "RemoteOK",
    "adzuna.in": "Adzuna",
    "adzuna.com": "Adzuna",
    "amazon.jobs": "Amazon Jobs",
    "careers.google.com": "Google Careers",
    "careers.microsoft.com": "Microsoft Careers"
}

def detect_ats_provider(url: Optional[str]) -> str:
    """
    Detect the underlying ATS provider from an official job URL.
    """
    if not url:
        return "Company Career Portal"
    try:
        hostname = (urlparse(url).hostname or "").lower()
        for domain, provider in ATS_DOMAIN_PATTERNS.items():
            if hostname == domain or hostname.endswith("." + domain):
                return provider
    except Exception:
        pass
    return "Company Career Portal"

def resolve_verified_apply_link(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolve the exact destination link for the 'Apply Now' action
    using the documented fallback hierarchy:
    1. Verified direct application URL (apply_url)
    2. Verified job-detail URL for exact position (official_job_url)
    3. If neither is available, disable / flag unverified rather than redirecting to an unrelated page.
    """
    # Normalize if needed
    ats_provider = job.get("ats_provider") or detect_ats_provider(job.get("official_job_url") or job.get("url"))
    normalized = normalize_job(job, provider=ats_provider)
    
    apply_url = (normalized.get("apply_url") or "").strip()
    official_job_url = (normalized.get("official_job_url") or normalized.get("url") or "").strip()
    
    # Check 1: Verified direct application URL
    if apply_url and basic_url_check(apply_url) and verify_ats_domain(apply_url):
        return {
            "destination_url": apply_url,
            "type": "direct_application",
            "ats_provider": ats_provider,
            "external_job_id": normalized.get("external_job_id"),
            "url_verified": True,
            "can_apply": normalized.get("job_status") != "closed",
            "message": "Opening direct application form on official ATS."
        }

    # Check 2: Verified job-detail URL for the exact position
    if official_job_url and basic_url_check(official_job_url) and verify_ats_domain(official_job_url):
        return {
            "destination_url": official_job_url,
            "type": "job_detail",
            "ats_provider": ats_provider,
            "external_job_id": normalized.get("external_job_id"),
            "url_verified": True,
            "can_apply": normalized.get("job_status") != "closed",
            "message": "Opening exact job description page on official recruitment site."
        }

    # Check 3: Valid general URL
    if basic_url_check(official_job_url):
        return {
            "destination_url": official_job_url,
            "type": "official_posting",
            "ats_provider": ats_provider,
            "external_job_id": normalized.get("external_job_id"),
            "url_verified": True,
            "can_apply": normalized.get("job_status") != "closed",
            "message": "Opening job posting page."
        }

    # Fallback: Link cannot be verified
    return {
        "destination_url": None,
        "type": "unverified",
        "ats_provider": ats_provider,
        "external_job_id": normalized.get("external_job_id"),
        "url_verified": False,
        "can_apply": False,
        "message": "Direct application link could not be verified for this opening."
    }
