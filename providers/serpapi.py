"""
==========================================================
AI JobAgent - SerpApi Google Jobs Provider
==========================================================
"""

from typing import List

from providers.base import BaseProvider
from models import JobData
from config import SERPAPI_API_KEY

from services.location_parser import (
    parse_location,
    is_remote,
)

class SerpApiProvider(BaseProvider):
    def __init__(self):
        super().__init__("SerpApi", "https://serpapi.com/search.json")

    def search_jobs(self, role: str = "") -> List[JobData]:
        if not SERPAPI_API_KEY:
            return []

        keywords = role.lower().split() if role else []
        jobs = []
        
        # Fetch up to 2 pages (approx 20 jobs)
        for page in range(2):
            params = {
                "engine": "google_jobs",
                "q": role if role else "Data Analyst",
                "location": "India",
                "api_key": SERPAPI_API_KEY,
                "hl": "en",
                "start": str(page * 10)
            }

            try:
                raw_data = self.fetch_raw_data(params=params)
                results = raw_data.get("jobs_results", [])
                if not results:
                    break
                for item in results:
                    job = self.build_job(item, keywords)
                    if job:
                        jobs.append(job)
            except Exception:
                break
                
        return jobs

    def build_job(self, item: dict, keywords: List[str]) -> JobData | None:
        title = (item.get("title") or "").strip()
        company = (item.get("company_name") or "").strip()
        
        # Parse apply url
        apply_url = ""
        apply_options = item.get("apply_options", [])
        if isinstance(apply_options, list) and len(apply_options) > 0:
            apply_url = apply_options[0].get("link", "")

        if not title or not company or not apply_url:
            return None

        description = item.get("description") or ""
        
        loc_name = item.get("location") or "India"
        location_data = parse_location(loc_name)
        
        # Extensions for type and remote status
        extensions = item.get("detected_extensions", {})
        remote = extensions.get("work_from_home", False)
        work_type = "Remote" if remote or is_remote(loc_name) else "Onsite"
        employment_type = extensions.get("schedule_type", "Full-time")

        search_text = (title + " " + description).lower()
        if keywords and not any(keyword in search_text for keyword in keywords):
            return None

        return JobData(
            provider=self.name,
            provider_id=str(item.get("job_id", "")),
            company=company,
            company_logo=item.get("thumbnail", ""),
            company_website="",
            title=title,
            category="",
            description=description,
            employment_type=employment_type,
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
            skills=[],
            publication_date="",
            apply_url=apply_url,
            company_url="",
            active=True,
        )

def search_serpapi_jobs(role: str = "") -> List[JobData]:
    provider = SerpApiProvider()
    return provider.search_jobs(role)
