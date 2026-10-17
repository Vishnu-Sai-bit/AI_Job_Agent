"""
==========================================================
AI JobAgent - ATS Job Links Normalizer
Author : Antigravity / Beere Vishnu Sai
==========================================================
"""

from urllib.parse import urlparse
from datetime import datetime, timezone
from typing import Dict, Any, Optional

APPROVED_ATS_DOMAINS = [
    "greenhouse.io",
    "boards.greenhouse.io",
    "boards-api.greenhouse.io",
    "lever.co",
    "jobs.lever.co",
    "api.lever.co",
    "ashbyhq.com",
    "jobs.ashbyhq.com",
    "myworkdayjobs.com",
    "smartrecruiters.com",
    "jobs.smartrecruiters.com",
    "workable.com",
    "apply.workable.com",
    "teamtailor.com",
    "recruitee.com",
    "personio.de",
    "personio.com",
    "icims.com",
    "taleo.net",
    "successfactors.com",
    "bamboohr.com",
    "breezy.hr",
    "jazzhr.com",
    "pinpointhq.com",
    "linkedin.com",
    "remotive.com",
    "jobicy.com",
    "arbeitnow.com",
    "remoteok.com",
    "adzuna.in",
    "adzuna.com",
    "amazon.jobs",
    "careers.google.com",
    "careers.microsoft.com"
]

def basic_url_check(url: Optional[str]) -> bool:
    """Basic URL syntax check; not proof that a link is official."""
    if not url:
        return False
    try:
        parsed = urlparse(url.strip())
        return (
            parsed.scheme in ("https", "http")
            and bool(parsed.hostname)
            and not parsed.username
            and not parsed.password
        )
    except Exception:
        return False

def verify_ats_domain(url: Optional[str]) -> bool:
    """
    Check if a URL matches an approved ATS or official recruitment domain.
    """
    if not basic_url_check(url):
        return False
    try:
        hostname = (urlparse(url).hostname or "").lower()
        return any(hostname == domain or hostname.endswith("." + domain) for domain in APPROVED_ATS_DOMAINS)
    except Exception:
        return False

def normalize_job(raw_job: Dict[str, Any], provider: str = "custom") -> Dict[str, Any]:
    """
    Convert provider-specific job data into our common ATS-aware format.
    Pass URLs returned by an official source or verified listing.
    Do not manufacture URLs from a job ID alone.
    """
    company = raw_job.get("company_name") or raw_job.get("company") or "Company"
    title = raw_job.get("job_title") or raw_job.get("title") or "Role"
    job_id = str(raw_job.get("external_job_id") or raw_job.get("job_id") or raw_job.get("id") or "")
    
    official_job_url = raw_job.get("official_job_url") or raw_job.get("job_url") or raw_job.get("url") or ""
    apply_url = raw_job.get("apply_url") or ""
    source_url = raw_job.get("source_url") or raw_job.get("source") or official_job_url
    
    # Verification check
    url_verified = raw_job.get("url_verified")
    if url_verified is None:
        url_verified = basic_url_check(official_job_url) and verify_ats_domain(official_job_url)

    now_iso = datetime.now(timezone.utc).isoformat()
    
    return {
        "id": raw_job.get("id", job_id),
        "company": company,
        "company_name": company,
        "title": title,
        "job_title": title,
        "ats_provider": raw_job.get("ats_provider") or provider,
        "external_job_id": job_id,
        "job_id": job_id,
        "official_job_url": official_job_url,
        "apply_url": apply_url,
        "url": official_job_url,
        "source_url": source_url,
        "source": raw_job.get("source", provider.title()),
        "url_verified": bool(url_verified),
        "last_verified_at": raw_job.get("last_verified_at") or now_iso,
        "job_status": raw_job.get("job_status") or raw_job.get("status") or "open",
        "location": raw_job.get("location", "Remote / Hybrid"),
        "skills": raw_job.get("skills", []),
        "experience": raw_job.get("experience", "1-3 yrs"),
        "description": raw_job.get("description", f"Verified opening for {title} at {company}.")
    }
