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
    candidate_skills = {s.lower().strip() for s in candidate.get("skills", [])}
    job_skills = job.get("skills") or [] if job else []
    
    matching = [s for s in job_skills if s and s.lower().strip() in candidate_skills]
    missing = [s for s in job_skills if s and s.lower().strip() not in candidate_skills]

    return render_template(
        "job_matching/detail.html",
        job=job,
        matching=matching,
        missing=missing,
        candidate=candidate,
        active_tab="job_matching"
    )
