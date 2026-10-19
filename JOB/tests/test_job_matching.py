import pytest
from models.job import Job
from models.resume import Resume
from models.user import CandidateProfile, User
from services.job_matcher import JobMatcher

def test_explainable_job_matching_formula():
    matcher = JobMatcher()

    # Create dummy candidate profile & resume
    user = User(id=1, email="candidate@example.com")
    profile = CandidateProfile(
        user_id=1,
        full_name="Alex Johnson",
        location="San Francisco, CA",
        experience_years=5.0,
        skills=["Python", "Flask", "React", "PostgreSQL", "Docker", "AWS"],
        preferred_titles=["Python Developer", "Full Stack Engineer"],
        preferred_countries=["United States"],
        preferred_cities=["San Francisco"],
        work_modes=["remote", "hybrid"],
        education=[{"degree": "Bachelor of Science", "institution": "UC Berkeley"}]
    )
    user.candidate_profile = profile

    resume = Resume(
        id=1,
        user_id=1,
        filename="resume.pdf",
        raw_text="Experienced Python, Flask, and React developer with PostgreSQL and Docker.",
        parsed_data={
            "skills": ["Python", "Flask", "React", "PostgreSQL", "Docker", "AWS"],
            "experience_years": 5.0,
            "education": [{"degree": "Bachelor of Science", "institution": "UC Berkeley"}],
            "projects": [{"title": "API Backend", "description": "Python Flask PostgreSQL"}]
        }
    )

    # Job requiring Python, Flask, Docker
    job = Job(
        id=101,
        source_id=1,
        source_platform="greenhouse",
        source_company_key="stripe",
        source_job_id="12345",
        title="Senior Python Backend Engineer",
        company="Stripe",
        location="San Francisco, CA",
        work_mode="hybrid",
        experience_level="senior",
        required_skills=["Python", "Flask", "Docker"],
        preferred_skills=["Kubernetes", "AWS"],
        description="We are seeking a Senior Python Engineer skilled in Python, Flask, and Docker to scale backend services.",
        original_url="https://boards.greenhouse.io/stripe/jobs/12345",
        apply_url="https://boards.greenhouse.io/stripe/jobs/12345#app",
        status="active"
    )

    match_result = matcher.compute_match(resume, profile, job)

    score = match_result["match_score"]
    breakdown = match_result["score_breakdown"]
    skills_detail = match_result["skill_match_details"]

    # Verify score is high
    assert score >= 75.0
    assert "Python" in skills_detail["matched_required"]
    assert "Flask" in skills_detail["matched_required"]
    assert "Docker" in skills_detail["matched_required"]

    # Verify formula breakdown structure (5 components, location removed)
    assert "skills" in breakdown
    assert "experience" in breakdown
    assert "keyword_coverage" in breakdown
    assert "projects" in breakdown
    assert "qualifications" in breakdown
    assert "location_work_mode" not in breakdown

    # Verify exact deterministic calculation: M = 0.40S + 0.25E + 0.15K + 0.10P + 0.10Q
    expected_score = round(
        0.40 * breakdown["skills"] +
        0.25 * breakdown["experience"] +
        0.15 * breakdown["keyword_coverage"] +
        0.10 * breakdown["projects"] +
        0.10 * breakdown["qualifications"],
        2
    )
    assert abs(score - expected_score) < 0.05

    # Verify explainable narrative
    explanation = match_result["match_explanation"]
    assert "compatibility" in explanation.lower() or "match" in explanation.lower()
