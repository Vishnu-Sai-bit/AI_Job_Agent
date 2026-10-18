"""
==========================================================
AI JobAgent - Multi-Factor Deduplication Service
Prevents duplicate job records across multiple sources using:
1. Exact & canonical URL matching
2. (Company Name + Requisition/Job ID)
3. (Company Name + Job Title + Location)
==========================================================
"""

import re
from typing import List, Dict, Any, Set
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse


def canonicalize_url(url: str) -> str:
    """Strip tracking query parameters (utm_*, ref, source, etc.) and trailing slashes."""
    if not url:
        return ""
    try:
        parsed = urlparse(url.strip())
        query_params = parse_qsl(parsed.query, keep_blank_values=False)
        filtered_params = [
            (k, v) for k, v in query_params
            if not k.lower().startswith("utm_")
            and k.lower() not in ("ref", "source", "trk", "tracking", "gh_src", "lever-source")
        ]
        # Sort query params for deterministic string representation
        filtered_params.sort(key=lambda x: x[0])
        clean_query = urlencode(filtered_params)
        path = parsed.path.rstrip("/")
        return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path, "", clean_query, "")).lower()
    except Exception:
        return url.strip().lower().rstrip("/")


def clean_text_key(text: str) -> str:
    """Normalize text for cross-platform fuzzy key generation."""
    if not text:
        return ""
    return re.sub(r"[^a-z0-9]", "", text.lower())


class JobDeduplicator:
    """Multi-factor job deduplication engine."""

    def __init__(self):
        self.seen_urls: Set[str] = set()
        self.seen_company_req_ids: Set[str] = set()
        self.seen_company_title_loc: Set[str] = set()

    def is_duplicate(self, job: Dict[str, Any]) -> bool:
        """Check if job was already registered in current context."""
        url = job.get("apply_url") or job.get("original_url") or ""
        canon_url = canonicalize_url(url)
        
        comp_key = clean_text_key(job.get("company_name") or "")
        req_id = str(job.get("job_id") or "").strip().lower()
        title_key = clean_text_key(job.get("job_title") or "")
        loc_key = clean_text_key(job.get("location") or "")

        # 1. URL factor
        if canon_url and canon_url in self.seen_urls:
            return True

        # 2. Company + Requisition ID factor
        if comp_key and req_id and req_id not in ("none", "0", ""):
            comp_req_key = f"{comp_key}:{req_id}"
            if comp_req_key in self.seen_company_req_ids:
                return True

        # 3. Company + Title + Location factor
        if comp_key and title_key:
            ctl_key = f"{comp_key}:{title_key}:{loc_key}"
            if ctl_key in self.seen_company_title_loc:
                return True

        return False

    def register(self, job: Dict[str, Any]) -> None:
        """Add job signatures to tracking sets."""
        url = job.get("apply_url") or job.get("original_url") or ""
        canon_url = canonicalize_url(url)
        if canon_url:
            self.seen_urls.add(canon_url)

        comp_key = clean_text_key(job.get("company_name") or "")
        req_id = str(job.get("job_id") or "").strip().lower()
        title_key = clean_text_key(job.get("job_title") or "")
        loc_key = clean_text_key(job.get("location") or "")

        if comp_key and req_id and req_id not in ("none", "0", ""):
            self.seen_company_req_ids.add(f"{comp_key}:{req_id}")

        if comp_key and title_key:
            self.seen_company_title_loc.add(f"{comp_key}:{title_key}:{loc_key}")

    def deduplicate(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out duplicates while preserving original order and highest completeness."""
        unique_jobs: List[Dict[str, Any]] = []
        for job in jobs:
            if not self.is_duplicate(job):
                self.register(job)
                unique_jobs.append(job)
        return unique_jobs


def deduplicate_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convenience functional helper for deduplicating job records."""
    deduper = JobDeduplicator()
    return deduper.deduplicate(jobs)
