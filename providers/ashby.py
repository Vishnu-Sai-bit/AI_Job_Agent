"""
==========================================================
AI JobAgent - Ashby Provider
Connects directly to Ashby Job Postings API to retrieve
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


class AshbyProvider:
    def __init__(self):
        self.name = "Ashby"

    def search_jobs(self, role: str = "") -> List[JobData]:
        jobs: List[JobData] = []
        boards = COMPANY_ATS_REGISTRY.get("ashby", [])[:5]
        role_lower = (role or "").lower().strip()

        for comp in boards:
            board = comp.get("board")
            comp_name = comp.get("name", "Company")
            if not board:
                continue

            url = f"https://api.ashbyhq.com/posting-api/job-board/{board}"
            try:
                resp = requests.get(url, headers={"User-Agent": "AIJobAgent/2.0"}, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("jobs", []):
                        title = item.get("title") or ""
                        desc = item.get("descriptionPlain") or clean_html(item.get("descriptionHtml") or "")
                        if role_lower and role_lower not in title.lower() and role_lower not in desc.lower():
                            continue

                        j_id = str(item.get("id") or "")
                        loc = item.get("location") or "Remote / Global"
                        app_url = item.get("jobUrl") or item.get("applyUrl") or f"https://jobs.ashbyhq.com/{board}/{j_id}"

                        job_obj = JobData(
                            provider="Ashby",
                            provider_id=j_id,
                            company=comp_name,
                            title=title,
                            description=desc[:1500] if desc else f"Authentic opening for {title} at {comp_name}.",
                            location=loc,
                            apply_url=app_url,
                            company_url=f"https://jobs.ashbyhq.com/{board}",
                            skills=[s.strip() for s in title.replace("/", " ").replace("-", " ").split() if len(s) > 2][:5],
                            active=True
                        )
                        jobs.append(job_obj)
                        if len(jobs) >= 20:
                            break
            except Exception as e:
                warning(f"Ashby fetch notice for {comp_name}: {e}")

            if len(jobs) >= 20:
                break

        return jobs


def search_ashby_jobs(role: str = "") -> List[JobData]:
    provider = AshbyProvider()
    return provider.search_jobs(role)
