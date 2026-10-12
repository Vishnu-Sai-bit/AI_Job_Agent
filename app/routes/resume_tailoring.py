"""
==========================================================
AI Job Copilot - Resume Tailoring Route Blueprint
==========================================================
"""

from flask import Blueprint, render_template, request, flash
from app.routes.main import get_candidate_context
from services.resume.resume_tailorer import tailor_resume_for_job

resume_tailoring_bp = Blueprint("resume_tailoring", __name__, url_prefix="/resume-tailoring")

@resume_tailoring_bp.route("/", methods=["GET", "POST"])
def index():
    candidate = get_candidate_context()
    tailored_result = None

    if request.method == "POST":
        job_title = request.form.get("job_title", "").strip()
        job_desc = request.form.get("job_desc", "").strip()

        if job_title and job_desc:
            try:
                tailored_result = tailor_resume_for_job(
                    original_resume_text=candidate.get("career_summary", ""),
                    target_role=job_title,
                    target_company="Target Enterprise",
                    job_description=job_desc,
                    candidate_skills=candidate.get("skills", [])
                )
                flash(f"Resume successfully tailored for '{job_title}'!", "success")
            except Exception as e:
                flash(f"Tailoring error: {e}", "danger")

    return render_template(
        "resumes/tailoring.html",
        candidate=candidate,
        tailored_result=tailored_result,
        active_tab="resume_tailoring"
    )
