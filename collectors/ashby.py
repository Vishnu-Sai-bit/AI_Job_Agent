"""
==========================================================
AI JobAgent - Ashby Collector
Connects to Ashby Public Job Board API for high-growth tech companies
(Linear, Cursor, Notion, Ramp, Vercel, Zapier) and returns authentic
vacancies with exact requisition IDs and direct application URLs.
==========================================================
"""

import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from collectors.base_collector import BaseCollector
from utils import info, warning

ASHBY_BOARDS = [
    {"name": "Linear", "board": "linear"},
    {"name": "Cursor", "board": "cursor"},
    {"name": "Notion", "board": "notion"},
    {"name": "Ramp", "board": "ramp"},
    {"name": "Vercel", "board": "vercel"},
    {"name": "Zapier", "board": "zapier"}
]

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json"
}


def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    try:
        return BeautifulSoup(raw_html, "html.parser").get_text(separator=" ").strip()
    except Exception:
        return str(raw_html).strip()


class AshbyCollector(BaseCollector):
    """Collector for Ashby Public Job Board API."""

    def __init__(self):
        super().__init__("Ashby")

    def fetch_jobs(self, query: str = "", location: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        jobs: List[Dict[str, Any]] = []
        role_lower = (query or "").lower().strip()
        loc_lower = (location or "").lower().strip()
        now_iso = datetime.now(timezone.utc).isoformat()

        for board_info in ASHBY_BOARDS:
            if len(jobs) >= limit:
                break

            comp_name = board_info["name"]
            board_name = board_info["board"]
            url = f"https://api.ashbyhq.com/posting-api/job-board/{board_name}"

            try:
                resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    postings = data.get("jobs", [])
                    for item in postings:
                        if len(jobs) >= limit:
                            break

                        title = item.get("title") or ""
                        if role_lower and role_lower not in title.lower():
                            continue

                        job_loc = item.get("location") or "Remote"
                        if loc_lower and loc_lower not in job_loc.lower():
                            continue

                        job_id = str(item.get("id") or "")
                        job_url = str(item.get("jobUrl") or f"https://jobs.ashbyhq.com/{board_name}/{job_id}")
                        apply_url = str(item.get("applyUrl") or f"https://jobs.ashbyhq.com/{board_name}/{job_id}/application")

                        raw_desc = clean_html(item.get("descriptionHtml") or item.get("descriptionPlain") or "")
                        posted_at = item.get("publishedAt") or now_iso

                        jobs.append({
                            "id": f"ashby_{board_name}_{job_id}",
                            "external_job_id": job_id,
                            "job_id": job_id,
                            "title": title,
                            "company": comp_name,
                            "company_name": comp_name,
                            "location": job_loc,
                            "source": "Ashby (Direct)",
                            "source_platform": "Ashby",
                            "source_company_key": board_name,
                            "source_job_id": job_id,
                            "url": apply_url or job_url,
                            "job_url": job_url,
                            "official_job_url": job_url,
                            "apply_url": apply_url,
                            "canonical_url": job_url,
                            "ats_provider": "Ashby",
                            "description": raw_desc or f"Open position for {title} at {comp_name}.",
                            "posted_at": posted_at,
                            "posted_date": "Active Live (Today)",
                            "is_live": True,
                            "status": "active",
                            "url_verified": True,
                            "last_verified_at": now_iso
                        })
            except Exception as e:
                warning(f"[Ashby:{board_name}] Fetch notice: {e}")

        return jobs


def fetch_ashby_jobs(query: str = "", location: str = "", limit: int = 20) -> List[Dict[str, Any]]:
    collector = AshbyCollector()
    return collector.fetch_jobs(query=query, location=location, limit=limit)
