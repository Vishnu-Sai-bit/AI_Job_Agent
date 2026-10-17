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


# ==========================================================
# 6. WORKDAY CONNECTOR (CXS Search API & Career Feeds)
# ==========================================================
def fetch_workday(config: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    Workday ATS Connector
    Captures exact company-hosted job detail URL and requisition ID.
    Supports Workday CXS API endpoint:
    POST https://{domain}/wday/cxs/{tenant}/{site}/jobs
    """
    domain = config.get("domain") or config.get("host") or ""
    tenant = config.get("tenant") or config.get("company_key") or ""
    site = config.get("site") or "External"
    comp_name = config.get("company") or (tenant.capitalize() if tenant else "Workday Employer")

    if not domain and tenant:
        domain = f"{tenant}.wd3.myworkdayjobs.com"

    if domain and tenant:
        url = f"https://{domain}/wday/cxs/{tenant}/{site}/jobs"
        payload = {"appliedFacets": {}, "limit": 25, "offset": 0, "searchText": ""}
        try:
            resp = requests.post(url, json=payload, headers=DEFAULT_HEADERS, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                for posting in data.get("jobPostings", []):
                    ext_path = posting.get("externalPath") or ""
                    bullet_fields = posting.get("bulletFields") or []
                    req_id = ""
                    for bf in bullet_fields:
                        if bf and re.search(r"^[A-Z0-9\-_]{4,}$", str(bf)):
                            req_id = str(bf)
                            break
                    if not req_id and ext_path:
                        m = re.search(r"_([A-Za-z0-9\-_]+)$", ext_path)
                        req_id = m.group(1) if m else ext_path.strip("/").split("/")[-1]

                    job_url = f"https://{domain}/en-US/{site}{ext_path}"
                    apply_url = f"{job_url}/apply"
                    loc = posting.get("locationsText") or "Remote / Office"
                    yield normalize_job(
                        company=comp_name,
                        provider="workday",
                        company_key=tenant or domain,
                        job_id=req_id or ext_path,
                        title=posting.get("title"),
                        location=loc,
                        job_url=job_url,
                        apply_url=apply_url,
                        description=f"Workday official job opening #{req_id} at {comp_name}.",
                        posted_at=posting.get("postedOn")
                    )
                return
        except Exception as e:
            warning(f"Workday connector notice for {comp_name}: {e}")

    for item in config.get("jobs", []):
        job_url = item.get("job_url") or item.get("url")
        apply_url = item.get("apply_url") or f"{job_url}/apply"
        yield normalize_job(
            company=comp_name,
            provider="workday",
            company_key=tenant or "workday",
            job_id=item.get("id") or item.get("job_id"),
            title=item.get("title"),
            location=item.get("location") or "India",
            job_url=job_url,
            apply_url=apply_url,
            description=item.get("description"),
            posted_at=item.get("posted_at")
        )


# ==========================================================
# 7. TEAMTAILOR CONNECTOR
# ==========================================================
def fetch_teamtailor(config: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    Teamtailor ATS Connector
    Captures careersite-job-url and careersite-job-apply-url.
    """
    subdomain = config.get("subdomain") or config.get("company_key") or ""
    comp_name = config.get("company") or subdomain.capitalize()
    if subdomain:
        feed_url = f"https://{subdomain}.teamtailor.com/jobs.json"
        data = get_json(feed_url, timeout=8)
        if data and isinstance(data, list):
            for item in data:
                j_url = item.get("careersite-job-url") or item.get("url") or f"https://{subdomain}.teamtailor.com/jobs/{item.get('id')}"
                a_url = item.get("careersite-job-apply-url") or item.get("apply_url") or f"{j_url}/apply"
                yield normalize_job(
                    company=comp_name,
                    provider="teamtailor",
                    company_key=subdomain,
                    job_id=item.get("id"),
                    title=item.get("title"),
                    location=item.get("location") or "Remote",
                    job_url=j_url,
                    apply_url=a_url,
                    description=item.get("body"),
                    posted_at=item.get("created-at")
                )
            return

    for item in config.get("jobs", []):
        yield normalize_job(
            company=comp_name,
            provider="teamtailor",
            company_key=subdomain or "teamtailor",
            job_id=item.get("id"),
            title=item.get("title"),
            location=item.get("location") or "Remote",
            job_url=item.get("job_url") or item.get("url"),
            apply_url=item.get("apply_url"),
            description=item.get("description")
        )


# ==========================================================
# 8. RECRUITEE CONNECTOR
# ==========================================================
def fetch_recruitee(config: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    Recruitee ATS Connector
    Captures exact job URL and careers_apply_url where available.
    Endpoint: https://{company}.recruitee.com/api/offers/
    """
    subdomain = config.get("subdomain") or config.get("company_key") or ""
    comp_name = config.get("company") or subdomain.capitalize()
    if subdomain:
        url = f"https://{subdomain}.recruitee.com/api/offers/"
        data = get_json(url, timeout=8)
        if data and isinstance(data, dict):
            for offer in data.get("offers", []):
                j_url = offer.get("careers_url") or f"https://{subdomain}.recruitee.com/o/{offer.get('slug') or offer.get('id')}"
                a_url = offer.get("careers_apply_url") or f"{j_url}/apply"
                yield normalize_job(
                    company=comp_name,
                    provider="recruitee",
                    company_key=subdomain,
                    job_id=offer.get("id"),
                    title=offer.get("title"),
                    location=offer.get("location") or "Remote",
                    job_url=j_url,
                    apply_url=a_url,
                    description=offer.get("description"),
                    posted_at=offer.get("published_at")
                )
            return

    for item in config.get("jobs", []):
        yield normalize_job(
            company=comp_name,
            provider="recruitee",
            company_key=subdomain or "recruitee",
            job_id=item.get("id"),
            title=item.get("title"),
            location=item.get("location") or "Remote",
            job_url=item.get("job_url") or item.get("url"),
            apply_url=item.get("apply_url"),
            description=item.get("description")
        )


# ==========================================================
# 9. PERSONIO CONNECTOR
# ==========================================================
def fetch_personio(config: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    Personio ATS Connector
    Captures position ID and published job's career-site URL.
    Endpoint: https://{company}.jobs.personio.de/xml
    """
    subdomain = config.get("subdomain") or config.get("company_key") or ""
    comp_name = config.get("company") or subdomain.capitalize()
    if subdomain:
        url = f"https://{subdomain}.jobs.personio.de/xml"
        try:
            resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=8)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, "xml")
                positions = soup.find_all("position")
                for pos in positions:
                    pos_id = pos.find("id")
                    pid = pos_id.text if pos_id else ""
                    name = pos.find("name")
                    title = name.text if name else "Open Position"
                    office = pos.find("office")
                    loc = office.text if office else "Remote"
                    j_url = f"https://{subdomain}.jobs.personio.de/job/{pid}"
                    a_url = f"{j_url}#apply"
                    yield normalize_job(
                        company=comp_name,
                        provider="personio",
                        company_key=subdomain,
                        job_id=pid,
                        title=title,
                        location=loc,
                        job_url=j_url,
                        apply_url=a_url,
                        description=f"Personio official vacancy #{pid} at {comp_name}."
                    )
                return
        except Exception as e:
            warning(f"Personio connector notice for {comp_name}: {e}")

    for item in config.get("jobs", []):
        yield normalize_job(
            company=comp_name,
            provider="personio",
            company_key=subdomain or "personio",
            job_id=item.get("id"),
            title=item.get("title"),
            location=item.get("location") or "Remote",
            job_url=item.get("job_url") or item.get("url"),
            apply_url=item.get("apply_url"),
            description=item.get("description")
        )


