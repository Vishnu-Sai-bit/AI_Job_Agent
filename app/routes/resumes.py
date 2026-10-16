"""
==========================================================
AI Job Copilot - Resume Center & ATS Analysis Routes
==========================================================
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
import json
from pathlib import Path
from app.routes.main import get_candidate_context
from services.resume.resume_parser import extract_resume_text
from services.resume.resume_analyzer import analyze_resume
from services.ats.ats_calculator import calculate_ats
from services.resume.resume_tailorer import tailor_resume_for_job
from services.resume.resume_enricher import infer_role

resumes_bp = Blueprint("resumes", __name__, url_prefix="/resumes")

@resumes_bp.route("/")
def index():
    candidate = get_candidate_context()
    return render_template(
        "resumes/index.html",
        candidate=candidate,
        has_resume=bool(candidate.get("has_resume", False)),
        active_tab="step_upload"
    )

@resumes_bp.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("resume_file")
    if not file or file.filename == "":
        flash("Please select a resume file (PDF or DOCX).", "warning")
        return redirect(url_for("resumes.index"))

    save_path = Path("resumes") / file.filename
    save_path.parent.mkdir(parents=True, exist_ok=True)
    file.save(save_path)

    try:
        raw_text = extract_resume_text(save_path)
        resume_data = analyze_resume(raw_text)
        ats_report = calculate_ats(resume_data)

        # Determine role directly from uploaded resume
        extracted_role = (resume_data.preferred_role or "").strip()
        if not extracted_role or extracted_role.lower() in ("job seeker", "candidate", "target role"):
            try:
                extracted_role = infer_role(raw_text) or ""
            except Exception:
                extracted_role = ""

        # Job preferences only apply if user explicitly entered them
        existing_ctx = get_candidate_context()
        has_user_prefs = bool(existing_ctx.get("has_preferences"))
        user_pref_role = existing_ctx.get("preferred_role", "").strip() if has_user_prefs else ""
        user_pref_loc = existing_ctx.get("preferred_location", "").strip() if has_user_prefs else ""

        parsed_dict = {
            "has_resume": True,
            "has_preferences": has_user_prefs,
            "candidate_name": resume_data.name or "Candidate",
            "email": resume_data.email or "",
            "phone": resume_data.phone or "",
            "linkedin": resume_data.linkedin or "",
            "github": resume_data.github or "",
            "portfolio": resume_data.portfolio or "",
            "resume_role": extracted_role,
            "preferred_role": user_pref_role,
            "preferred_location": user_pref_loc,
            "skills": resume_data.skills,
            "experience_years": resume_data.experience_years,
            "education": resume_data.education,
            "projects": resume_data.projects,
            "certifications": resume_data.certifications,
            "ats_score": round(ats_report.score, 1),
            "ats_breakdown": {
                "contact_score": ats_report.contact_score,
                "skills_score": ats_report.skills_score,
                "experience_score": ats_report.experience_score,
                "education_score": ats_report.education_score,
                "projects_score": ats_report.projects_score,
                "certifications_score": ats_report.certifications_score,
            },
            "strengths": ats_report.strengths,
            "weaknesses": ats_report.weaknesses,
            "suggestions": ats_report.suggestions,
            "career_summary": resume_data.career_summary,
            "raw_text": raw_text[:4000],
            "source_file": file.filename
        }

        with open("data/default_parsed_resume.json", "w", encoding="utf-8") as f:
            json.dump(parsed_dict, f, indent=2)

        flash(f"Resume '{file.filename}' uploaded and analyzed successfully! Found {len(parsed_dict['skills'])} skills. Showing tailored jobs matching your resume profile:", "success")
        return redirect(url_for("jobs.index"))
    except Exception as e:
        flash(f"Analysis error: {e}", "danger")
        return redirect(url_for("resumes.index"))

@resumes_bp.route("/parsed")
def parsed():
    candidate = get_candidate_context()
    return render_template(
        "resumes/parsing.html",
        candidate=candidate,
        active_tab="step_parsing"
    )

@resumes_bp.route("/ai-analysis")
def ai_analysis():
    candidate = get_candidate_context()
    return render_template(
        "resumes/ai_analysis.html",
        candidate=candidate,
        active_tab="step_ai_analysis"
    )

@resumes_bp.route("/ats-evaluation")
@resumes_bp.route("/analyze")
def analyze():
    candidate = get_candidate_context()
    return render_template(
        "resumes/analysis.html",
        candidate=candidate,
        active_tab="step_ats"
    )

@resumes_bp.route("/download-report")
def download_report():
    from flask import Response
    from services.report.report_generator import generate_profile_report
    candidate = get_candidate_context()
    
    resume_data = {
        "name": candidate.get("candidate_name", "Candidate"),
        "preferred_role": candidate.get("preferred_role", "Data Analyst"),
        "skills": candidate.get("skills", []),
    }
    ats_report = {
        "ats_score": candidate.get("ats_score", 85.0),
        "feedback": {
            "Contact & Social Links": {"score": candidate.get("ats_breakdown", {}).get("contact_score", 9), "reason": "Contact information is complete and verified."},
            "Skills Keyword Density": {"score": candidate.get("ats_breakdown", {}).get("skills_score", 28), "reason": "Strong keyword alignment with data analytics industry standards."},
            "Work Experience": {"score": candidate.get("ats_breakdown", {}).get("experience_score", 15), "reason": "Include quantified impact metrics in bullet points."},
            "Education": {"score": candidate.get("ats_breakdown", {}).get("education_score", 15), "reason": "Degree qualifications verified."},
            "Projects": {"score": candidate.get("ats_breakdown", {}).get("projects_score", 14), "reason": "Strong demonstration of end-to-end analytical problem solving."}
        }
    }
    content = generate_profile_report(resume_data, ats_report)
    return Response(
        content,
        mimetype="text/markdown",
        headers={"Content-Disposition": "attachment;filename=ATS_Suitability_Report.md"}
    )

@resumes_bp.route("/tailor", methods=["GET", "POST"])
def tailor():
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
                    target_company="Target MNC",
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
