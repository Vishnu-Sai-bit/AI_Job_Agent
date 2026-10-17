"""
==========================================================
AI JobAgent - Greenhouse Provider
Connects directly to Greenhouse Job Board API to retrieve
authentic vacancies with exact job IDs and application URLs.
==========================================================
"""

from typing import List
import requests
from bs4 import BeautifulSoup
from models import JobData
from services.job_links.company_registry import COMPANY_ATS_REGISTRY
from utils import info, warning


def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    try:
        return BeautifulSoup(raw_html, "html.parser").get_text(separator=" ").strip()
    except Exception:
        return str(raw_html).strip()


class GreenhouseProvider:
    def __init__(self):
        self.name = "Greenhouse"

    def search_jobs(self, role: str = "") -> List[JobData]:
        jobs: List[JobData] = []
        boards = COMPANY_ATS_REGISTRY.get("greenhouse", [])[:6]
        role_lower = (role or "").lower().strip()

        for comp in boards:
            token = comp.get("token")
            comp_name = comp.get("name", "Company")
            if not token:
                continue

            url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
            try:
                resp = requests.get(url, headers={"User-Agent": "AIJobAgent/2.0"}, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("jobs", []):
                        title = item.get("title") or ""
                        if role_lower and role_lower not in title.lower() and role_lower not in (item.get("content") or "").lower():
                            continue

                        j_id = str(item.get("id") or "")
                        desc = clean_html(item.get("content") or "")
                        loc = (item.get("location") or {}).get("name") or "Remote / Office"
                        app_url = item.get("absolute_url") or f"https://job-boards.greenhouse.io/{token}/jobs/{j_id}"

                        job_obj = JobData(
                            provider="Greenhouse",
                            provider_id=j_id,
                            company=comp_name,
                            title=title,
                            description=desc[:1500] if desc else f"Authentic opening for {title} at {comp_name}.",
                            location=loc,
                            apply_url=app_url,
                            company_url=f"https://job-boards.greenhouse.io/{token}",
                            skills=[s.strip() for s in title.replace("/", " ").replace("-", " ").split() if len(s) > 2][:5],
                            active=True
                        )
                        jobs.append(job_obj)
                        if len(jobs) >= 20:
                            break
            except Exception as e:
                warning(f"Greenhouse fetch notice for {comp_name}: {e}")

            if len(jobs) >= 20:
                break

        return jobs


def search_greenhouse_jobs(role: str = "") -> List[JobData]:
    provider = GreenhouseProvider()
    return provider.search_jobs(role)
