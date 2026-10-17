"""
==========================================================
AI JobAgent - Workday Provider
Retrieves authentic vacancies published on company Workday career sites.
==========================================================
"""

import json
from pathlib import Path
from typing import List
import requests
from models import JobData
from config import BASE_DIR
from utils import info, warning


WORKDAY_CXS_TENANTS = [
    {
        "name": "Target",
        "api_url": "https://target.wd5.myworkdayjobs.com/wday/cxs/target/targetcareers/jobs",
        "base_url": "https://target.wd5.myworkdayjobs.com/en-US/targetcareers"
    },
    {
        "name": "Salesforce",
        "api_url": "https://salesforce.wd12.myworkdayjobs.com/wday/cxs/salesforce/External_Career_Site/jobs",
        "base_url": "https://salesforce.wd12.myworkdayjobs.com/en-US/External_Career_Site"
    },
    {
        "name": "Adobe",
        "api_url": "https://adobe.wd5.myworkdayjobs.com/wday/cxs/adobe/external_experienced/jobs",
        "base_url": "https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced"
    },
    {
        "name": "Autodesk",
        "api_url": "https://autodesk.wd1.myworkdayjobs.com/wday/cxs/autodesk/Ext/jobs",
        "base_url": "https://autodesk.wd1.myworkdayjobs.com/en-US/Ext"
    },
    {
        "name": "Mastercard",
        "api_url": "https://mastercard.wd1.myworkdayjobs.com/wday/cxs/mastercard/CorporateCareers/jobs",
        "base_url": "https://mastercard.wd1.myworkdayjobs.com/en-US/CorporateCareers"
    }
]


class WorkdayProvider:
    def __init__(self):
        self.name = "Workday"

    def search_jobs(self, role: str = "") -> List[JobData]:
        jobs: List[JobData] = []
        search_query = role or "Data Analyst"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "appliedFacets": {},
            "limit": 5,
            "offset": 0,
            "searchText": search_query
        }

        # 1. Fetch live vacancies from public Workday CXS endpoints
        for tenant in WORKDAY_CXS_TENANTS:
            comp_name = tenant["name"]
            api_url = tenant["api_url"]
            base_url = tenant["base_url"]
            try:
                resp = requests.post(api_url, json=payload, headers=headers, timeout=6)
                if resp.status_code == 200:
                    data = resp.json()
                    for p in data.get("jobPostings", []):
                        title = p.get("title") or ""
                        external_path = p.get("externalPath") or ""
                        bullet_fields = p.get("bulletFields", [])
                        req_id = bullet_fields[0] if bullet_fields else (external_path.split("_")[-1] if "_" in external_path else f"WD-{abs(hash(title)) % 100000}")
                        direct_url = f"{base_url}{external_path}" if external_path else base_url
                        loc = p.get("locationsText") or "Hybrid / Remote"

                        clean_skills = [s.strip() for s in title.replace("/", " ").replace("-", " ").split() if len(s) > 2][:5]
                        if "Analyst" in title or "Data" in title:
                            clean_skills = ["SQL", "Python", "Data Analysis", "Tableau", "Excel"]

                        job_obj = JobData(
                            provider="Workday",
                            provider_id=str(req_id),
                            company=comp_name,
                            title=title,
                            description=f"Authentic opening for {title} published on {comp_name} official Workday career portal. Requisition ID: {req_id}.",
                            location=loc,
                            apply_url=direct_url,
                            company_url=base_url,
                            skills=clean_skills,
                            experience="1-4 yrs",
                            active=True
                        )
                        jobs.append(job_obj)
                        if len(jobs) >= 20:
                            break
            except Exception as e:
                warning(f"Workday live fetch notice for {comp_name}: {e}")

            if len(jobs) >= 20:
                break

        # 2. Merge verified catalog Workday jobs
        export_file = BASE_DIR / "data" / "jobs_export.json"
        if export_file.exists():
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

                    # Avoid duplicate titles if already fetched live
                    if any(existing.title.lower() == title.lower() and existing.company.lower() == company.lower() for existing in jobs):
                        continue

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
                warning(f"WorkdayProvider catalog notice: {e}")

        return jobs


def search_workday_jobs(role: str = "") -> List[JobData]:
    provider = WorkdayProvider()
    return provider.search_jobs(role)
