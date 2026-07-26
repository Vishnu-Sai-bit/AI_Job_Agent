"""
==========================================================
AI JobAgent - RemoteOK Provider
==========================================================
"""

from typing import List

from providers.base import BaseProvider
from models import JobData

from services.resume.salary_parser import (
    parse_salary,
)

from services.resume.location_parser import (
    parse_location,
    is_remote,
)

from services.resume.experience_parser import (
    parse_experience,
)

class RemoteOKProvider(BaseProvider):
    def __init__(self):
        super().__init__("RemoteOK", "https://remoteok.com/api")

    def get_headers(self) -> dict:
        headers = super().get_headers()
        headers["Accept"] = "application/json"
        return headers

    def search_jobs(self, role: str = "") -> List[JobData]:
        raw_data = self.fetch_raw_data()
        keywords = role.lower().split() if role else []
        jobs = []
        
        # Check if response is a list (RemoteOK returns a list where first item is usually info, others are jobs)
        if not isinstance(raw_data, list):
            return jobs
            
        for item in raw_data:
            if not isinstance(item, dict) or "id" not in item:
                continue
            job = self.build_job(item, keywords)
            if job:
                jobs.append(job)
        return jobs

    def build_job(self, item: dict, keywords: List[str]) -> JobData | None:
        title = (item.get("position") or item.get("title") or "").strip()
        company = (item.get("company") or "").strip()
        apply_url = (item.get("url") or "").strip()

        if not title or not company or not apply_url:
            return None

        description = item.get("description") or ""
        skills = item.get("tags", [])
        if not isinstance(skills, list):
            skills = []

        search_text = (title + " " + description + " " + " ".join(skills)).lower()
        if keywords and not any(keyword in search_text for keyword in keywords):
            return None

        category = item.get("category") or ""
        if category and category not in skills:
            skills.append(category)

        location = item.get("location") or "Worldwide"
        location_data = parse_location(location)
        
        salary_text = item.get("salary") or "Not Mentioned"
        salary = parse_salary(salary_text)

        experience_text = item.get("experience") or "Not Mentioned"
        experience_years = parse_experience(experience_text)

        employment_type = item.get("employment_type") or "Full Time"
        work_type = "Remote" if is_remote(location) else "Onsite"

        return JobData(
            provider=self.name,
            provider_id=str(item.get("id", "")),
            company=company,
            company_logo=item.get("company_logo", ""),
            company_website=item.get("company_url", ""),
            title=title,
            category=category,
            description=description,
            employment_type=employment_type,
            work_type=work_type,
            location=location,
            city=location_data["city"],
            state=location_data["state"],
            country=location_data["country"],
            remote=is_remote(location),
            salary=salary["text"],
            currency=salary["currency"],
            min_salary=salary["min_salary"],
            max_salary=salary["max_salary"],
            experience=experience_text,
            experience_years=experience_years,
            skills=skills,
            publication_date=item.get("date", ""),
            apply_url=apply_url,
            company_url=item.get("company_url", ""),
            active=True,
        )

def search_remoteok_jobs(role: str = "") -> List[JobData]:
    provider = RemoteOKProvider()
    return provider.search_jobs(role)