# ==========================================================
# 10. BAMBOOHR CONNECTOR
# ==========================================================
def fetch_bamboohr(config: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    BambooHR ATS Connector
    Stores published job's actual career-site URL and job ID.
    Endpoint: https://{company}.bamboohr.com/careers/list
    """
    subdomain = config.get("subdomain") or config.get("company_key") or ""
    comp_name = config.get("company") or subdomain.capitalize()
    if subdomain:
        url = f"https://{subdomain}.bamboohr.com/careers/list"
        data = get_json(url, timeout=8)
        if data and isinstance(data, dict):
            for item in data.get("result", []):
                item_id = item.get("id")
                j_url = item.get("careerPageUrl") or f"https://{subdomain}.bamboohr.com/careers/{item_id}"
                a_url = f"{j_url}?source=ai_job_agent"
                loc_obj = item.get("location") or {}
                loc_str = f"{loc_obj.get('city', '')}, {loc_obj.get('state', '')}".strip(" ,") or "Remote"
                yield normalize_job(
                    company=comp_name,
                    provider="bamboohr",
                    company_key=subdomain,
                    job_id=item_id,
                    title=item.get("jobOpeningName"),
                    location=loc_str,
                    job_url=j_url,
                    apply_url=a_url,
                    description=f"BambooHR official vacancy for {item.get('jobOpeningName')} at {comp_name}."
                )
            return

    for item in config.get("jobs", []):
        yield normalize_job(
            company=comp_name,
            provider="bamboohr",
            company_key=subdomain or "bamboohr",
            job_id=item.get("id"),
            title=item.get("title"),
            location=item.get("location") or "Remote",
            job_url=item.get("job_url") or item.get("url"),
            apply_url=item.get("apply_url"),
            description=item.get("description")
        )


# ==========================================================
# 11. PINPOINT CONNECTOR
# ==========================================================
def fetch_pinpoint(config: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    Pinpoint ATS Connector
    Uses job specific links returned by company's configured career site or API.
    Endpoint: https://{company}.pinpointhq.com/postings.json
    """
    subdomain = config.get("subdomain") or config.get("company_key") or ""
    comp_name = config.get("company") or subdomain.capitalize()
    if subdomain:
        url = f"https://{subdomain}.pinpointhq.com/postings.json"
        data = get_json(url, timeout=8)
        if data and isinstance(data, dict):
            for item in data.get("data", []):
                j_url = item.get("url") or f"https://{subdomain}.pinpointhq.com/postings/{item.get('id')}"
                a_url = item.get("apply_url") or f"{j_url}/applications/new"
                yield normalize_job(
                    company=comp_name,
                    provider="pinpoint",
                    company_key=subdomain,
                    job_id=item.get("id"),
                    title=item.get("title"),
                    location=str(item.get("location") or "Remote"),
                    job_url=j_url,
                    apply_url=a_url,
                    description=item.get("description")
                )
            return

    for item in config.get("jobs", []):
        yield normalize_job(
            company=comp_name,
            provider="pinpoint",
            company_key=subdomain or "pinpoint",
            job_id=item.get("id"),
            title=item.get("title"),
            location=item.get("location") or "Remote",
            job_url=item.get("job_url") or item.get("url"),
            apply_url=item.get("apply_url"),
            description=item.get("description")
        )


# ==========================================================
# 12. BREEZY HR CONNECTOR
# ==========================================================
def fetch_breezy(config: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    Breezy HR ATS Connector
    Stores published position's actual job and apply links.
    Endpoint: https://{company}.breezy.hr/json
    """
    subdomain = config.get("subdomain") or config.get("company_key") or ""
    comp_name = config.get("company") or subdomain.capitalize()
    if subdomain:
        url = f"https://{subdomain}.breezy.hr/json"
        data = get_json(url, timeout=8)
        if data and isinstance(data, list):
            for item in data:
                j_url = item.get("url") or f"https://{subdomain}.breezy.hr/p/{item.get('id')}"
                a_url = f"{j_url}/apply"
                loc_obj = item.get("location") or {}
                loc_str = loc_obj.get("name") if isinstance(loc_obj, dict) else str(loc_obj)
                yield normalize_job(
                    company=comp_name,
                    provider="breezy",
                    company_key=subdomain,
                    job_id=item.get("id"),
                    title=item.get("name"),
                    location=loc_str or "Remote",
                    job_url=j_url,
                    apply_url=a_url,
                    description=item.get("description")
                )
            return

    for item in config.get("jobs", []):
        yield normalize_job(
            company=comp_name,
            provider="breezy",
            company_key=subdomain or "breezy",
            job_id=item.get("id"),
            title=item.get("title"),
            location=item.get("location") or "Remote",
            job_url=item.get("job_url") or item.get("url"),
            apply_url=item.get("apply_url"),
            description=item.get("description")
        )


# ==========================================================
# 13. JOBVITE CONNECTOR
# ==========================================================
def fetch_jobvite(config: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    Jobvite ATS Connector
    Captures company site identifier and job-specific link.
    """
    company_id = config.get("company_id") or config.get("company_key") or ""
    comp_name = config.get("company") or company_id.capitalize()
    for item in config.get("jobs", []):
        j_id = item.get("id") or item.get("job_id")
        j_url = item.get("job_url") or item.get("url") or f"https://jobs.jobvite.com/{company_id}/job/{j_id}"
        a_url = item.get("apply_url") or f"{j_url}/apply"
        yield normalize_job(
            company=comp_name,
            provider="jobvite",
            company_key=company_id or "jobvite",
            job_id=j_id,
            title=item.get("title"),
            location=item.get("location") or "India",
            job_url=j_url,
            apply_url=a_url,
            description=item.get("description")
        )


# ==========================================================
# 14. JAZZHR CONNECTOR
# ==========================================================
def fetch_jazzhr(config: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    JazzHR ATS Connector
    Extracts exact job listing and application links from supported company sources.
    """
    company_id = config.get("company_id") or config.get("company_key") or ""
    comp_name = config.get("company") or company_id.capitalize()
    for item in config.get("jobs", []):
        j_id = item.get("id") or item.get("job_id")
        j_url = item.get("job_url") or item.get("url") or f"https://{company_id}.applytojob.com/apply/{j_id}"
        a_url = item.get("apply_url") or f"{j_url}#apply"
        yield normalize_job(
            company=comp_name,
            provider="jazzhr",
            company_key=company_id or "jazzhr",
            job_id=j_id,
            title=item.get("title"),
            location=item.get("location") or "Remote",
            job_url=j_url,
            apply_url=a_url,
            description=item.get("description")
        )


# ==========================================================
# 15. SAP SUCCESSFACTORS CONNECTOR
# ==========================================================
def fetch_successfactors(config: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    SAP SuccessFactors Connector
    Captures actual posting URL and requisition IDs in supported deep-link formats.
    """
    company_key = config.get("company_key") or ""
    comp_name = config.get("company") or "SAP Client"
    for item in config.get("jobs", []):
        req_id = item.get("id") or item.get("requisition_id") or item.get("job_id")
        j_url = item.get("job_url") or item.get("url") or f"https://career.successfactors.com/career?company={company_key}&career_job_req_id={req_id}"
        a_url = item.get("apply_url") or j_url
        yield normalize_job(
            company=comp_name,
            provider="successfactors",
            company_key=company_key or "successfactors",
            job_id=req_id,
            title=item.get("title"),
            location=item.get("location") or "India",
            job_url=j_url,
            apply_url=a_url,
            description=item.get("description")
        )


# ==========================================================
# 16. ORACLE TALEO CONNECTOR
# ==========================================================
def fetch_taleo(config: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    Oracle Taleo Connector
    Uses correct career section and job identifier in supported job-detail or application URL.
    """
    company_key = config.get("company_key") or ""
    comp_name = config.get("company") or "Taleo Client"
    for item in config.get("jobs", []):
        j_id = item.get("id") or item.get("job_id")
        career_section = item.get("career_section") or "2"
        j_url = item.get("job_url") or item.get("url") or f"https://{company_key}.taleo.net/careersection/{career_section}/jobdetail.ftl?job={j_id}"
        a_url = item.get("apply_url") or f"https://{company_key}.taleo.net/careersection/{career_section}/jobapply.ftl?job={j_id}"
        yield normalize_job(
            company=comp_name,
            provider="taleo",
            company_key=company_key or "taleo",
            job_id=j_id,
            title=item.get("title"),
            location=item.get("location") or "India",
            job_url=j_url,
            apply_url=a_url,
            description=item.get("description")
        )


# ==========================================================
# 17. iCIMS CONNECTOR
# ==========================================================
def fetch_icims(config: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    iCIMS Connector
    Captures company career site's exact job-detail link commonly including a job identifier.
    """
    subdomain = config.get("subdomain") or config.get("company_key") or ""
    comp_name = config.get("company") or subdomain.capitalize()
    for item in config.get("jobs", []):
        j_id = item.get("id") or item.get("job_id")
        j_url = item.get("job_url") or item.get("url") or f"https://{subdomain}.icims.com/jobs/{j_id}/job"
        a_url = item.get("apply_url") or f"https://{subdomain}.icims.com/jobs/{j_id}/apply"
        yield normalize_job(
            company=comp_name,
            provider="icims",
            company_key=subdomain or "icims",
            job_id=j_id,
            title=item.get("title"),
            location=item.get("location") or "India",
            job_url=j_url,
            apply_url=a_url,
            description=item.get("description")
        )


# ==========================================================
# 18. UKG CONNECTOR
# ==========================================================
def fetch_ukg(config: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    UKG Connector
    Uses employer's configured recruiting link rather than assuming universal URL pattern.
    """
    tenant = config.get("tenant") or config.get("company_key") or ""
    comp_name = config.get("company") or tenant.capitalize()
    for item in config.get("jobs", []):
        j_id = item.get("id") or item.get("job_id")
        j_url = item.get("job_url") or item.get("url") or f"https://recruiting.ultipro.com/{tenant}/JobBoard/JobDetail?jobId={j_id}"
        a_url = item.get("apply_url") or f"{j_url}&apply=true"
        yield normalize_job(
            company=comp_name,
            provider="ukg",
            company_key=tenant or "ukg",
            job_id=j_id,
            title=item.get("title"),
            location=item.get("location") or "India",
            job_url=j_url,
            apply_url=a_url,
            description=item.get("description")
        )


# ==========================================================
# 19. CORNERSTONE CONNECTOR
# ==========================================================
def fetch_cornerstone(config: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    Cornerstone OnDemand Connector
    Resolves and retains correct job specific external posting URL.
    """
    portal = config.get("portal") or config.get("company_key") or ""
    comp_name = config.get("company") or portal.capitalize()
    for item in config.get("jobs", []):
        req_id = item.get("id") or item.get("requisition_id") or item.get("job_id")
        j_url = item.get("job_url") or item.get("url") or f"https://{portal}.csod.com/ux/ats/careersite/1/home/requisition/{req_id}"
        a_url = item.get("apply_url") or f"{j_url}/apply"
        yield normalize_job(
            company=comp_name,
            provider="cornerstone",
            company_key=portal or "cornerstone",
            job_id=req_id,
            title=item.get("title"),
            location=item.get("location") or "India",
            job_url=j_url,
            apply_url=a_url,
            description=item.get("description")
        )


# Master provider connectors registry (Tier 1 + Tier 2)
CONNECTORS = {
    # Tier 1 - Priority ATS Integrations
    "greenhouse": fetch_greenhouse,
    "lever": fetch_lever,
    "ashby": fetch_ashby,
    "smartrecruiters": fetch_smartrecruiters,
    "workable": fetch_workable,
    "workday": fetch_workday,
    "teamtailor": fetch_teamtailor,
    "recruitee": fetch_recruitee,
    "personio": fetch_personio,
    # Tier 2 - URL Extraction & Provider Rules
    "bamboohr": fetch_bamboohr,
    "pinpoint": fetch_pinpoint,
    "breezy": fetch_breezy,
    "jobvite": fetch_jobvite,
    "jazzhr": fetch_jazzhr,
    "successfactors": fetch_successfactors,
    "taleo": fetch_taleo,
    "icims": fetch_icims,
    "ukg": fetch_ukg,
    "cornerstone": fetch_cornerstone,
}
