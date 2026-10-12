"""
==========================================================
AI Job Copilot - Learning Hub Route Blueprint
==========================================================
"""

from flask import Blueprint, render_template, request
from app.routes.main import get_candidate_context
from services.learning.learning_engine import generate_learning_roadmap

learning_bp = Blueprint("learning", __name__, url_prefix="/learning-hub")

@learning_bp.route("/", methods=["GET", "POST"], strict_slashes=False)
@learning_bp.route("", methods=["GET", "POST"], strict_slashes=False)
def index():
    candidate = get_candidate_context()
    target_role = request.args.get("role", candidate.get("preferred_role", "Data Analyst"))

    if request.method == "POST":
        target_role = request.form.get("target_role", target_role)

    roadmap = generate_learning_roadmap(
        role=target_role,
        skills=candidate.get("skills", ["Python", "SQL", "Tableau", "Excel"])
    )

    return render_template(
        "learning/index.html",
        candidate=candidate,
        target_role=target_role,
        roadmap=roadmap,
        active_tab="learning"
    )
