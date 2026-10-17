"""
==========================================================
AI JobAgent - Direct Company Careers Provider
Loads verified employer-hosted openings (Accenture, Google,
Microsoft, Amazon, Infosys, etc.) with exact requisition IDs.
==========================================================
"""

import json
from pathlib import Path
from typing import List
from models import JobData
from config import BASE_DIR
from utils import info, warning


class CompanyCareersProvider:
    def __init__(self):
        self.name = "Company Careers"

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
                title = item.get("title") or ""
                company = item.get("company") or ""
                desc = item.get("description") or ""

                if role_lower and (role_lower not in title.lower() and role_lower not in company.lower() and role_lower not in desc.lower()):
                    continue

                j_id = str(item.get("job_id") or item.get("external_job_id") or item.get("id") or "")
                apply_url = item.get("apply_url") or item.get("official_job_url") or item.get("url") or ""
                loc = item.get("location") or "India"

                job_obj = JobData(
                    provider=item.get("ats_provider") or "Company Careers",
                    provider_id=j_id,
                    company=company,
                    title=title,
                    description=desc,
                    location=loc,
                    apply_url=apply_url,
                    company_url=item.get("official_job_url") or apply_url,
                    skills=item.get("skills", []),
                    experience=item.get("experience", "1-3 yrs"),
                    active=True
                )
                jobs.append(job_obj)
        except Exception as e:
            warning(f"CompanyCareersProvider error: {e}")

        return jobs


def search_company_careers_jobs(role: str = "") -> List[JobData]:
    provider = CompanyCareersProvider()
    return provider.search_jobs(role)
