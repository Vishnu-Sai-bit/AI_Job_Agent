"""
==========================================================
AI JobAgent - Job Deduplication Agent
Author : Antigravity
==========================================================
"""

import re
from typing import List, Dict
from models.job import JobData
from utils import info

def normalize_company(company: str) -> str:
    if not company:
        return ""
    comp = company.lower()
    # Remove corporate suffixes and special characters
    comp = re.sub(r"\b(inc|incorporated|llc|ltd|pvt|private|technologies|tech|solutions|corporation|corp|services|group|co)\b", "", comp)
    comp = re.sub(r"[^\w\s]", "", comp)
    return " ".join(comp.split())

def normalize_title(title: str) -> str:
    if not title:
        return ""
    t = title.lower()
    # Remove level/tier prefixes and noise
    t = re.sub(r"\b(junior|senior|entry level|associate|lead|intern|fresher|ii|iii|iv|sr|jr)\b", "", t)
    t = re.sub(r"[\(\[\{].*?[\)\]\}]", "", t)
    t = re.sub(r"[^\w\s]", "", t)
    return " ".join(t.split())

def is_official_url(url: str) -> bool:
    if not url:
        return False
    u = url.lower()
    ats_keywords = [
        "greenhouse.io", "lever.co", "workday.com", "myworkdayjobs.com",
        "smartrecruiters.com", "taleo.net", "icims.com", "bamboohr.com",
        "ashbyhq.com", "jobvite.com", "careers.", "jobs."
    ]
    return any(kw in u for kw in ats_keywords)

def deduplicate_jobs(jobs: List[JobData]) -> List[JobData]:
    """
    Cluster and merge duplicate job postings across multiple job sources.
    Returns unique opportunities with consolidated multi-source tracking.
    """
    if not jobs:
        return []

    unique_clusters: Dict[str, JobData] = {}

    for job in jobs:
        comp_norm = normalize_company(job.company)
        title_norm = normalize_title(job.title)
        
        # Primary cluster key
        if comp_norm and title_norm:
            cluster_key = f"{comp_norm}::{title_norm}"
        else:
            cluster_key = f"{job.company.lower().strip()}::{job.title.lower().strip()}"

        # Ensure job has initial source
        source_name = job.provider.capitalize() if job.provider else "Web"
        if not job.sources:
            job.sources = [source_name]

        if cluster_key in unique_clusters:
            existing = unique_clusters[cluster_key]
            # Merge sources
            for s in job.sources:
                if s not in existing.sources:
                    existing.sources.append(s)
            
            # Prioritize official/direct apply URLs
            if not is_official_url(existing.apply_url) and (is_official_url(job.apply_url) or len(job.apply_url) > len(existing.apply_url)):
                existing.apply_url = job.apply_url

            # Merge skills
            for sk in job.skills:
                if sk.lower() not in {s.lower() for s in existing.skills}:
                    existing.skills.append(sk)

            # Keep the longer, richer description
            if len(job.description or "") > len(existing.description or ""):
                existing.description = job.description

            # Fill in missing metadata
            if not existing.salary or existing.salary == "Not Mentioned":
                if job.salary and job.salary != "Not Mentioned":
                    existing.salary = job.salary
                    existing.min_salary = job.min_salary
                    existing.max_salary = job.max_salary

            if not existing.location or existing.location == "India":
                if job.location and job.location != "India":
                    existing.location = job.location
                    existing.city = job.city
        else:
            unique_clusters[cluster_key] = job

    deduped = list(unique_clusters.values())
    info(f"Deduplication completed: {len(jobs)} raw jobs merged into {len(deduped)} unique opportunities.")
    return deduped
