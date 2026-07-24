"""
==========================================================
AI JobAgent - Jooble Provider
==========================================================
"""

import requests
from typing import List

from providers.base import BaseProvider
from models import JobData
from config import JOOBLE_API_KEY

from services.location_parser import (
    parse_location,
    is_remote,
)

class JoobleProvider(BaseProvider):
    def __init__(self):
        super().__init__("Jooble", "https://jooble.org/api")

    def search_jobs(self, role: str = "") -> List[JobData]:
        if not JOOBLE_API_KEY:
            return []

        url = f"{self.api_url}/{JOOBLE_API_KEY}"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "keywords": role if role else "Data Analyst",
            "location": "India"
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            raw_data = response.json()
        except Exception:
            return []

        keywords = role.lower().split() if role else []
        jobs = []
        for item in raw_data.get("jobs", []):
            job = self.build_job(item, keywords)
            if job:
                jobs.append(job)
        return jobs

    def build_job(self, item: dict, keywords: List[str]) -> JobData | None:
        title = (item.get("title") or "").strip()
        company = (item.get("company") or "").strip()
        apply_url = (item.get("link") or "").strip()

        if not title or not company or not apply_url:
            return None

        description = item.get("snippet") or ""
        skills = []

        search_text = (title + " " + description).lower()
        if keywords and not any(keyword in search_text for keyword in keywords):
            return None

        loc_name = item.get("location") or "India"
        location_data = parse_location(loc_name)
        work_type = "Remote" if is_remote(loc_name) else "Onsite"

        return JobData(
            provider=self.name,
            provider_id=str(item.get("id", "")),
            company=company,
            company_logo="",
            company_website="",
            title=title,
            category="",
            description=description,
            employment_type="Full Time",
            work_type=work_type,
            location=loc_name,
            city=location_data["city"],
            state=location_data["state"],
            country=location_data["country"],
            remote=work_type == "Remote",
            salary=item.get("salary", "Not Mentioned"),
            currency="",
            min_salary=None,
            max_salary=None,
            experience="Not Mentioned",
            experience_years=0.0,
            skills=skills,
            publication_date=item.get("updated", ""),
            apply_url=apply_url,
            company_url="",
            active=True,
        )

def search_jooble_jobs(role: str = "") -> List[JobData]:
    provider = JoobleProvider()
    return provider.search_jobs(role)
