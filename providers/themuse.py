"""
==========================================================
AI JobAgent - TheMuse Provider
==========================================================
"""

from typing import List

from providers.base import BaseProvider
from models import JobData

from services.resume.location_parser import (
    parse_location,
    is_remote,
)

class TheMuseProvider(BaseProvider):
    def __init__(self):
        super().__init__("TheMuse", "https://www.themuse.com/api/public/jobs")

    def search_jobs(self, role: str = "") -> List[JobData]:
        params = {
            "page": "1"
        }
        if role:
            params["desc"] = role

        raw_data = self.fetch_raw_data(params=params)
        keywords = role.lower().split() if role else []
        jobs = []
        for item in raw_data.get("results", []):
            job = self.build_job(item, keywords)
            if job:
                jobs.append(job)
        return jobs

    def build_job(self, item: dict, keywords: List[str]) -> JobData | None:
        title = (item.get("name") or "").strip()
        company_info = item.get("company") or {}
        company = (company_info.get("name") or "").strip()
        
        refs = item.get("refs") or {}
        apply_url = (refs.get("landing_page") or "").strip()

        if not title or not company or not apply_url:
            return None

        description = item.get("contents") or ""
        
        locations = item.get("locations") or []
        loc_name = locations[0].get("name") if locations else "Worldwide"
        
        skills = []
        categories = item.get("categories") or []
        for cat in categories:
            cat_name = cat.get("name")
            if cat_name and cat_name not in skills:
                skills.append(cat_name)

        search_text = (title + " " + description + " " + " ".join(skills)).lower()
        if keywords and not any(keyword in search_text for keyword in keywords):
            return None

        location_data = parse_location(loc_name)
        work_type = "Remote" if is_remote(loc_name) else "Onsite"

        return JobData(
            provider=self.name,
            provider_id=str(item.get("id", "")),
            company=company,
            company_logo="",
            company_website="",
            title=title,
            category=categories[0].get("name") if categories else "",
            description=description,
            employment_type="Full Time",
            work_type=work_type,
            location=loc_name,
            city=location_data["city"],
            state=location_data["state"],
            country=location_data["country"],
            remote=work_type == "Remote",
            salary="Not Mentioned",
            currency="",
            min_salary=None,
            max_salary=None,
            experience="Not Mentioned",
            experience_years=0.0,
            skills=skills,
            publication_date=item.get("publication_date", ""),
            apply_url=apply_url,
            company_url="",
            active=True,
        )

def search_themuse_jobs(role: str = "") -> List[JobData]:
    provider = TheMuseProvider()
    return provider.search_jobs(role)
