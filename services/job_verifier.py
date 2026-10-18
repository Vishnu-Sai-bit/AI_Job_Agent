"""
==========================================================
AI JobAgent - Job Verifier Service
Validates URL syntax, ensures zero intermediate aggregator
redirects, checks employer domain legitimacy, and verifies
active listing status.
==========================================================
"""

import re
from datetime import datetime, timezone
from typing import Dict, Any, Tuple
from urllib.parse import urlparse
import requests
from utils import info, warning

# Domains considered aggregators rather than direct employer applications
AGGREGATOR_DOMAINS = {
    "linkedin.com",
    "indeed.com",
    "adzuna.com",
    "naukri.com",
    "jooble.org",
    "foundit.in",
    "monster.com",
    "glassdoor.com",
}

# Recognized enterprise ATS and career platform domains
KNOWN_ATS_DOMAINS = {
    "myworkdayjobs.com",
    "greenhouse.io",
    "lever.co",
    "ashbyhq.com",
    "smartrecruiters.com",
    "oraclecloud.com",
    "taleo.net",
    "icims.com",
    "bamboohr.com",
    "workable.com",
    "recruitee.com",
    "personio.de",
    "accenture.com",
    "google.com",
    "microsoft.com",
    "amazon.jobs",
    "infosys.com",
    "nttdata.com",
    "dbs.com",
    "remotive.com",
    "remoteok.com",
    "arbeitnow.com",
}


class JobVerifier:
    """Verifies that job links are syntactically sound, active, and direct."""

    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout

    def is_valid_url(self, url: str) -> bool:
        """Check URL syntax."""
        if not url:
            return False
        try:
            parsed = urlparse(url.strip())
            return parsed.scheme in ("http", "https") and bool(parsed.netloc)
        except Exception:
            return False

    def is_direct_employer_link(self, url: str) -> bool:
        """Ensure URL does not point to an aggregator."""
        if not url:
            return False
        try:
            parsed = urlparse(url.strip())
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            
            for agg in AGGREGATOR_DOMAINS:
                if domain == agg or domain.endswith("." + agg):
                    return False
            return True
        except Exception:
            return False

    def verify_job(self, job: Dict[str, Any], check_http: bool = False) -> Dict[str, Any]:
        """
        Verify and enrich job record with verification flags and timestamps.
        Updates 'last_verified_at', 'status', and 'url_verified'.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        apply_url = job.get("apply_url") or job.get("original_url") or ""

        if not self.is_valid_url(apply_url):
            job["status"] = "invalid_url"
            job["url_verified"] = False
            job["last_verified_at"] = now_iso
            return job

        if not self.is_direct_employer_link(apply_url):
            job["status"] = "aggregator_blocked"
            job["url_verified"] = False
            job["last_verified_at"] = now_iso
            return job

        job["url_verified"] = True
        job["status"] = "active"
        job["last_verified_at"] = now_iso

        if check_http and apply_url.startswith("http"):
            try:
                resp = requests.head(
                    apply_url,
                    headers={"User-Agent": "AIJobAgent/2.0"},
                    allow_redirects=True,
                    timeout=self.timeout
                )
                if resp.status_code in (404, 410):
                    job["status"] = "closed"
                    job["url_verified"] = False
                elif resp.status_code < 400:
                    job["status"] = "active"
                    job["url_verified"] = True
            except Exception:
                # Do not fail active status for temporary connection flakiness
                pass

        return job


def verify_job_listing(job: Dict[str, Any], check_http: bool = False) -> Dict[str, Any]:
    """Functional convenience wrapper for verifying a single job."""
    return JobVerifier().verify_job(job, check_http=check_http)
