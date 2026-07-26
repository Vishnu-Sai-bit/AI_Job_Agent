"""
==========================================================
AI JobAgent - Adzuna Provider
==========================================================
"""

from typing import List

from providers.base import BaseProvider
from models import JobData
from config import ADZUNA_APP_ID, ADZUNA_APP_KEY

from services.resume.location_parser import (
    parse_location,
    is_remote,
)

class AdzunaProvider(BaseProvider):
    def __init__(self):
        super().__init__("Adzuna", "https://api.adzuna.com/v1/api/jobs/in/search/1")

    def search_jobs(self, role: str = "") -> List[JobData]:
        if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
            return []

        params = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_APP_KEY,
            "results_per_page": 10
        }
        if role:
            params["what"] = role

        raw_data = self.fetch_raw_data(params=params)
        keywords = role.lower().split() if role else []
        jobs = []
        for item in raw_data.get("results", []):
            job = self.build_job(item, keywords)
            if job:
                jobs.append(job)
        return jobs

    def build_job(self, item: dict, keywords: List[str]) -> JobData | None:
        title = (item.get("title") or "").strip()
        company_info = item.get("company") or {}
        company = (company_info.get("display_name") or "").strip()
        apply_url = (item.get("redirect_url") or "").strip()

        if not title or not company or not apply_url:
            return None

        description = item.get("description") or ""
        
        location_info = item.get("location") or {}
        area = location_info.get("area") or []
        loc_name = area[0] if area else "India"
        location_data = parse_location(loc_name)
        
        skills = []
        category_info = item.get("category") or {}
        category = category_info.get("label") or ""
        if category:
            skills.append(category)

        search_text = (title + " " + description + " " + " ".join(skills)).lower()
        if keywords and not any(keyword in search_text for keyword in keywords):
            return None

        min_sal = item.get("salary_min")
        max_sal = item.get("salary_max")
        salary_text = "Not Mentioned"
        if min_sal or max_sal:
            sal_parts = []
            if min_sal:
                sal_parts.append(f"INR {min_sal}")
            if max_sal:
                sal_parts.append(f"INR {max_sal}")
            salary_text = " - ".join(sal_parts)

        work_type = "Remote" if is_remote(loc_name) else "Onsite"

        return JobData(
            provider=self.name,
            provider_id=str(item.get("id", "")),
            company=company,
            company_logo="",
            company_website="",
            title=title,
            category=category,
            description=description,
            employment_type="Full Time",
            work_type=work_type,
            location=loc_name,
            city=location_data["city"],
            state=location_data["state"],
            country=location_data["country"],
            remote=work_type == "Remote",
            salary=salary_text,
            currency="INR",
            min_salary=int(min_sal) if min_sal else None,
            max_salary=int(max_sal) if max_sal else None,
            experience="Not Mentioned",
            experience_years=0.0,
            skills=skills,
            publication_date=item.get("created", ""),
            apply_url=apply_url,
            company_url="",
            active=True,
        )

def search_adzuna_jobs(role: str = "") -> List[JobData]:
    provider = AdzunaProvider()
    return provider.search_jobs(role)
