"""
==========================================================
AI Job Copilot - Career Intelligence & Learning Routes
==========================================================
"""

from flask import Blueprint, render_template, request
from app.routes.main import get_candidate_context
from app.routes.jobs import load_verified_jobs
from services.learning.learning_engine import generate_learning_roadmap
from services.analytics.market_skill_aggregator import aggregate_market_skill_gaps

career_bp = Blueprint("career", __name__)

@career_bp.route("/career", strict_slashes=False)
@career_bp.route("/career/", strict_slashes=False)
@career_bp.route("/roadmaps", strict_slashes=False)
@career_bp.route("/roadmaps/", strict_slashes=False)
@career_bp.route("/career-intelligence", strict_slashes=False)
@career_bp.route("/career-intelligence/", strict_slashes=False)
def career_intelligence():
    candidate = get_candidate_context()
    target_role = candidate.get("preferred_role", "Data Analyst")
    jobs = load_verified_jobs()
    market_data = aggregate_market_skill_gaps(
        candidate_skills=candidate.get("skills", []),
        jobs=jobs
    )
    return render_template(
        "career_intelligence/index.html",
        candidate=candidate,
        market_data=market_data,
        target_role=target_role,
        active_tab="career_intelligence"
    )

@career_bp.route("/learning", methods=["GET", "POST"], strict_slashes=False)
@career_bp.route("/learning/", methods=["GET", "POST"], strict_slashes=False)
def learning():
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
