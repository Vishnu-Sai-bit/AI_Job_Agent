"""
==========================================================
AI Job Copilot - Job Match Analysis Route Blueprint
==========================================================
"""

from flask import Blueprint, render_template, request, redirect, url_for
from app.routes.main import get_candidate_context
from app.routes.jobs import load_verified_jobs

job_matching_bp = Blueprint("job_matching", __name__, url_prefix="/job-matching")

@job_matching_bp.route("/")
@job_matching_bp.route("/<job_id>")
def detail(job_id=None):
    jobs = load_verified_jobs()
    if not job_id and jobs:
        job = jobs[0]
    else:
        job = next((j for j in jobs if str(j.get("id")) == str(job_id)), None)
    if not job and jobs:
        job = jobs[0]

    candidate = get_candidate_context()
    from services.ats_scorer import calculate_job_compatibility_score
    compat = calculate_job_compatibility_score(candidate, job or {})

    matching = compat.get("matching_skills", [])
    missing = compat.get("missing_skills", [])
    
    return render_template(
        "job_matching/detail.html",
        job=job,
        matching=matching,
        missing=missing,
        compat=compat,
        candidate=candidate,
        active_tab="job_matching"
    )
