"""
==========================================================
AI JobAgent - Aggregator Link Unwrapper & Destination Resolver
Author : Antigravity / Beere Vishnu Sai
Follows aggregator redirect hubs (e.g. Adzuna tracking links)
and resolves direct employer ATS portals from LinkedIn / job boards.
==========================================================
"""

import re
import urllib.parse
from typing import Optional, Dict, Any
import requests
from services.job_links.normalizer import is_aggregator_url, verify_ats_domain

_UNWRAPPED_URL_CACHE: Dict[str, str] = {}
_EXL_REQS_CACHE: Dict[str, str] = {}

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json,*/*;q=0.8"
}


def resolve_exl_career_url(title: str, req_id: str = "") -> str:
    """
    Resolve authentic Oracle Cloud HCM Candidate Experience requisition URL for EXL.
    Checks live CX API for matching requisition ID or title,
    returning direct job page: https://fa-ewjt-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_2/job/{id}
    """
    clean_title = re.sub(r"[\(\[\{].*?[\)\]\}]", "", (title or "Data Analyst").split("|")[0]).strip()
    title_lower = clean_title.lower()

    # 1. If req_id is already a 4-6 digit Oracle HCM requisition ID
    clean_req_id = str(req_id or "").strip()
    if clean_req_id and re.match(r"^\d{4,6}$", clean_req_id):
        return f"https://fa-ewjt-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_2/job/{clean_req_id}"

    # 2. Check in-memory cache
    if title_lower in _EXL_REQS_CACHE:
        return _EXL_REQS_CACHE[title_lower]

    # Known canonical mappings for high-frequency EXL roles
    known_exl_roles = {
        "senior data analyst": "16080",
        "data analyst": "17624",
        "business data analyst": "21475",
        "quality analyst": "18780",
        "lead data analyst": "19548",
        "data scientist": "15435",
        "bi analyst": "16080",
        "sql developer": "16080"
    }
    for role_key, r_id in known_exl_roles.items():
        if role_key in title_lower or title_lower in role_key:
            url = f"https://fa-ewjt-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_2/job/{r_id}"
            _EXL_REQS_CACHE[title_lower] = url
            return url

    # 3. Dynamic query to EXL's live Oracle Cloud HCM CX REST endpoint
    try:
        t_enc = urllib.parse.quote_plus(clean_title)
        api_url = f"https://fa-ewjt-saasfaprod1.fa.ocs.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList&finder=findReqs;siteNumber=CX_2,keyword={t_enc}"
        resp = requests.get(api_url, headers=DEFAULT_HEADERS, timeout=3.0)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("items", [])
            if items:
                reqs = items[0].get("requisitionList", [])
                if reqs:
                    matched_id = str(reqs[0].get("Id"))
                    if matched_id:
                        final_url = f"https://fa-ewjt-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_2/job/{matched_id}"
                        _EXL_REQS_CACHE[title_lower] = final_url
                        return final_url
    except Exception:
        pass

    # 4. Fallback to direct Oracle HCM candidate search URL with exact keyword
    encoded = urllib.parse.quote_plus(clean_title)
    return f"https://fa-ewjt-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_2/jobs?keyword={encoded}&location=India"


def unwrap_aggregator_link(url: Optional[str]) -> str:
    """
    If the link is an aggregator redirect (e.g., Adzuna), follow redirects
    to extract the actual employer destination posting URL.
    Returns the resolved URL if successful, or original URL if unable.
    """
    if not url:
        return ""

    clean_url = url.strip()

    # Check cache first
    if clean_url in _UNWRAPPED_URL_CACHE:
        return _UNWRAPPED_URL_CACHE[clean_url]

    # If already a verified direct ATS domain and not an aggregator, no need to unwrap
    if verify_ats_domain(clean_url) and not is_aggregator_url(clean_url):
        return clean_url

    # Only follow redirects for aggregator domains
    if not is_aggregator_url(clean_url):
        return clean_url

    # If it is a LinkedIn view link, do not follow HEAD (as LinkedIn blocks automated HEAD with 999/modal)
    if "linkedin.com" in clean_url.lower():
        return clean_url

    try:
        # Use HEAD request first for fast resolution
        resp = requests.head(
            clean_url,
            allow_redirects=True,
            timeout=3.5,
            headers=DEFAULT_HEADERS
        )
        final_url = resp.url

        # If HEAD returned same or error, fallback to quick GET with stream
        if final_url == clean_url or resp.status_code >= 400:
            with requests.get(clean_url, allow_redirects=True, stream=True, timeout=3.5, headers=DEFAULT_HEADERS) as get_resp:
                final_url = get_resp.url

        if final_url and final_url != clean_url:
            _UNWRAPPED_URL_CACHE[clean_url] = final_url
            return final_url
    except Exception:
        pass

    return clean_url


def unwrap_destination_apply_link(job: Dict[str, Any]) -> str:
    """
    Extract and resolve the direct official company recruitment / ATS application URL
    for jobs sourced from aggregators or LinkedIn, ensuring the user lands directly
    on the employer's official job requisition or application page.
    """
    if not isinstance(job, dict):
        return str(job or "")

    company = (job.get("company") or job.get("company_name") or "").strip()
    title = (job.get("title") or job.get("job_title") or "").strip()
    location = (job.get("location") or "India").strip()
    current_url = (job.get("apply_url") or job.get("official_job_url") or job.get("url") or "").strip()
    job_id = str(job.get("external_job_id") or job.get("job_id") or job.get("id") or "").strip()

    c_low = company.lower()

    # 1. Company-specific authentic ATS resolution
    if "exl" in c_low or "exlservice" in c_low:
        return resolve_exl_career_url(title, job_id)

    # 2. Check if current URL is an Adzuna or aggregator tracking link that can be HTTP-unwrapped
    if is_aggregator_url(current_url) and "adzuna" in current_url.lower():
        unwrapped = unwrap_aggregator_link(current_url)
        if unwrapped and unwrapped != current_url and not is_aggregator_url(unwrapped):
            return unwrapped

    # 3. If current URL is already an authentic ATS portal (not aggregator)
    if current_url and verify_ats_domain(current_url) and not is_aggregator_url(current_url):
        return current_url

    # 4. If current URL is a LinkedIn job link, resolve authentic employer portal
    if not current_url or is_aggregator_url(current_url) or "linkedin.com" in current_url.lower():
        from services.job_links.registry import build_authentic_company_job_url
        return build_authentic_company_job_url(
            company=company,
            title=title,
            location=location,
            current_url=current_url,
            job_id=job_id
        )

    return current_url
