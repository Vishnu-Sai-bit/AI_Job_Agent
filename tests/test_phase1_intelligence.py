import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from models.job import JobData
from models.resume import ResumeData
from services.job.job_deduplicator import deduplicate_jobs
from services.job.job_verifier import verify_job, verify_all_jobs
from services.matcher.job_matcher import match_jobs

def test_job_deduplication():
    print("--- 1. Testing Job Deduplication Engine ---")
    j1 = JobData(
        provider="adzuna",
        company="GlobalCorp Technologies Inc.",
        title="Junior Data Analyst",
        location="Bengaluru, India",
        apply_url="https://adzuna.in/job/123",
        skills=["Python", "SQL"]
    )
    j2 = JobData(
        provider="serpapi",
        company="GlobalCorp",
        title="Data Analyst",
        location="Bengaluru, India",
        apply_url="https://careers.globalcorp.com/jobs/data-analyst",
        skills=["SQL", "Power BI", "Tableau"]
    )
    j3 = JobData(
        provider="remoteok",
        company="CodeTech LLC",
        title="Python Developer",
        location="Remote, India",
        apply_url="https://remoteok.com/job/456",
        skills=["Python", "FastAPI"]
    )

    raw_jobs = [j1, j2, j3]
    deduped = deduplicate_jobs(raw_jobs)
    
    # j1 and j2 should be clustered into 1 job
    assert len(deduped) == 2, f"Expected 2 unique jobs, got {len(deduped)}"
    
    globalcorp_job = next(j for j in deduped if "globalcorp" in j.company.lower())
    assert len(globalcorp_job.sources) == 2, f"Expected 2 sources, got {globalcorp_job.sources}"
    assert "https://careers.globalcorp.com" in globalcorp_job.apply_url, "Expected direct careers URL to be prioritized"
    print("Result: Multi-source Job Deduplication Passed [PASSED]")

def test_job_verification():
    print("\n--- 2. Testing Job Verification Agent ---")
    j_verified = JobData(
        company="Microsoft",
        title="Data Analyst",
        apply_url="https://careers.microsoft.com/job/123",
        description="Responsible for building data models and dashboards."
    )
    verify_job(j_verified)
    assert j_verified.verification_status == "verified"

    j_caution = JobData(
        company="FastJobs",
        title="Data Entry / Analyst",
        apply_url="https://example.com/apply",
        description="Immediate joining. Registration fee of Rs 500 required for verification."
    )
    verify_job(j_caution)
    assert j_caution.verification_status == "caution"
    print("Result: Job Verification & Risk Screening Passed [PASSED]")

def test_explainable_fit_breakdown():
    print("\n--- 3. Testing Explainable Fit Breakdown & Resume Evidence ---")
    resume = ResumeData(
        preferred_role="Data Analyst",
        preferred_location="Hyderabad",
        experience_years=1.0,
        skills=["Python", "SQL", "Tableau", "Power BI", "Excel"],
        projects=[
            {
                "title": "EV Charging Analysis",
                "description": "Designed EDA pipeline on 30,000+ records and built Tableau dashboards tracking 8+ KPIs."
            }
        ]
    )

    job = JobData(
        company="Scout Analytics",
        title="Data Analyst",
        location="Hyderabad, India",
        skills=["SQL", "Tableau", "Python"],
        apply_url="https://greenhouse.io/scout/da"
    )

    matched = match_jobs(resume, [job])
    assert len(matched) > 0
    top_job = matched[0]
    
    assert "skills" in top_job.fit_breakdown
    assert "role" in top_job.fit_breakdown
    assert "experience" in top_job.fit_breakdown
    assert "location" in top_job.fit_breakdown
    assert len(top_job.resume_evidence) > 0
    print(f"Fit Breakdown: {top_job.fit_breakdown}")
    print(f"Resume Evidence: {top_job.resume_evidence}")
    print("Result: Explainable Fit Breakdown & Evidence Passed [PASSED]")

if __name__ == "__main__":
    test_job_deduplication()
    test_job_verification()
    test_explainable_fit_breakdown()
    print("\nALL PHASE 1 INTELLIGENCE TESTS PASSED!")
