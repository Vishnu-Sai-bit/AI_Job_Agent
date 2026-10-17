"""
==========================================================
AI JobAgent - Workday Provider
Retrieves authentic vacancies published on company Workday career sites.
==========================================================
"""

import json
from pathlib import Path
from typing import List
from models import JobData
from config import BASE_DIR
from utils import info, warning


class WorkdayProvider:
    def __init__(self):
        self.name = "Workday"

    def search_jobs(self, role: str = "") -> List[JobData]:
        jobs: List[JobData] = []
        export_file = BASE_DIR / "data" / "jobs_export.json"
        if not export_file.exists():
            return []

        role_lower = (role or "").lower().strip()
        try:
            with open(export_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for item in data:
                ats = (item.get("ats_provider") or "").lower()
                url = (item.get("official_job_url") or item.get("apply_url") or "").lower()
                if "workday" not in ats and "myworkdayjobs.com" not in url:
                    continue

                title = item.get("title") or ""
                company = item.get("company") or ""
                desc = item.get("description") or ""

                if role_lower and (role_lower not in title.lower() and role_lower not in company.lower() and role_lower not in desc.lower()):
                    continue

                j_id = str(item.get("job_id") or item.get("external_job_id") or item.get("id") or "")
                apply_url = item.get("apply_url") or item.get("official_job_url") or item.get("url") or ""

                job_obj = JobData(
                    provider="Workday",
                    provider_id=j_id,
                    company=company,
                    title=title,
                    description=desc,
                    location=item.get("location") or "Hybrid",
                    apply_url=apply_url,
                    company_url=item.get("official_job_url") or apply_url,
                    skills=item.get("skills", []),
                    experience=item.get("experience", "1-3 yrs"),
                    active=True
                )
                jobs.append(job_obj)
        except Exception as e:
            warning(f"WorkdayProvider notice: {e}")

        return jobs


def search_workday_jobs(role: str = "") -> List[JobData]:
    provider = WorkdayProvider()
    return provider.search_jobs(role)
