"""
==========================================================
AI Job Copilot - AI Career Assistant Route
==========================================================
"""

import json
from flask import Blueprint, render_template, request, jsonify
from app.routes.main import get_candidate_context
from app.routes.jobs import load_verified_jobs
from services.crm.application_crm import get_all_applications
from services.analytics.copilot_assistant import copilot_assistant

assistant_bp = Blueprint("assistant", __name__, url_prefix="/assistant")

@assistant_bp.route("/", methods=["GET", "POST"])
@assistant_bp.route("", methods=["GET", "POST"])
@assistant_bp.route("/career-tools", methods=["GET", "POST"])
@assistant_bp.route("/ai-career-tools", methods=["GET", "POST"])
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

from services.cover_letter.cover_letter_generator import generate_cover_letter
from services.interview.interview_generator import generate_interview_questions
from services.email.email_generator import generate_job_emails
from services.linkedin.linkedin_optimizer import optimize_linkedin_profile
from services.salary.salary_predictor import predict_salary

@assistant_bp.route("/execute-tool", methods=["POST"])
def execute_tool():
    data = request.get_json(silent=True) or {}
    tool = data.get("tool", "cover-letter")
    candidate = get_candidate_context()

    try:
        if tool == "cover-letter":
            name = data.get("name") or candidate.get("candidate_name", "Candidate")
            job_title = data.get("job_title") or candidate.get("preferred_role", "Data Analyst")
            company = data.get("company", "Target Company")
            skills = [s.strip() for s in (data.get("skills") or "").split(",") if s.strip()] or candidate.get("skills", [])
            job_desc = data.get("job_desc", "")
            res = generate_cover_letter(name=name, skills=skills, job_title=job_title, company=company, job_desc=job_desc)

            body_html = "<br><br>".join(res.get("body_paragraphs", []))
            output = f"""<div class="p-3 bg-dark rounded border border-secondary text-light">
<div class="mb-2"><strong class="text-info">Subject:</strong> {res.get('subject')}</div>
<div class="mb-2"><strong class="text-secondary">{res.get('salutation', 'Dear Hiring Team,')}</strong></div>
<p class="mb-2">{res.get('introduction')}</p>
<div class="mb-2">{body_html}</div>
<p class="mb-3">{res.get('conclusion')}</p>
<div class="text-secondary">{res.get('sign_off', 'Sincerely,')}<br><strong>{name}</strong></div>
</div>"""
            return jsonify({"success": True, "output": output, "raw": res})

        elif tool == "interview":
            role = data.get("role") or candidate.get("preferred_role", "Data Analyst")
            skills = [s.strip() for s in (data.get("skills") or "").split(",") if s.strip()] or candidate.get("skills", [])
            company = data.get("company", "Target Company")
            round_type = data.get("round_type", "Technical Deep Dive")
            difficulty = data.get("difficulty", "Mid-Level Specialist")
            tone = data.get("tone", "Senior Technical Hiring Manager")
            count = int(data.get("count", 5))

            res = generate_interview_questions(
                role=role,
                skills=skills,
                resume_context=json.dumps(candidate),
                question_count=count,
                interviewer_role=tone,
                company=company,
                round_type=round_type,
                difficulty=difficulty
            )
            q_list = res.get("questions", [])
            html_parts = [f'<div class="mb-3 p-2 bg-dark rounded border border-primary-subtle text-primary small fw-semibold"><i class="bi bi-building me-1"></i> {company} · {round_type} ({difficulty}) · {tone}</div>']
            for idx, q in enumerate(q_list, 1):
                html_parts.append(f"""<div class="p-3 mb-3 bg-dark rounded border border-secondary">
<div class="d-flex justify-content-between align-items-center mb-1">
  <strong class="text-white">Q{idx}. [{q.get('type', 'Technical')}]</strong>
</div>
<p class="text-light fw-medium mb-2">{q.get('question')}</p>
<div class="small text-info mb-1"><i class="bi bi-lightbulb me-1"></i><strong>Strategy:</strong> {q.get('answer_tips')}</div>
<div class="small text-success"><i class="bi bi-check-circle me-1"></i><strong>Model Response:</strong> {q.get('sample_answer')}</div>
</div>""")
            return jsonify({"success": True, "output": "".join(html_parts), "raw": res})

        elif tool == "email":
            name = data.get("name") or candidate.get("candidate_name", "Candidate")
            role = data.get("role") or candidate.get("preferred_role", "Data Analyst")
            company = data.get("company", "Microsoft")
            skills = [s.strip() for s in (data.get("skills") or "").split(",") if s.strip()] or candidate.get("skills", [])

            res = generate_job_emails(
                name=name,
                skills=skills,
                role=role,
                company=company,
                email=candidate.get("email", "candidate@gmail.com"),
                phone=candidate.get("phone", "+91 9182679641"),
                resume_context=json.dumps(candidate)
            )
            cold = res.get("cold_outreach", {})
            inmail = res.get("linkedin_inmail", {})
            followup = res.get("follow_up_email", {})

            output = f"""<div class="d-flex flex-column gap-3">
<div class="p-3 bg-dark rounded border border-primary">
  <div class="d-flex justify-content-between mb-2">
    <strong class="text-primary"><i class="bi bi-envelope-paper-fill me-1"></i> 1. High-Impact Cold Outreach to Hiring Lead</strong>
    <span class="badge bg-primary-subtle text-primary">Direct Email</span>
  </div>
  <div class="text-info small mb-2"><strong>Subject:</strong> {cold.get('subject')}</div>
  <div class="text-light small" style="white-space: pre-line;">{cold.get('body')}</div>
</div>

<div class="p-3 bg-dark rounded border border-info">
  <div class="d-flex justify-content-between mb-2">
    <strong class="text-info"><i class="bi bi-linkedin me-1"></i> 2. LinkedIn Connection Note (&lt;300 Chars)</strong>
    <span class="badge bg-info-subtle text-info">Connection Request</span>
  </div>
  <div class="text-light small" style="white-space: pre-line;">{inmail.get('body')}</div>
</div>

<div class="p-3 bg-dark rounded border border-secondary">
  <div class="d-flex justify-content-between mb-2">
    <strong class="text-warning"><i class="bi bi-clock-history me-1"></i> 3. Strategic 4-Day Follow-Up Email</strong>
    <span class="badge bg-warning-subtle text-warning">Follow-Up</span>
  </div>
  <div class="text-info small mb-2"><strong>Subject:</strong> {followup.get('subject')}</div>
  <div class="text-light small" style="white-space: pre-line;">{followup.get('body')}</div>
</div>
</div>"""
            return jsonify({"success": True, "output": output, "raw": res})

        elif tool == "linkedin":
            name = data.get("name") or candidate.get("candidate_name", "Candidate")
            role = data.get("role") or candidate.get("preferred_role", "Data Analyst")
            skills = [s.strip() for s in (data.get("skills") or "").split(",") if s.strip()] or candidate.get("skills", [])

            res = optimize_linkedin_profile(
                name=name,
                role=role,
                skills=skills,
                experience_text=json.dumps(candidate)
            )
            headlines = res.get("suggested_headlines", [])
            h_html = "".join([f'<li class="mb-2 text-light">{h}</li>' for h in headlines])
            keywords = res.get("seo_keywords_to_add", [])
            k_html = " ".join([f'<span class="badge bg-primary-subtle text-primary me-1 mb-1">{k}</span>' for k in keywords])

            output = f"""<div class="d-flex flex-column gap-3">
<div class="p-3 bg-dark rounded border border-primary">
  <h6 class="text-primary fw-bold mb-2"><i class="bi bi-card-heading me-1"></i> Optimized High-Ranking Headlines</h6>
  <ul class="mb-0 small ps-3">{h_html}</ul>
</div>

<div class="p-3 bg-dark rounded border border-success">
  <h6 class="text-success fw-bold mb-2"><i class="bi bi-person-lines-fill me-1"></i> Search-Optimized 'About' Summary</h6>
  <div class="text-light small" style="white-space: pre-line;">{res.get('about_summary')}</div>
</div>

<div class="p-3 bg-dark rounded border border-secondary">
  <h6 class="text-warning fw-bold mb-2"><i class="bi bi-search me-1"></i> High-Traffic Recruiter SEO Keywords</h6>
  <div class="d-flex flex-wrap">{k_html}</div>
</div>
</div>"""
            return jsonify({"success": True, "output": output, "raw": res})

        elif tool == "salary":
            role = data.get("role") or candidate.get("preferred_role", "Data Analyst")
            try:
                yoe = float(data.get("experience") or 1.0)
            except Exception:
                yoe = 1.0
            location = data.get("location") or candidate.get("preferred_location", "Hyderabad")
            skills = [s.strip() for s in (data.get("skills") or "").split(",") if s.strip()] or candidate.get("skills", [])

            res = predict_salary(role=role, experience_years=yoe, skills=skills, location=location)

            low = res.get("low", 600000)
            med = res.get("median", 950000)
            high = res.get("high", 1400000)
            cur = res.get("currency", "INR")

            output = f"""<div class="d-flex flex-column gap-3">
<div class="p-4 bg-dark rounded border border-success text-center">
  <span class="text-secondary small text-uppercase fw-semibold">Estimated Market Salary Range</span>
  <div class="display-5 fw-bold text-success my-2">
    ₹{int(low/100000):,} - ₹{int(high/100000):,} LPA
  </div>
  <div class="text-info fw-semibold mb-3">Median Benchmark: ₹{int(med/100000):,} LPA ({location})</div>
  <p class="text-secondary small mb-0 px-3">{res.get('market_trend', 'Strong demand for analytics specialists in tier-1 tech hubs.')}</p>
</div>

<div class="p-3 bg-dark rounded border border-secondary">
  <h6 class="text-light fw-bold mb-2"><i class="bi bi-shield-check text-info me-1"></i> Compensation Valuation Analysis</h6>
  <p class="text-secondary small mb-0">{res.get('justification', 'Range evaluated based on verified skills stack in SQL, Python, Power BI and prevailing compensation tiers.')}</p>
</div>
</div>"""
            return jsonify({"success": True, "output": output, "raw": res})

        else:
            return jsonify({"success": False, "error": f"Unknown tool: {tool}"}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e), "output": f'<div class="text-danger p-3">Generation error: {str(e)}</div>'}), 500

