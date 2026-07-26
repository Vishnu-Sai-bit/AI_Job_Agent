"""
==========================================================
AI JobAgent - JSearch Provider (RapidAPI)
==========================================================
"""

from typing import List

from providers.base import BaseProvider
from models import JobData
from config import RAPIDAPI_KEY, RAPIDAPI_HOST

from services.resume.location_parser import (
    is_remote,
)

class JSearchProvider(BaseProvider):
    def __init__(self):
        super().__init__("JSearch", "https://jsearch.p.rapidapi.com/search-v2")

    def get_headers(self) -> dict:
        headers = super().get_headers()
        headers["X-RapidAPI-Key"] = RAPIDAPI_KEY
        headers["X-RapidAPI-Host"] = RAPIDAPI_HOST
        return headers

    def search_jobs(self, role: str = "") -> List[JobData]:
        if not RAPIDAPI_KEY or "YOUR_RAPIDAPI_KEY" in RAPIDAPI_KEY:
            # Return empty list gracefully if key is placeholder or empty
            return []

        params = {
            "query": role if role else "Data Analyst",
            "page": "1",
            "num_pages": "2"
        }

        raw_data = self.fetch_raw_data(params=params)
        keywords = role.lower().split() if role else []
        jobs = []
        for item in raw_data.get("data", []):
            job = self.build_job(item, keywords)
            if job:
                jobs.append(job)
        return jobs

    def build_job(self, item: dict, keywords: List[str]) -> JobData | None:
        title = (item.get("job_title") or "").strip()
        company = (item.get("employer_name") or "").strip()
        apply_url = (item.get("job_apply_link") or "").strip()

        if not title or not company or not apply_url:
            return None

        description = item.get("job_description") or ""
        skills = item.get("job_required_skills") or []
        if not isinstance(skills, list):
            skills = []

        search_text = (title + " " + description + " " + " ".join(skills)).lower()
        if keywords and not any(keyword in search_text for keyword in keywords):
            return None

        city = item.get("job_city") or ""
        state = item.get("job_state") or ""
        country = item.get("job_country") or ""

        location_parts = [c for c in [city, state, country] if c]
        location = ", ".join(location_parts) if location_parts else "Remote"

        remote = item.get("job_is_remote") or False
        work_type = "Remote" if remote or is_remote(location) else "Onsite"

        min_sal = item.get("job_min_salary")
        max_sal = item.get("job_max_salary")
        currency = item.get("job_salary_currency") or ""

        salary_text = "Not Mentioned"
        if min_sal or max_sal:
            sal_parts = []
            if min_sal:
                sal_parts.append(f"{currency} {min_sal}")
            if max_sal:
                sal_parts.append(f"{currency} {max_sal}")
            salary_text = " - ".join(sal_parts)

        exp_months = item.get("job_required_experience_in_months")
        experience_years = round(exp_months / 12.0, 1) if exp_months else 0.0
        experience_text = f"{experience_years} years" if experience_years else "Not Mentioned"

        employment_type = item.get("job_employment_type") or "Full Time"

        return JobData(
            provider=self.name,
            provider_id=str(item.get("job_id", "")),
            company=company,
            company_logo=item.get("employer_logo", ""),
            company_website="",
            title=title,
            category="",
            description=description,
            employment_type=employment_type,
            work_type=work_type,
            location=location,
            city=city,
            state=state,
            country=country,
            remote=remote,
            salary=salary_text,
            currency=currency,
            min_salary=int(min_sal) if min_sal else None,
            max_salary=int(max_sal) if max_sal else None,
            experience=experience_text,
            experience_years=experience_years,
            skills=skills,
            publication_date=item.get("job_posted_at_datetime_utc", ""),
            apply_url=apply_url,
            company_url="",
            active=True,
        )

def search_jsearch_jobs(role: str = "") -> List[JobData]:
    provider = JSearchProvider()
    return provider.search_jobs(role)
