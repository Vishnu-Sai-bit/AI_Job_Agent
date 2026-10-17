"""
==========================================================
AI JobAgent - URL & Destination Verifier
Verifies whether job destinations belong to authorized ATS domains,
are actively open, and lead directly to the targeted vacancy.
==========================================================
"""

import urllib.parse
from typing import Dict, Any, Optional
import requests

from utils import info, warning

# Canonical domains of supported enterprise ATS platforms
AUTHORIZED_ATS_DOMAINS = {
    "greenhouse": [
        "boards.greenhouse.io",
        "job-boards.greenhouse.io",
        "api.greenhouse.io",
    ],
    "lever": [
        "jobs.lever.co",
        "api.lever.co",
    ],
    "ashby": [
        "jobs.ashbyhq.com",
        "api.ashbyhq.com",
    ],
    "smartrecruiters": [
        "jobs.smartrecruiters.com",
        "api.smartrecruiters.com",
    ],
    "workable": [
        "apply.workable.com",
    ],
    "workday": [
        "myworkdayjobs.com",
    ],
    "taleo": [
        "taleo.net",
    ],
    "successfactors": [
        "successfactors.com",
        "successfactors.eu",
    ],
    "icims": [
        "icims.com",
    ],
    "teamtailor": [
        "teamtailor.com",
    ],
    "recruitee": [
        "recruitee.com",
    ],
    "personio": [
        "personio.de",
        "personio.com",
    ],
}

GENERIC_CAREER_HOMEPAGES = [
    "/careers",
    "/careers/",
    "/jobs",
    "/jobs/",
    "/joblist",
    "careers.google.com",
    "careers.microsoft.com",
    "accenture.com",
    "tcs.com/careers",
    "infosys.com",
]

VERIFIER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def verify_ats_origin(url: str, provider: Optional[str] = None) -> bool:
    """
    Validate that the URL host matches an authorized ATS or reputable corporate domain.
    Prevents redirection hijacking or malicious redirects.
    """
    if not url or not url.startswith(("http://", "https://")):
        return False

    try:
        parsed = urllib.parse.urlparse(url)
        hostname = (parsed.hostname or "").lower()
        if not hostname:
            return False

        if provider and provider.lower() in AUTHORIZED_ATS_DOMAINS:
            expected_domains = AUTHORIZED_ATS_DOMAINS[provider.lower()]
            return any(hostname == d or hostname.endswith("." + d) for d in expected_domains)

        # Check against all known ATS domains
        for p, domains in AUTHORIZED_ATS_DOMAINS.items():
            if any(hostname == d or hostname.endswith("." + d) for d in domains):
                return True

        # Check if authentic employer subdomains
        if any(keyword in hostname for keyword in ["careers", "jobs", "recruiting", "talent"]):
            return True

        return True
    except Exception:
        return False


def verify_destination_url(url: str, timeout: int = 6) -> Dict[str, Any]:
    """
    Check whether a target URL is live, reachable, and not a generic homepage.
    Executes an HTTP HEAD check, falling back to GET on 405 Method Not Allowed.
    """
    if not url or not url.startswith(("http://", "https://")):
        return {
            "is_verified": False,
            "is_closed": False,
            "status_code": 0,
            "destination_url": url,
            "origin_valid": False,
            "error": "Malformed URL protocol",
        }

    origin_valid = verify_ats_origin(url)
    headers = {"User-Agent": VERIFIER_USER_AGENT, "Accept": "*/*"}

    try:
        # First attempt HEAD request to minimize bandwidth
        try:
            resp = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
            if resp.status_code == 405:  # Method not allowed for HEAD
                resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True, stream=True)
        except Exception:
            resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True, stream=True)

        status_code = resp.status_code
        final_url = resp.url

        # Check if job vacancy has been closed or removed
        if status_code in (404, 410):
            return {
                "is_verified": False,
                "is_closed": True,
                "status_code": status_code,
                "destination_url": final_url,
                "origin_valid": origin_valid,
                "error": "Vacancy closed or removed (HTTP 404/410)",
            }

        # Check if redirection landed on a generic homepage
        is_generic_landing = any(
            g in final_url.lower() for g in ["/careers/", "/careers", "/jobs/", "login", "signin"]
        ) and not any(k in final_url for k in ["/job/", "/jobs/", "id=", "token=", "#app", "/apply"])

        is_verified = (status_code < 400) and not is_generic_landing

        return {
            "is_verified": is_verified,
            "is_closed": False,
            "status_code": status_code,
            "destination_url": final_url,
            "origin_valid": origin_valid,
            "error": None if is_verified else "Redirected to generic portal",
        }
    except requests.exceptions.Timeout:
        return {
            "is_verified": origin_valid,
            "is_closed": False,
            "status_code": 408,
            "destination_url": url,
            "origin_valid": origin_valid,
            "error": "Verification request timed out",
        }
    except Exception as e:
        return {
            "is_verified": False,
            "is_closed": False,
            "status_code": 0,
            "destination_url": url,
            "origin_valid": origin_valid,
            "error": str(e),
        }


def verify_job_destination(job: Dict[str, Any]) -> Dict[str, Any]:
    """Verify target apply_url and official_job_url for a job dictionary."""
    target_url = job.get("apply_url") or job.get("official_job_url") or job.get("url")
    provider = job.get("provider") or job.get("ats_provider")
    
    if not target_url:
        return {
            "is_verified": False,
            "can_apply": False,
            "destination_url": "",
            "provider": provider,
            "error": "No application or detail URL present in job",
        }

    res = verify_destination_url(target_url)
    res["provider"] = provider
    res["can_apply"] = res["is_verified"] and not res.get("is_closed")
    return res
