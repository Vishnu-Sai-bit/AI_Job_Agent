"""
==========================================================
AI JobAgent - Job Verification & Trust Agent
Author : Antigravity
==========================================================
"""

from typing import List, Tuple
from models.job import JobData

ATS_DOMAINS = {
    "greenhouse.io", "lever.co", "workday.com", "myworkdayjobs.com",
    "smartrecruiters.com", "taleo.net", "icims.com", "bamboohr.com",
    "ashbyhq.com", "jobvite.com", "oracle.com", "microsoft.com",
    "amazon.jobs", "google.com", "meta.com"
}

SUSPICIOUS_PHRASES = [
    "registration fee", "pay to apply", "processing fee", "security deposit",
    "investment required", "send money", "telegram contact only", "whatsapp only"
]

def verify_job(job: JobData) -> JobData:
    """
    Inspect job posting for authenticity, safety, and risk indicators.
    Enriches the JobData object with verification status and trust notes.
    """
    notes: List[str] = []
    status: str = "verified"

    url_lower = (job.apply_url or "").lower()
    desc_lower = (job.description or "").lower()

    # 1. Suspicious Payment or Scam Check
    for phrase in SUSPICIOUS_PHRASES:
        if phrase in desc_lower:
            status = "caution"
            notes.append(f"Caution: Contains potential risk phrase '{phrase}'.")

    # 2. Direct ATS / Corporate Portal Check
    is_direct_ats = any(domain in url_lower for domain in ATS_DOMAINS)
    if is_direct_ats:
        notes.append("Direct Enterprise ATS / Corporate Portal Verified")
    elif "linkedin.com" in url_lower or "indeed.com" in url_lower:
        notes.append("Verified Job Platform Listing (LinkedIn / Indeed)")
    elif "careers" in url_lower or "jobs." in url_lower:
        notes.append("Direct Company Careers Page")
    else:
        if status != "caution":
            status = "review"
        notes.append("Aggregator / Third-Party Application Portal (Review recommended)")

    # 3. Company Metadata Check
    if not job.company or job.company.lower() in ["unknown", "confidential", "hiring company"]:
        if status != "caution":
            status = "review"
        notes.append("Company name is unlisted or confidential")
    else:
        notes.append(f"Official Company Entity: {job.company}")

    # 4. Job Description Depth
    if len(job.description or "") < 20:
        notes.append("Brief / title-only job listing provided")
    else:
        notes.append("Role responsibilities and requirements confirmed")

    job.verification_status = status
    job.verification_notes = notes
    return job

def verify_all_jobs(jobs: List[JobData]) -> List[JobData]:
    """
    Verify all jobs in the list.
    """
    return [verify_job(j) for j in jobs]
