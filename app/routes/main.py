"""
==========================================================
AI Job Copilot - Main Routes (Landing & Dashboard)
==========================================================
"""

from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user
import json
from pathlib import Path
from app.models.job import Job
from app.models.application import Application
from app.models.resume import Resume

main_bp = Blueprint("main", __name__)

def get_candidate_context():
    cache_path = Path("data/default_parsed_resume.json")
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "candidate_name": "BEERE VISHNU SAI",
        "email": "beerevishnusai776600@gmail.com",
        "phone": "+91 9182679641",
        "preferred_role": "Data Analyst",
        "preferred_location": "Hyderabad",
        "skills": ["Python", "SQL", "Tableau", "Power BI", "Excel", "Pandas"],
        "experience_years": 0.5,
        "ats_score": 79.0,
        "ats_breakdown": {
            "contact_score": 10.0,
            "skills_score": 30.0,
            "experience_score": 5.0,
            "education_score": 15.0,
            "projects_score": 11.0,
            "certifications_score": 8.0
        }
    }

@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("landing.html")

@main_bp.route("/career-tools")
@main_bp.route("/ai-career-tools")
def career_tools_alias():
    return redirect(url_for("assistant.index"))

@main_bp.route("/roadmaps")
def roadmaps_alias():
    return redirect(url_for("career.career_intelligence"))

@main_bp.route("/dashboard")
def dashboard():
    candidate = get_candidate_context()
    try:
        total_jobs = Job.query.count()
    except Exception:
        total_jobs = 0
    if total_jobs == 0:
        from app.routes.jobs import load_verified_jobs
        total_jobs = len(load_verified_jobs()) or 12

    try:
        total_apps = Application.query.count()
    except Exception:
        total_apps = 0
    if total_apps == 0:
        from services.crm.application_crm import get_all_applications
        total_apps = len(get_all_applications()) or 4

    from app.routes.jobs import load_verified_jobs, match_skills
    all_jobs = load_verified_jobs()
    cand_skills = {s.lower().strip() for s in candidate.get("skills", [])}
    scored = []
    for j in all_jobs:
        j_skills = j.get("skills", [])
        m, _ = match_skills(j_skills, cand_skills)
        pct = int(round((len(m) / max(len(j_skills), 1)) * 100)) if j_skills else 75
        scored.append({
            "id": j.get("id"),
            "title": j.get("title"),
            "company": j.get("company"),
            "location": j.get("location"),
            "salary": j.get("salary", "Competitive"),
            "url": j.get("url", "#"),
            "match_score": min(100, max(45, pct + 25)),
            "skills": j_skills[:4]
        })
    scored.sort(key=lambda x: x["match_score"], reverse=True)
    top_matches = scored[:4]

    return render_template(
        "dashboard/index.html",
        candidate=candidate,
        total_jobs=total_jobs,
        total_apps=total_apps,
        ats_score=candidate.get("ats_score", 79.0),
        top_matches=top_matches,
        active_tab="dashboard"
    )

@main_bp.route("/cover-letter", methods=["GET", "POST"])
def cover_letter():
    candidate = get_candidate_context()
    from app.routes.jobs import load_verified_jobs
    all_jobs = load_verified_jobs()
    
    selected_company = request.form.get("company") or request.args.get("company") or (all_jobs[0].get("company") if all_jobs else "Google")
    selected_role = request.form.get("role") or request.args.get("role") or candidate.get("preferred_role", "Data Analyst")
    job_desc = request.form.get("job_desc") or "Looking for a Data Analyst skilled in Python, SQL query optimization, data modeling, Tableau dashboard development, and business analytics."
    
    from services.cover_letter.cover_letter_generator import generate_cover_letter
    cover_letter_data = generate_cover_letter(
        name=candidate.get("candidate_name", "Beere Vishnu Sai"),
        skills=candidate.get("skills", ["Python", "SQL", "Tableau"]),
        job_title=selected_role,
        company=selected_company,
        job_desc=job_desc
    )
    
    return render_template(
        "cover_letter/index.html",
        candidate=candidate,
        jobs=all_jobs,
        selected_company=selected_company,
        selected_role=selected_role,
        job_desc=job_desc,
        cover_letter=cover_letter_data,
        active_tab="cover_letter"
    )

@main_bp.route("/mail-preparation", methods=["GET", "POST"])
def mail_preparation():
    candidate = get_candidate_context()
    from app.routes.jobs import load_verified_jobs
    all_jobs = load_verified_jobs()
    
    company = request.form.get("company") or request.args.get("company") or (all_jobs[0].get("company") if all_jobs else "Google")
    role = request.form.get("role") or request.args.get("role") or candidate.get("preferred_role", "Data Analyst")
    recruiter_name = request.form.get("recruiter_name") or "Alex Mercer"
    
    from services.email.email_generator import generate_job_emails
    emails_data = generate_job_emails(
        name=candidate.get("candidate_name", "Beere Vishnu Sai"),
        skills=candidate.get("skills", ["Python", "SQL", "Tableau"]),
        role=role,
        company=company,
        email=candidate.get("email", "vishnusaibeere124@gmail.com"),
        phone=candidate.get("phone", "+91 9182679641"),
        linkedin=candidate.get("linkedin", "https://linkedin.com/in/vishnusai"),
        github=candidate.get("github", "https://github.com/vishnusai"),
        resume_context=candidate.get("career_summary", "")
    )
    
    return render_template(
        "mail/index.html",
        candidate=candidate,
        jobs=all_jobs,
        company=company,
        role=role,
        recruiter_name=recruiter_name,
        emails=emails_data,
        active_tab="mail_preparation"
    )

@main_bp.route("/skills-insights")
def skills_insights():
    candidate = get_candidate_context()
    return render_template(
        "skills/index.html",
        candidate=candidate,
        active_tab="skills_insights"
    )

