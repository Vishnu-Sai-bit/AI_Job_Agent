"""
==========================================================
AI JobAgent - Enterprise Job Deduplication Engine
Detects and eliminates duplicate job vacancies across
real-time live feeds, verified ATS portals, and aggregator APIs.
==========================================================
"""

import re
import urllib.parse
from typing import Dict, Any, List, Optional, Tuple, Set


def normalize_canonical_company(company: Optional[str]) -> str:
    """
    Normalize company names across different aggregators and ATS portals.
    Examples:
    - 'Tata Consultancy Services (TCS)' -> 'tcs'
    - 'EY (Ernst & Young)' -> 'ey'
    - 'Google Inc.' -> 'google'
    - 'Razorpay Software Pvt Ltd' -> 'razorpay'
    """
    if not company:
        return ""
    c = str(company).lower().strip()
    
    # Handle known abbreviations in parentheses: e.g. Tata Consultancy Services (TCS) -> tcs
    m_abbr = re.search(r"\(([a-z0-9\s]{2,10})\)", c)
    if m_abbr and len(m_abbr.group(1).strip()) <= 6:
        # e.g. TCS or EY
        abbr = m_abbr.group(1).strip()
        if abbr in ("tcs", "ey", "ibm", "hcl", "pwc", "hp"):
            return abbr

    # Strip parentheticals
    c = re.sub(r"[\(\[\{].*?[\)\]\}]", "", c)

    # Strip common legal and corporate filler suffixes
    c = re.sub(
        r"\b(inc|incorporated|corp|corporation|llc|ltd|limited|pvt|private|technologies|tech|solutions|group|services|software|systems|system|india|careers|global)\b",
        "",
        c
    )
    # Strip non-alphanumeric
    c = re.sub(r"[^a-z0-9]", "", c)
    return c


def normalize_canonical_title(title: Optional[str]) -> str:
    """
    Extract the core role title, stripping marketing buzzwords,
    location suffixes, and formatting prefixes.
    Examples:
    - 'Software Engineer | Java/Golang/Python/ C/C++ | 2 to 4 years | Bangalore' -> 'software engineer'
    - '[Hiring] Junior Data Analyst (Bangalore, India)' -> 'junior data analyst'
    - 'Lead Software Engineer - Mobile (Flutter)' -> 'lead software engineer mobile flutter'
    """
    if not title:
        return ""
    t = str(title).lower().strip()

    # 1. If title is formatted with pipe delimiters (like Cisco or our rich formatter), take the first portion
    if "|" in t:
        t = t.split("|")[0].strip()

    # 2. Strip parenthetical and bracketed content
    t = re.sub(r"[\(\[\{].*?[\)\]\}]", " ", t)

    # 3. Strip recruitment noise prefixes & buzzwords
    noise_patterns = [
        r"(?i)\b(urgent\s*hiring|immediate\s*joiner|immediate\s*requirement|opening\s*for|urgently\s*required|hiring\s*for|we\s*are\s*hiring|job\s*opening)\b",
        r"(?i)\b(fresher|internship|entry\s*level|experienced)\b",
        r"(?i)\b(remote|hybrid|work\s*from\s*home|onsite)\b",
    ]
    for np in noise_patterns:
        t = re.sub(np, " ", t)

    # 4. Strip common city/location suffixes at end of title: e.g. 'Data Analyst - Bangalore'
    t = re.sub(
        r"(?i)\s*[-–—:/]\s*(bangalore|bengaluru|hyderabad|pune|mumbai|delhi|noida|gurugram|gurgaon|chennai|kolkata|india|usa|uk)\s*$",
        "",
        t
    )

    # 5. Clean punctuation and non-alphanumeric characters
    t = re.sub(r"[^a-z0-9\s]", " ", t)

    # 6. Filter out minor filler words
    stop_words = {"and", "or", "for", "in", "at", "the", "with", "a", "an", "of", "to"}
    tokens = [w for w in t.split() if w not in stop_words and len(w) > 1]
    return " ".join(tokens)


def normalize_canonical_url(url: Optional[str]) -> str:
    """
    Normalize URLs by stripping tracking parameters, session anchors,
    and trailing slashes while preserving authentic job identifiers.
    """
    if not url or url.strip() == "#":
        return ""
    try:
        raw_url = url.strip()
        parsed = urllib.parse.urlparse(raw_url)
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]

        clean_path = parsed.path.rstrip("/")

        # Preserve genuine requisition query parameter if present
        preserved_params = []
        if parsed.query:
            query_pairs = urllib.parse.parse_qsl(parsed.query)
            for k, v in query_pairs:
                k_low = k.lower()
                if k_low in ("currentjobid", "jobid", "jobreferencecode", "req_id", "requisition_id"):
                    preserved_params.append(f"{k_low}={v}")

        query_str = f"?{'&'.join(sorted(preserved_params))}" if preserved_params else ""
        return f"{netloc}{clean_path}{query_str}"
    except Exception:
        return url.strip().split("?")[0].rstrip("/")


def extract_canonical_req_id(job: Dict[str, Any]) -> str:
    """Extract clean requisition or external job identifier."""
    raw_id = str(job.get("external_job_id") or job.get("job_id") or job.get("id") or "").strip()
    if not raw_id or raw_id.lower() in ("none", "null", "false", "0", ""):
        return ""
    # Strip any URL prefixes if whole URL was passed as ID
    if "/" in raw_id:
        raw_id = raw_id.rstrip("/").split("/")[-1]
    return raw_id


def deduplicate_jobs(
    jobs: List[Dict[str, Any]],
    preserve_order: bool = True
) -> List[Dict[str, Any]]:
    """
    Deduplicate job listings using multi-factor identity matching:
    1. Canonical URL match (normalized without tracking parameters)
    2. Company + Requisition / External Job ID match
    3. Canonical Company + Normalized Role Title match
    """
    if not jobs:
        return []

    seen_urls: Set[str] = set()
    seen_req_keys: Set[str] = set()
    seen_comp_titles: Set[str] = set()

    unique_jobs: List[Dict[str, Any]] = []

    for job in jobs:
        if not isinstance(job, dict):
            continue

        comp = normalize_canonical_company(job.get("company"))
        title = normalize_canonical_title(job.get("raw_title") or job.get("title"))
        req_id = extract_canonical_req_id(job)
        url = normalize_canonical_url(job.get("official_job_url") or job.get("apply_url") or job.get("url"))

        is_dup = False

        # 1. URL Check
        if url and url in seen_urls:
            is_dup = True

        # 2. Requisition ID Check per Company
        if comp and req_id and len(req_id) >= 4:
            req_key = f"{comp}::{req_id}"
            if req_key in seen_req_keys:
                is_dup = True

        # 3. Canonical Company + Normalized Title Check
        if comp and title:
            comp_title_key = f"{comp}::{title}"
            if comp_title_key in seen_comp_titles:
                is_dup = True

        if is_dup:
            continue

        # Register identifiers
        if url:
            seen_urls.add(url)
        if comp and req_id and len(req_id) >= 4:
            seen_req_keys.add(f"{comp}::{req_id}")
        if comp and title:
            seen_comp_titles.add(f"{comp}::{title}")

        unique_jobs.append(job)

    return unique_jobs
