"""
==========================================================
AI Job Copilot - Resume Analysis Route Blueprint
==========================================================
"""

from flask import Blueprint, render_template
from app.routes.main import get_candidate_context

resume_analysis_bp = Blueprint("resume_analysis", __name__, url_prefix="/resume-analysis")

@resume_analysis_bp.route("/")
def index():
    candidate = get_candidate_context()
    return render_template(
        "resumes/analysis.html",
        candidate=candidate,
        active_tab="resume_analysis"
    )
