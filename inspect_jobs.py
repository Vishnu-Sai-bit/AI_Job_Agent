import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from models import ResumeData
from services.search_jobs import fetch_jobs, clean_jobs
from services.job_matcher import match_jobs

resume = ResumeData(
    name="Beere Vishnu Sai",
    preferred_role="Data Analyst",
    preferred_location="Hyderabad",
    experience_years=2,
    skills=["Python", "SQL", "Power BI", "Excel", "Tableau"]
)

jobs, failed = fetch_jobs(resume.preferred_role)
jobs = clean_jobs(jobs)
matched = match_jobs(resume, jobs)

print("\n--- Top 15 Matched Jobs Before Location Filtering ---")
for j in sorted(matched, key=lambda x: x.match_score, reverse=True)[:15]:
    print(f"Title: {j.title} | Company: {j.company} | Location: {j.location} | Match Score: {j.match_score}%")
