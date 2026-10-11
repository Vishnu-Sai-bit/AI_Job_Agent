"""
==========================================================
AI Job Copilot - Main Routes (Landing & Dashboard)
==========================================================
"""

from flask import Blueprint, render_template, redirect, url_for
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

    from app.routes.jobs import load_verified_jobs
    all_jobs = load_verified_jobs()
    cand_skills = {s.lower().strip() for s in candidate.get("skills", [])}
    scored = []
    for j in all_jobs:
        j_skills = j.get("skills") or []
        m = [s for s in j_skills if s and s.lower().strip() in cand_skills]
        pct = int(round((len(m) / max(len(j_skills), 1)) * 100)) if j_skills else 75
        scored.append({
            "id": j.get("id"),
            "title": j.get("title"),
            "company": j.get("company"),
            "location": j.get("location"),
            "salary": j.get("salary", "Competitive"),
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
