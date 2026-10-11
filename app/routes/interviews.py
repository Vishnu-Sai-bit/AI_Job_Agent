"""
==========================================================
AI Job Copilot - Interview Center Routes
==========================================================
"""

from flask import Blueprint, render_template, request, flash
from app.routes.main import get_candidate_context
from services.interview.interview_generator import generate_interview_questions
from services.interview.mock_evaluator import evaluate_mock_answer

interviews_bp = Blueprint("interviews", __name__, url_prefix="/interviews")

@interviews_bp.route("/", methods=["GET", "POST"])
def index():
    candidate = get_candidate_context()
    role = request.args.get("role", candidate.get("preferred_role", "Data Analyst"))
    company = request.args.get("company", "Target MNC")
    questions = []
    evaluation = None

    if request.method == "POST":
        action = request.form.get("action")
        if action == "generate":
            role = request.form.get("role", "Data Analyst")
            company = request.form.get("company", "Google")
            q_res = generate_interview_questions(
                role=role,
                skills=candidate.get("skills", ["Python", "SQL", "Tableau"]),
                company=company,
                question_count=4
            )
            questions = q_res.get("questions", []) if isinstance(q_res, dict) else q_res
            flash(f"Generated 4 technical & behavioral questions for '{role}' at {company}!", "success")
        elif action == "evaluate":
            q_text = request.form.get("question_text", "")
            ans_text = request.form.get("answer_text", "")
            target_role = request.form.get("eval_role", "Data Analyst")
            if q_text and ans_text:
                evaluation = evaluate_mock_answer(
                    question=q_text,
                    candidate_answer=ans_text,
                    role=target_role,
                    resume_context=", ".join(candidate.get("skills", []))
                )
                flash("AI Interview Evaluation complete!", "success")

    if not questions:
        q_res = generate_interview_questions(
            role=role,
            skills=candidate.get("skills", ["Python", "SQL", "Tableau"]),
            company=company,
            question_count=4
        )
        questions = q_res.get("questions", []) if isinstance(q_res, dict) else q_res

    return render_template(
        "interviews/index.html",
        candidate=candidate,
        role=role,
        company=company,
        questions=questions,
        evaluation=evaluation,
        active_tab="interviews"
    )
