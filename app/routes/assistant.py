"""
==========================================================
AI Job Copilot - AI Career Assistant Route
==========================================================
"""

from flask import Blueprint, render_template, request, jsonify
from app.routes.main import get_candidate_context
from app.routes.jobs import load_verified_jobs
from services.crm.application_crm import get_all_applications
from services.analytics.copilot_assistant import copilot_assistant

assistant_bp = Blueprint("assistant", __name__, url_prefix="/assistant")

@assistant_bp.route("/", methods=["GET", "POST"])
def index():
    candidate = get_candidate_context()
    jobs = load_verified_jobs()
    applications = get_all_applications()

    user_query = ""
    ai_response = None
    suggested_actions = ["🎯 Focus Jobs Today", "📊 Check ATS Score", "🎤 Practice Interview", "📈 View Roadmaps"]

    if request.method == "POST":
        user_query = request.form.get("query", "").strip()
        if user_query:
            result = copilot_assistant.answer_query(
                query=user_query,
                resume_context=candidate,
                jobs=jobs,
                applications=applications
            )
            ai_response = result.get("response")
            suggested_actions = result.get("suggested_actions", suggested_actions)

    return render_template(
        "assistant/index.html",
        candidate=candidate,
        user_query=user_query,
        ai_response=ai_response,
        suggested_actions=suggested_actions,
        active_tab="assistant"
    )

@assistant_bp.route("/api/query", methods=["POST"])
@assistant_bp.route("/chat", methods=["POST"])
def api_query():
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or data.get("message") or "").strip()
    candidate = get_candidate_context()
    jobs = load_verified_jobs()
    applications = get_all_applications()

    result = copilot_assistant.answer_query(
        query=query,
        resume_context=candidate,
        jobs=jobs,
        applications=applications
    )
    return jsonify(result)
