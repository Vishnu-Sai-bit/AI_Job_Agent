"""
==========================================================
AI Job Agent - Job Service (job_service.py)
Validates official URLs, checks reachability, selects direct
application destinations, and saves normalized vacancies.
==========================================================
"""

from urllib.parse import urlparse
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import requests

from models import db, Job

# Pre-approved ATS domains and verified enterprise career platforms
ALLOWED_HOSTS = {
    # Greenhouse
    "greenhouse.io",
    "boards.greenhouse.io",
    "job-boards.greenhouse.io",
    # Lever
    "lever.co",
    "jobs.lever.co",
    # Workday
    "myworkdayjobs.com",
    # Direct Company Career Platforms
    "accenture.com",
    "oraclecloud.com",
    "ashbyhq.com",
    "smartrecruiters.com",
    "remotive.com",
    "remoteok.com",
    "arbeitnow.com",
    "google.com",
    "microsoft.com",
    "amazon.jobs",
    "target.com",
    "salesforce.com",
    "adobe.com",
    "autodesk.com",
    "mastercard.com",
    "spotify.com",
    "infosys.com",
}


def validate_official_url(url: Optional[str]) -> bool:
    """
    Validates that a URL is HTTPS, contains no embedded credentials,
    has a non-empty path, and belongs to an approved employer or ATS domain.
    Does not accept arbitrary URLs supplied by third-party aggregators.
    """
    if not url:
        return False
    try:
        parsed = urlparse(url.strip())
        host = (parsed.hostname or "").lower()
        if parsed.scheme != "https":
            return False
        if parsed.username or parsed.password:
            return False
        # Exact host or a genuine subdomain of an allowed host
        allowed = any(
            host == domain or host.endswith("." + domain)
            for domain in ALLOWED_HOSTS
        )
        return allowed and bool(parsed.path and parsed.path != "/")
    except (ValueError, AttributeError):
        return False


def select_apply_url(job: Job) -> Optional[str]:
    """
    Selects the authentic application URL for the job.
    Prioritizes 'apply_url' if valid, falling back to 'original_url'.
    Never returns an unapproved or invalid URL.
    """
    if not job:
        return None

    if job.apply_url and validate_official_url(job.apply_url):
        return job.apply_url.strip()

    if job.original_url and validate_official_url(job.original_url):
        return job.original_url.strip()

    return None


def check_job_link(url: str, timeout: float = 10.0) -> str:
    """
    Basic HTTP check for a URL on a pre-approved host.
    Does not follow redirects blindly.
    Returns: 'reachable', 'redirect_review', 'unavailable', 'invalid', or 'unknown'
    """
    if not validate_official_url(url):
        return "invalid"

    try:
        response = requests.get(
            url,
            timeout=timeout,
            allow_redirects=False,
            headers={
                "User-Agent": "AIJobAgent-LinkChecker/1.0"
            },
            stream=True,
        )
        status = response.status_code
        response.close()

        if 200 <= status < 300:
            return "reachable"
        if status in (301, 302, 303, 307, 308):
            # Inspect Location separately. Never follow it blindly.
            return "redirect_review"
        if status in (404, 410):
            return "unavailable"
        return "unknown"
    except (requests.RequestException, Exception):
        return "unknown"


def save_job(data: Dict[str, Any]) -> Job:
    """
    Normalizes source data and saves/updates it in the database.
    Expected fields:
        source_platform, source_job_id, company_name, title,
        original_url, apply_url (optional), location (optional),
        posted_at (optional), is_active (optional), link_status (optional)
    """
    source = str(data.get("source_platform") or "").strip().lower()
    source_id = str(data.get("source_job_id") or "").strip()
    company_name = str(data.get("company_name") or "").strip()
    title = str(data.get("title") or "").strip()
    original_url = str(data.get("original_url") or "").strip()

    if not source_id:
        raise ValueError("Missing original source job ID")

    if not validate_official_url(original_url):
        raise ValueError("Unapproved official job URL")

    apply_url = data.get("apply_url")
    if apply_url:
        apply_url = apply_url.strip()
        # An invalid application URL must not override a valid job URL
        if not validate_official_url(apply_url):
            apply_url = None

    location = data.get("location")
    if location:
        location = str(location).strip()

    posted_at = data.get("posted_at")
    if isinstance(posted_at, str) and posted_at:
        try:
            posted_at = datetime.fromisoformat(posted_at.replace("Z", "+00:00"))
        except Exception:
            posted_at = datetime.now(timezone.utc)
    elif not isinstance(posted_at, datetime):
        posted_at = datetime.now(timezone.utc)

    is_active = bool(data.get("is_active", True))
    link_status = str(data.get("link_status", "unverified")).strip()

    # Deduplication check by (source_platform, source_job_id)
    job = Job.query.filter_by(
        source_platform=source,
        source_job_id=source_id
    ).first()

    now = datetime.now(timezone.utc)

    if job is None:
        job = Job(
            source_platform=source,
            source_job_id=source_id,
            company_name=company_name,
            title=title,
            location=location,
            original_url=original_url,
            apply_url=apply_url,
            posted_at=posted_at,
            first_seen_at=now,
            last_verified_at=now if link_status == "verified" else None,
            is_active=is_active,
            link_status=link_status,
        )
        db.session.add(job)
    else:
        # Update existing record
        job.company_name = company_name
        job.title = title
        job.location = location
        job.original_url = original_url
        if apply_url:
            job.apply_url = apply_url
        job.posted_at = posted_at
        job.is_active = is_active
        job.link_status = link_status
        if link_status == "verified":
            job.last_verified_at = now

    db.session.commit()
    return job
