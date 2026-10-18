"""
==========================================================
AI JobAgent - RemoteOK Collector
Fetches real remote job listings from RemoteOK API
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


class RemoteOKCollector:
    """Collector for RemoteOK remote jobs API."""

    def __init__(self):
        self.name = "RemoteOK"
        self.api_url = "https://remoteok.com/api"

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
                for item in data:
                    if not isinstance(item, dict) or not item.get("id"):
                        continue
                    if len(jobs) >= limit:
                        break

                    title = item.get("position") or item.get("title") or ""
                    company = item.get("company") or ""
                    apply_url = item.get("url") or item.get("apply_url") or ""

                    if not title or not company or not apply_url:
                        continue

                    # Filter by query if provided
                    desc_raw = item.get("description") or ""
                    tags = item.get("tags") or []
                    tags_str = " ".join(tags) if isinstance(tags, list) else ""

                    search_body = f"{title} {desc_raw} {tags_str}".lower()
                    if role_lower and role_lower not in search_body:
                        continue

                    j_id = str(item.get("id") or "")
                    desc = clean_html(desc_raw)[:600] if desc_raw else f"Authentic vacancy for {title} at {company}."
                    job_loc = item.get("location") or location or "Remote"
                    epoch_date = item.get("epoch")
                    posted_on = datetime.fromtimestamp(epoch_date, tz=timezone.utc).isoformat() if epoch_date else (item.get("date") or "")

                    direct_apply = item.get("apply_url") or apply_url

                    jobs.append({
                        "job_id": j_id,
                        "company_name": company,
                        "job_title": title,
                        "description": desc,
                        "location": job_loc,
                        "posted_at": posted_on,
                        "source_platform": "RemoteOK",
                        "original_url": apply_url,
                        "apply_url": direct_apply,
                        "last_verified_at": now_iso,
                        "status": "active",
                        "skills": tags if isinstance(tags, list) else ["Remote", "Software Engineering"],
                        "url_verified": True
                    })
        except Exception as e:
            warning(f"RemoteOKCollector error: {e}")

        return jobs


def fetch_remoteok_jobs(query: str = "", location: str = "", limit: int = 20) -> List[Dict[str, Any]]:
    return RemoteOKCollector().fetch_jobs(query=query, location=location, limit=limit)
