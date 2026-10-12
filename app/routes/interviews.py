"""
==========================================================
AI Job Copilot - Unified Interview Center Routes
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
    company = request.args.get("company", "Microsoft")
    round_type = request.args.get("round_type", "Technical Deep Dive")
    difficulty = request.args.get("difficulty", "Mid-Level Specialist (Practical + STAR)")
    question_count = int(request.args.get("question_count", 5))
    interviewer_role = request.args.get("interviewer_role", "Senior Technical Hiring Manager")
    
    default_skills = candidate.get("skills", ["Python", "SQL", "Tableau", "Excel"])
    skills_list = default_skills
    skills_str = ", ".join(skills_list)
    
    questions = []
    evaluation = None
    action = None

    if request.method == "POST":
        action = request.form.get("action")
        if action == "generate":
            role = request.form.get("role", role)
            company = request.form.get("company", company)
            round_type = request.form.get("round_type", round_type)
            difficulty = request.form.get("difficulty", difficulty)
            question_count = int(request.form.get("question_count", question_count))
            interviewer_role = request.form.get("interviewer_role", interviewer_role)
            skills_input = request.form.get("skills", "")
            if skills_input:
                skills_list = [s.strip() for s in skills_input.split(",") if s.strip()]
                skills_str = ", ".join(skills_list)

            q_res = generate_interview_questions(
                role=role,
                skills=skills_list,
                company=company,
                round_type=round_type,
                difficulty=difficulty,
                question_count=question_count,
                interviewer_role=interviewer_role
            )
            questions = q_res.get("questions", []) if isinstance(q_res, dict) else q_res
            flash(f"Generated {len(questions)} calibrated interview questions for '{role}' at {company} ({round_type})!", "success")

        elif action == "evaluate":
            q_text = request.form.get("question_text", "")
            ans_text = request.form.get("answer_text", "")
            target_role = request.form.get("eval_role", role)
            role = target_role
            company = request.form.get("eval_company", company)
            round_type = request.form.get("eval_round_type", round_type)
            difficulty = request.form.get("eval_difficulty", difficulty)
            interviewer_role = request.form.get("eval_interviewer_role", interviewer_role)
            
            if q_text and ans_text:
                evaluation = evaluate_mock_answer(
                    question=q_text,
                    candidate_answer=ans_text,
                    role=target_role,
                    resume_context=skills_str
                )
                flash("AI Interview Evaluation complete with rubric score!", "success")

    if not questions and action != "evaluate":
        q_res = generate_interview_questions(
            role=role,
            skills=skills_list,
            company=company,
            round_type=round_type,
            difficulty=difficulty,
            question_count=question_count,
            interviewer_role=interviewer_role
        )
        questions = q_res.get("questions", []) if isinstance(q_res, dict) else q_res
    elif not questions and action == "evaluate":
        eval_q = request.form.get("question_text", "Explain the difference between ROW_NUMBER and DENSE_RANK in SQL.")
        questions = [
            {
                "type": "Technical / Practice",
                "question": eval_q,
                "answer_tips": "Focus on clear STAR structure, technical keywords, and measurable outcomes.",
                "sample_answer": evaluation.get("refined_model_answer", "") if evaluation else ""
            }
        ]

    return render_template(
        "interviews/index.html",
        candidate=candidate,
        role=role,
        company=company,
        round_type=round_type,
        difficulty=difficulty,
        question_count=question_count,
        interviewer_role=interviewer_role,
        skills=skills_str,
        questions=questions,
        evaluation=evaluation,
        active_tab="interviews"
    )
