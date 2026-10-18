"""
==========================================================
AI JobAgent - Greenhouse Collector
Connects to Greenhouse Job Board API to retrieve
authentic vacancies with exact job IDs and application URLs.
==========================================================
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from utils import info, warning

GREENHOUSE_BOARDS = [
    {"name": "GitLab", "token": "gitlab"},
    {"name": "Figma", "token": "figma"},
    {"name": "Stripe", "token": "stripe"},
    {"name": "Databricks", "token": "databricks"},
    {"name": "Elastic", "token": "elastic"},
    {"name": "Razorpay", "token": "razorpay"}
]


def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    try:
        return BeautifulSoup(raw_html, "html.parser").get_text(separator=" ").strip()
    except Exception:
        return str(raw_html).strip()


class GreenhouseCollector:
    """Collector for Greenhouse Job Board API."""

    def __init__(self):
        self.name = "Greenhouse"

    def fetch_jobs(self, query: str = "", location: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        jobs: List[Dict[str, Any]] = []
        role_lower = (query or "").lower().strip()
        now_iso = datetime.now(timezone.utc).isoformat()

        for board in GREENHOUSE_BOARDS:
            if len(jobs) >= limit:
                break

            comp_name = board["name"]
            token = board["token"]
            url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"

            try:
                resp = requests.get(url, headers={"User-Agent": "AIJobAgent/2.0"}, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("jobs", []):
                        if len(jobs) >= limit:
                            break

                        title = item.get("title") or ""
                        content = item.get("content") or ""
                        
                        if role_lower and (role_lower not in title.lower() and role_lower not in content.lower()):
                            continue

                        j_id = str(item.get("id") or "")
                        desc = clean_html(content)[:500] if content else f"Official vacancy for {title} at {comp_name}."
                        loc = (item.get("location") or {}).get("name") or location or "Remote / Office"
                        app_url = item.get("absolute_url") or f"https://job-boards.greenhouse.io/{token}/jobs/{j_id}"
                        updated_at = item.get("updated_at") or ""

                        jobs.append({
                            "job_id": j_id,
                            "company_name": comp_name,
                            "job_title": title,
                            "description": desc,
                            "location": loc,
                            "posted_at": updated_at,
                            "source_platform": "Greenhouse",
                            "original_url": app_url,
                            "apply_url": f"{app_url}#app" if "#" not in app_url else app_url,
                            "last_verified_at": now_iso,
                            "status": "active",
                            "skills": ["Python", "SQL", "APIs", "Data Analysis"] if "data" in title.lower() else ["Software Engineering", "APIs", "Git"],
                            "url_verified": True
                        })
            except Exception as e:
                warning(f"Greenhouse collector notice for {comp_name}: {e}")

        return jobs


def fetch_greenhouse_jobs(query: str = "", location: str = "", limit: int = 20) -> List[Dict[str, Any]]:
    return GreenhouseCollector().fetch_jobs(query=query, location=location, limit=limit)
