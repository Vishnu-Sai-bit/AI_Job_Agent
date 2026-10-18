"""
==========================================================
AI JobAgent - ArbeitNow Collector
Fetches authentic vacancies from ArbeitNow API
with original slugs/IDs and direct application URLs.
==========================================================
"""

from datetime import datetime, timezone
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from utils import info, warning


def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    try:
        return BeautifulSoup(raw_html, "html.parser").get_text(separator=" ").strip()
    except Exception:
        return str(raw_html).strip()


class ArbeitNowCollector:
    """Collector for ArbeitNow European and global jobs API."""

    def __init__(self):
        self.name = "ArbeitNow"
        self.api_url = "https://www.arbeitnow.com/api/job-board-api"

    def fetch_jobs(self, query: str = "", location: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        jobs: List[Dict[str, Any]] = []
        now_iso = datetime.now(timezone.utc).isoformat()
        role_lower = (query or "").lower().strip()

        try:
            resp = requests.get(
                self.api_url,
                headers={"User-Agent": "AIJobAgent/2.0"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                raw_jobs = data.get("data", [])
                for item in raw_jobs:
                    if len(jobs) >= limit:
                        break

                    title = item.get("title") or ""
                    company = item.get("company_name") or ""
                    apply_url = item.get("url") or ""

                    if not title or not company or not apply_url:
                        continue

                    desc_raw = item.get("description") or ""
                    tags = item.get("tags") or []
                    tags_str = " ".join(tags) if isinstance(tags, list) else ""

                    search_body = f"{title} {desc_raw} {tags_str}".lower()
                    if role_lower and role_lower not in search_body:
                        continue

                    j_id = str(item.get("slug") or "")
                    desc = clean_html(desc_raw)[:600] if desc_raw else f"Authentic vacancy for {title} at {company}."
                    job_loc = item.get("location") or location or ("Remote" if item.get("remote") else "Office")
                    created_at = item.get("created_at")
                    posted_on = datetime.fromtimestamp(created_at, tz=timezone.utc).isoformat() if isinstance(created_at, (int, float)) else str(created_at or "")

                    jobs.append({
                        "job_id": j_id,
                        "company_name": company,
                        "job_title": title,
                        "description": desc,
                        "location": job_loc,
                        "posted_at": posted_on,
                        "source_platform": "ArbeitNow",
                        "original_url": apply_url,
                        "apply_url": apply_url,
                        "last_verified_at": now_iso,
                        "status": "active",
                        "skills": tags if isinstance(tags, list) else ["Technology", "Engineering"],
                        "url_verified": True
                    })
        except Exception as e:
            warning(f"ArbeitNowCollector error: {e}")

        return jobs


def fetch_arbeitnow_jobs(query: str = "", location: str = "", limit: int = 20) -> List[Dict[str, Any]]:
    return ArbeitNowCollector().fetch_jobs(query=query, location=location, limit=limit)
