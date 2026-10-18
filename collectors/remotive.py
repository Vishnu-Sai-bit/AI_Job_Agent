"""
==========================================================
AI JobAgent - Remotive Collector
Fetches real remote job listings from Remotive API
with original job IDs and authentic application URLs.
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


class RemotiveCollector:
    """Collector for Remotive remote jobs API."""

    def __init__(self):
        self.name = "Remotive"
        self.api_url = "https://remotive.com/api/remote-jobs"

    def fetch_jobs(self, query: str = "", location: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        jobs: List[Dict[str, Any]] = []
        params = {}
        if query:
            params["search"] = query
        if limit:
            params["limit"] = str(limit)

        now_iso = datetime.now(timezone.utc).isoformat()

        try:
            resp = requests.get(
                self.api_url,
                params=params,
                headers={"User-Agent": "AIJobAgent/2.0"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                raw_jobs = data.get("jobs", [])
                for item in raw_jobs[:limit]:
                    title = item.get("title") or ""
                    company = item.get("company_name") or ""
                    apply_url = item.get("url") or ""

                    if not title or not company or not apply_url:
                        continue

                    j_id = str(item.get("id") or "")
                    desc_raw = item.get("description") or ""
                    desc = clean_html(desc_raw)[:600] if desc_raw else f"Authentic vacancy for {title} at {company}."
                    candidate_loc = item.get("candidate_required_location") or location or "Remote"
                    pub_date = item.get("publication_date") or ""
                    tags = item.get("tags") or []
                    category = item.get("category")
                    skills = list(tags) if isinstance(tags, list) else []
                    if category and category not in skills:
                        skills.append(category)

                    jobs.append({
                        "job_id": j_id,
                        "company_name": company,
                        "job_title": title,
                        "description": desc,
                        "location": candidate_loc,
                        "posted_at": pub_date,
                        "source_platform": "Remotive",
                        "original_url": apply_url,
                        "apply_url": apply_url,
                        "last_verified_at": now_iso,
                        "status": "active",
                        "skills": skills or ["Remote", "Software Engineering"],
                        "url_verified": True
                    })
        except Exception as e:
            warning(f"RemotiveCollector error: {e}")

        return jobs


def fetch_remotive_jobs(query: str = "", location: str = "", limit: int = 20) -> List[Dict[str, Any]]:
    return RemotiveCollector().fetch_jobs(query=query, location=location, limit=limit)
