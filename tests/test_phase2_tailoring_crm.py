"""
==========================================================
AI JobAgent - Phase 2 Tailoring & CRM Tests
==========================================================
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from services.resume.resume_tailorer import tailor_resume_for_job
from services.crm.application_crm import (
    get_all_applications,
    add_or_update_application,
    delete_application,
    generate_followup_message
)

def test_resume_tailoring():
    print("--- 1. Testing Resume Tailoring Agent ---")
    resume_context = {
        "skills": ["Python", "SQL", "Tableau", "Power BI", "Excel"],
        "career_summary": "Data Analyst with 2 years experience building dashboards.",
        "projects": [
            {
                "title": "EV Charging Station Analysis",
                "description": "Analyzed 30,000 records, computed 8 KPIs, built Tableau dashboards."
            }
        ],
        "experience": [],
        "certifications": ["Oracle Analytics Cloud Professional"]
    }

    tailored = tailor_resume_for_job(
        resume_context=resume_context,
        job_title="Senior BI & Data Analyst",
        job_company="GlobalCorp",
        job_description="Seeking a BI specialist skilled in SQL, Tableau, and KPI reporting.",
        required_skills=["SQL", "Tableau", "KPI Reporting"]
    )

    assert "tailored_summary" in tailored, "Expected tailored_summary"
    assert "core_matching_skills" in tailored, "Expected core_matching_skills"
    assert len(tailored["core_matching_skills"]) > 0
    assert "tailored_projects" in tailored, "Expected tailored_projects"
    print(f"Tailored Summary: {tailored['tailored_summary'][:100]}...")
    print(f"Core Matching Skills: {tailored['core_matching_skills']}")
    print("Result: Resume Tailoring Agent Passed [PASSED]")

def test_application_crm_pipeline():
    print("\n--- 2. Testing Application Pipeline CRM & Follow-Up ---")
    
    # 1. Add application in 'saved' state
    app = add_or_update_application({
        "company": "TestMNC",
        "role": "Data Analyst",
        "location": "Hyderabad, India",
        "salary": "12-15 LPA",
        "apply_url": "https://careers.testmnc.com/123",
        "status": "saved"
    })
    app_id = app["id"]
    assert app["status"] == "saved"

    # 2. Mark as 'applied' with past date to test follow-up due calculation
    past_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
    app_updated = add_or_update_application({
        "id": app_id,
        "company": "TestMNC",
        "role": "Data Analyst",
        "status": "applied",
        "date_applied": past_date
    })
    assert app_updated["status"] == "applied"
    assert app_updated["followup_date"] != ""

    # 3. Verify get_all_applications flags follow-up due
    all_apps = get_all_applications()
    test_app = next(a for a in all_apps if a["id"] == app_id)
    assert test_app["is_followup_due"] is True, "Expected follow-up to be due for past application"

    # 4. Generate follow-up message
    followup = generate_followup_message(app_id, "Beere Vishnu Sai")
    assert "TestMNC" in followup["body"]
    assert "Data Analyst" in followup["body"]
    print(f"Follow-up Subject: {followup['subject']}")

    # 5. Clean up test record
    delete_application(app_id)
    print("Result: Application Pipeline CRM & Follow-Up Passed [PASSED]")

if __name__ == "__main__":
    test_resume_tailoring()
    test_application_crm_pipeline()
    print("\nALL PHASE 2 TAILORING & CRM TESTS PASSED!")
