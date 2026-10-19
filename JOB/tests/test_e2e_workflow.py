import io
import pytest
from app import create_app
from extensions import db
from models.user import User, CandidateProfile
from models.job import Job
from models.job_source import JobSource
from models.job_match import JobMatch
from services.career_assistant import CareerAssistant
from services.cover_letter_service import CoverLetterService

@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        # Find or create test source
        source = JobSource.query.filter_by(platform="greenhouse", company_key="stripe").first()
        if not source:
            source = JobSource(
                platform="greenhouse",
                company_key="stripe",
                name="Stripe (Greenhouse)"
            )
            db.session.add(source)
            db.session.commit()

        job1 = Job(
            source_id=source.id,
            source_platform="greenhouse",
            source_company_key="stripe",
            source_job_id="test-e2e-101",
            title="Senior Python Backend Engineer",
            company="Stripe",
            location="Remote",
            work_mode="remote",
            employment_type="full-time",
            experience_level="senior",
            required_skills=["Python", "Flask", "PostgreSQL"],
            preferred_skills=["Docker", "AWS"],
            description="We are seeking a Senior Python Engineer skilled in Python, Flask, and PostgreSQL.",
            original_url="https://boards.greenhouse.io/stripe/jobs/101",
            apply_url="https://boards.greenhouse.io/stripe/jobs/101#app",
            status="active"
        )
        job2 = Job(
            source_id=source.id,
            source_platform="greenhouse",
            source_company_key="stripe",
            source_job_id="test-e2e-102",
            title="Frontend React Engineer",
            company="Stripe",
            location="San Francisco, CA",
            work_mode="on-site",
            employment_type="full-time",
            experience_level="mid",
            required_skills=["React", "TypeScript", "CSS"],
            preferred_skills=["GraphQL"],
            description="Seeking Frontend Engineer proficient in React, TypeScript, and CSS.",
            original_url="https://boards.greenhouse.io/stripe/jobs/102",
            apply_url="https://boards.greenhouse.io/stripe/jobs/102#app",
            status="active"
        )
        db.session.add_all([job1, job2])
        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_complete_candidate_lifecycle(client, app):
    # 1. Register candidate account
    reg_res = client.post("/register", data={
        "full_name": "Dev Candidate",
        "email": "dev.candidate@example.com",
        "password": "securepassword123",
        "confirm_password": "securepassword123"
    }, follow_redirects=True)
    assert reg_res.status_code == 200
    assert b"Welcome to AI Job Agent" in reg_res.data or b"Upload Your Resume" in reg_res.data

    with app.app_context():
        user = User.query.filter_by(email="dev.candidate@example.com").first()
        assert user is not None
        assert user.candidate_profile is not None

    # 2. Upload sample PDF resume
    # Valid minimal PDF structure
    pdf_content = (
        b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"5 0 obj\n<< /Length 200 >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n"
        b"(Dev Candidate dev.candidate@example.com (555) 000-1111 San Francisco CA) Tj\n"
        b"ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n500\n%%EOF"
    )

    upload_data = {
        "resume_file": (io.BytesIO(pdf_content), "my_resume.pdf")
    }
    up_res = client.post("/resume/upload", data=upload_data, content_type="multipart/form-data", follow_redirects=True)
    assert up_res.status_code == 200

    with app.app_context():
        user = User.query.filter_by(email="dev.candidate@example.com").first()
        resume = user.get_active_resume()
        assert resume is not None
        assert resume.filename == "my_resume.pdf"
        assert resume.ats_quality_score > 0

    # 3. Update candidate skills and preferences
    prof_res = client.post("/resume/update-profile", data={
        "full_name": "Dev Candidate",
        "headline": "Senior Python & Backend Engineer",
        "location": "San Francisco, CA",
        "summary": "Experienced Python developer building distributed backend systems.",
        "skills": "Python, Flask, PostgreSQL, Docker, AWS, React",
        "experience_years": "5"
    }, follow_redirects=True)
    assert prof_res.status_code == 200

    # 4. Verify Job Match Calculation
    with app.app_context():
        user = User.query.filter_by(email="dev.candidate@example.com").first()
        job1 = Job.query.filter_by(source_job_id="test-e2e-101").first()
        match1 = JobMatch.query.filter_by(user_id=user.id, job_id=job1.id).first()
        assert match1 is not None
        assert match1.match_score >= 80.0
        assert "Python" in match1.skill_match_details["matched_required"]
        assert "Flask" in match1.skill_match_details["matched_required"]

    # 5. Search Jobs via Web UI
    search_res = client.get("/jobs?q=Python&min_match=75")
    assert search_res.status_code == 200
    assert b"Senior Python Backend Engineer" in search_res.data

    # 6. Bookmark / Save Job via AJAX API
    with app.app_context():
        job1 = Job.query.filter_by(source_job_id="test-e2e-101").first()
        job1_id = job1.id

    save_res = client.post(f"/api/jobs/save/{job1_id}")
    assert save_res.status_code == 200
    assert save_res.get_json()["saved"] is True

    # 7. Check Saved Jobs page
    saved_page = client.get("/saved-jobs")
    assert saved_page.status_code == 200
    assert b"Senior Python Backend Engineer" in saved_page.data

    # 8. Test Grounded Apply Now Redirection
    apply_res = client.get(f"/apply/{job1_id}", follow_redirects=False)
    assert apply_res.status_code == 302
    assert "boards.greenhouse.io/stripe/jobs/101" in apply_res.headers["Location"]

    # 9. Test Application Tracker
    # Create application as applied
    app_create = client.post("/applications/api/create", json={"job_id": job1_id, "status": "applied"})
    assert app_create.status_code == 200
    app_id = app_create.get_json()["application_id"]

    # Update application to interviewing
    app_update = client.post("/applications/api/update", json={
        "application_id": app_id,
        "status": "interviewing",
        "notes": "First round technical interview scheduled for Thursday."
    })
    assert app_update.status_code == 200
    assert app_update.get_json()["status"] == "interviewing"

    # View applications page
    apps_page = client.get("/applications")
    assert apps_page.status_code == 200
    assert b"Interviewing" in apps_page.data

    # 10. Test Conversational AI Career Assistant
    with app.app_context():
        user = User.query.filter_by(email="dev.candidate@example.com").first()
        assistant = CareerAssistant()

        # Command A: Search
        chat_search = assistant.process_message(user, "Find Python developer jobs matching my resume")
        assert chat_search["type"] == "job_list"
        assert len(chat_search["cards"]) > 0
        assert "Senior Python Backend Engineer" in chat_search["cards"][0]["title"]

        # Command B: Threshold filter
        chat_threshold = assistant.process_message(user, "Show jobs with an 80% or higher match")
        assert chat_threshold["type"] == "job_list"

        # Command C: Missing skills
        chat_gap = assistant.process_message(user, "Which skills am I missing for this position?", context_job_id=job1_id)
        assert "Skill Analysis" in chat_gap["reply"]
        assert "Python" in chat_gap["reply"]

        # Command D: Grounded Cover Letter
        chat_cover = assistant.process_message(user, "Prepare a cover letter for this job", context_job_id=job1_id)
        assert chat_cover["type"] == "cover_letter"
        assert "Dev Candidate" in chat_cover["reply"]
        assert "Stripe" in chat_cover["reply"]

        # Command E: Application Status
        chat_status = assistant.process_message(user, "Show my application status")
        assert "Interviewing" in chat_status["reply"]
