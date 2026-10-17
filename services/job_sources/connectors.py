"""
==========================================================
AI JobAgent - ATS Connectors
Connectors for retrieving vacancies from public ATS APIs:
Greenhouse, Lever, Ashby, SmartRecruiters, and Workable.
Each connector maps provider-specific responses to a common schema.
==========================================================
"""

import re
import html
from urllib.parse import quote
from typing import Dict, Any, Generator, Optional, List
import requests
from bs4 import BeautifulSoup

from utils import info, warning, error

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
}


def clean_html_text(raw_html: Optional[str]) -> str:
    """Clean HTML markup into readable plaintext."""
    if not raw_html:
        return ""
    try:
        text = BeautifulSoup(raw_html, "html.parser").get_text(separator=" ")
        text = re.sub(r"\s+", " ", text).strip()
        return text
    except Exception:
        return re.sub(r"<[^>]+>", " ", str(raw_html)).strip()


def normalize_job(
    company: str,
    provider: str,
    company_key: str,
    job_id: Any,
    title: str,
    location: Optional[str],
    job_url: str,
    apply_url: Optional[str] = None,
    description: Optional[str] = None,
    posted_at: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Standardize vacancies across all ATS platforms into a single unified record.
    """
    clean_id = str(job_id or "").strip()
    clean_title = str(title or "Open Opportunity").strip()
    clean_company = str(company or "Verified Employer").strip()
    clean_loc = str(location or "Remote / Global").strip()
    clean_job_url = str(job_url or "").strip()
    clean_apply_url = str(apply_url or clean_job_url).strip()
    clean_desc = clean_html_text(description)

    return {
        "company_name": clean_company,
        "company": clean_company,
        "provider": provider.lower().strip(),
        "ats_provider": provider.capitalize(),
        "company_key": str(company_key).strip(),
        "external_job_id": clean_id,
        "job_id": clean_id,
        "job_title": clean_title,
        "title": clean_title,
        "location": clean_loc,
        "official_job_url": clean_job_url,
        "job_url": clean_job_url,
        "apply_url": clean_apply_url,
        "url": clean_apply_url or clean_job_url,
        "description": clean_desc,
        "posted_at": str(posted_at or ""),
        "posted_date": "Active Live (Today)",
        "url_verified": False,
        "status": "open",
        "is_live": True,
    }


def get_json(url: str, timeout: int = 12) -> Optional[Any]:
    """Execute GET request with standardized headers and error handling."""
    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
        warning(f"ATS connector request returned HTTP {resp.status_code} for {url}")
        return None
    except Exception as e:
        warning(f"ATS connector request exception for {url}: {e}")
        return None


# ==========================================================
# 1. GREENHOUSE CONNECTOR (Public Job Board API)
# ==========================================================
def fetch_greenhouse(config: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    Query Greenhouse Public Job Board API using the company's board token.
    Endpoint: https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true
    """
    token = quote(str(config.get("board_token") or "").strip(), safe="")
    if not token:
        return

    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    data = get_json(url)
    if not data or not isinstance(data, dict):
        return

    jobs = data.get("jobs", [])
    for job in jobs:
        loc_obj = job.get("location") or {}
        loc_name = loc_obj.get("name") if isinstance(loc_obj, dict) else str(loc_obj)
        job_url = job.get("absolute_url") or f"https://boards.greenhouse.io/{token}/jobs/{job.get('id')}"
        apply_url = f"{job_url}#app" if "#app" not in job_url else job_url

        yield normalize_job(
            company=config.get("company", token.capitalize()),
            provider="greenhouse",
            company_key=token,
            job_id=job.get("id"),
            title=job.get("title"),
            location=loc_name or "Remote",
            job_url=job_url,
            apply_url=apply_url,
            description=job.get("content"),
            posted_at=job.get("updated_at"),
        )


# ==========================================================
# 2. LEVER CONNECTOR (Public Postings API)
# ==========================================================
def fetch_lever(config: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    Query Lever Public Postings API using the company's site identifier.
    Endpoint: https://api.lever.co/v0/postings/{site}?mode=json
    """
    site = quote(str(config.get("site") or "").strip(), safe="")
    if not site:
        return

    url = f"https://api.lever.co/v0/postings/{site}?mode=json"
    data = get_json(url)
    if not data or not isinstance(data, list):
        return

    for job in data:
        categories = job.get("categories") or {}
        job_url = job.get("hostedUrl") or f"https://jobs.lever.co/{site}/{job.get('id')}"
        apply_url = job.get("applyUrl") or f"{job_url}/apply"

        yield normalize_job(
            company=config.get("company", site.capitalize()),
            provider="lever",
            company_key=site,
            job_id=job.get("id"),
            title=job.get("text"),
            location=categories.get("location") or "Remote",
            job_url=job_url,
            apply_url=apply_url,
            description=job.get("descriptionPlain") or job.get("description"),
            posted_at=str(job.get("createdAt") or ""),
        )


# ==========================================================
# 3. ASHBY CONNECTOR (Public Job Board API)
# ==========================================================
def fetch_ashby(config: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    Query Ashby Public Job Postings API using its job-board name.
    Endpoint: https://api.ashbyhq.com/posting-api/job-board/{board_name}
    """
    board = quote(str(config.get("board_name") or "").strip(), safe="")
    if not board:
        return

    url = f"https://api.ashbyhq.com/posting-api/job-board/{board}"
    data = get_json(url)
    if not data or not isinstance(data, dict):
        return

    jobs = data.get("jobs", [])
    for job in jobs:
        job_url = job.get("jobUrl") or f"https://jobs.ashbyhq.com/{board}/{job.get('id')}"
        apply_url = job.get("applyUrl") or f"{job_url}/application"

        yield normalize_job(
            company=config.get("company", board.capitalize()),
            provider="ashby",
            company_key=board,
            job_id=job.get("id") or job_url,
            title=job.get("title"),
            location=job.get("location") or "Remote",
            job_url=job_url,
            apply_url=apply_url,
            description=job.get("descriptionPlain") or job.get("description"),
            posted_at=job.get("publishedAt"),
        )


# ==========================================================
# 4. SMARTRECRUITERS CONNECTOR (Public Postings API)
# ==========================================================
def fetch_smartrecruiters(config: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    Query SmartRecruiters Public Postings API using its company identifier.
    Endpoint: https://api.smartrecruiters.com/v1/companies/{company_id}/postings
    """
    company_id = quote(str(config.get("company_id") or config.get("company_identifier") or "").strip(), safe="")
    if not company_id:
        return

    url = f"https://api.smartrecruiters.com/v1/companies/{company_id}/postings"
    data = get_json(url)
    if not data or not isinstance(data, dict):
        return

    content = data.get("content", [])
    for item in content:
        loc_obj = item.get("location") or {}
        loc_name = f"{loc_obj.get('city', '')}, {loc_obj.get('country', '')}".strip(" ,") or "Global"
        item_id = item.get("id") or item.get("refNumber")
        job_url = f"https://jobs.smartrecruiters.com/{company_id}/{item_id}"
        apply_url = f"https://jobs.smartrecruiters.com/{company_id}/{item_id}/apply"

        yield normalize_job(
            company=config.get("company", company_id.capitalize()),
            provider="smartrecruiters",
            company_key=company_id,
            job_id=item_id,
            title=item.get("name"),
            location=loc_name,
            job_url=job_url,
            apply_url=apply_url,
            description=f"SmartRecruiters official opening for {item.get('name')} at {config.get('company')}.",
            posted_at=item.get("releasedDate"),
        )


# ==========================================================
# 5. WORKABLE CONNECTOR (Public Widget API)
# ==========================================================
def fetch_workable(config: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    Query Workable Public Widget API using account subdomain.
    Endpoint: https://apply.workable.com/api/v1/widget/accounts/{subdomain}
    """
    subdomain = quote(str(config.get("account_subdomain") or "").strip(), safe="")
    if not subdomain:
        return

    url = f"https://apply.workable.com/api/v1/widget/accounts/{subdomain}"
    data = get_json(url)
    if not data or not isinstance(data, dict):
        return

    jobs = data.get("jobs", [])
    for item in jobs:
        shortcode = item.get("shortcode") or item.get("id")
        job_url = item.get("url") or f"https://apply.workable.com/{subdomain}/j/{shortcode}/"
        apply_url = item.get("application_url") or f"{job_url}apply/"

        yield normalize_job(
            company=config.get("company", subdomain.capitalize()),
            provider="workable",
            company_key=subdomain,
            job_id=shortcode,
            title=item.get("title"),
            location=item.get("city") or item.get("country") or "Remote",
            job_url=job_url,
            apply_url=apply_url,
            description=item.get("description"),
            posted_at=item.get("published_on"),
        )


# Master provider connectors registry
CONNECTORS = {
    "greenhouse": fetch_greenhouse,
    "lever": fetch_lever,
    "ashby": fetch_ashby,
    "smartrecruiters": fetch_smartrecruiters,
    "workable": fetch_workable,
}
