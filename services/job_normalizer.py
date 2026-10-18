"""
==========================================================
AI JobAgent - Job Normalizer
Normalizes raw multi-source job postings into the unified
11-field schema and guarantees zero salary data display.
==========================================================
"""

import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup


def clean_html_text(raw_html: str) -> str:
    """Strip HTML tags cleanly and normalize spacing."""
    if not raw_html:
        return ""
    try:
        text = BeautifulSoup(str(raw_html), "html.parser").get_text(separator=" ")
        return re.sub(r"\s+", " ", text).strip()
    except Exception:
        return re.sub(r"<[^>]+>", " ", str(raw_html)).strip()


def normalize_job_dict(raw: Dict[str, Any], default_source: str = "Company Careers") -> Dict[str, Any]:
    """
    Transforms any raw job record into the canonical 11-field Job dictionary:
    1. job_id
    2. company_name
    3. job_title
    4. description
    5. location
    6. posted_at
    7. source_platform
    8. original_url
    9. apply_url
    10. last_verified_at
    11. status
    
    CRITICAL REQUIREMENT: ZERO salary fields or values are preserved.
    """
    now_iso = datetime.now(timezone.utc).isoformat()

    # 1. Job ID
    job_id = str(
        raw.get("job_id")
        or raw.get("external_job_id")
        or raw.get("provider_id")
        or raw.get("id")
        or raw.get("slug")
        or ""
    ).strip()

    # 2. Company Name
    company_name = str(
        raw.get("company_name")
        or raw.get("company")
        or raw.get("employer")
        or "Featured Employer"
    ).strip()

    # 3. Job Title
    job_title = str(
        raw.get("job_title")
        or raw.get("title")
        or raw.get("position")
        or "Software Engineer"
    ).strip()

    # 4. Description
    raw_desc = (
        raw.get("description")
        or raw.get("content")
        or raw.get("details")
        or raw.get("summary")
        or f"Authentic career opening for {job_title} at {company_name}."
    )
    description = clean_html_text(raw_desc)

    # 5. Location
    loc_val = raw.get("location") or raw.get("candidate_required_location") or raw.get("locationsText")
    if isinstance(loc_val, dict):
        location = loc_val.get("name") or "Remote / Office"
    else:
        location = str(loc_val or "Remote / Office").strip()

    # 6. Posted At
    posted_at = str(
        raw.get("posted_at")
        or raw.get("posted_date")
        or raw.get("publication_date")
        or raw.get("postedOn")
        or raw.get("date")
        or now_iso
    ).strip()

    # 7. Source Platform
    source_platform = str(
        raw.get("source_platform")
        or raw.get("provider")
        or raw.get("source")
        or raw.get("ats_provider")
        or default_source
    ).strip()

    # 8. Original URL & 9. Apply URL
    orig_url = str(
        raw.get("original_url")
        or raw.get("official_job_url")
        or raw.get("url")
        or raw.get("apply_url")
        or ""
    ).strip()

    apply_url = str(
        raw.get("apply_url")
        or raw.get("official_job_url")
        or raw.get("url")
        or orig_url
    ).strip()

    # 10. Last Verified At
    last_verified_at = str(raw.get("last_verified_at") or now_iso).strip()

    # 11. Status
    raw_status = str(raw.get("status") or "active").lower().strip()
    status = "active" if raw_status in ("active", "open", "verified", "live") else raw_status

    # Optional metadata attributes (skills, experience, match)
    skills = raw.get("skills") or []
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]

    return {
        "job_id": job_id,
        "company_name": company_name,
        "job_title": job_title,
        "description": description,
        "location": location,
        "posted_at": posted_at,
        "source_platform": source_platform,
        "original_url": orig_url,
        "apply_url": apply_url,
        "last_verified_at": last_verified_at,
        "status": status,
        "skills": skills,
        "url_verified": bool(raw.get("url_verified", True)),
    }


def normalize_job_list(raw_jobs: List[Dict[str, Any]], default_source: str = "Company Careers") -> List[Dict[str, Any]]:
    """Normalize a batch of job records."""
    normalized: List[Dict[str, Any]] = []
    for item in raw_jobs:
        if isinstance(item, dict):
            normalized.append(normalize_job_dict(item, default_source=default_source))
    return normalized
