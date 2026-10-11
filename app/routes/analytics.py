"""
==========================================================
AI Job Copilot - Career Analytics Route
==========================================================
"""

from flask import Blueprint, render_template
from app.routes.main import get_candidate_context
from app.routes.jobs import load_verified_jobs
from services.crm.application_crm import get_all_applications

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")

@analytics_bp.route("/")
def index():
    candidate = get_candidate_context()
    jobs = load_verified_jobs()
    applications = get_all_applications()

    stages = ["saved", "applied", "interview", "offer", "rejected"]
    stage_counts = {s: sum(1 for a in applications if a.get("stage") == s) for s in stages}

    # Match score distribution
    high_match = sum(1 for j in jobs if j.get("match_score", 70) >= 80)
    med_match = sum(1 for j in jobs if 60 <= j.get("match_score", 70) < 80)
    low_match = sum(1 for j in jobs if j.get("match_score", 70) < 60)

    ats_breakdown = candidate.get("ats_breakdown", {
        "contact_score": 10.0,
        "skills_score": 30.0,
        "experience_score": 5.0,
        "education_score": 15.0,
        "projects_score": 11.0,
        "certifications_score": 8.0
    })

    return render_template(
        "analytics/index.html",
        candidate=candidate,
        stage_counts=stage_counts,
        total_jobs=len(jobs),
        high_match=high_match,
        med_match=med_match,
        low_match=low_match,
        ats_breakdown=ats_breakdown,
        active_tab="analytics"
    )
