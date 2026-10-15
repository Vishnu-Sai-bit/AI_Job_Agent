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

resumes_bp = Blueprint("resumes", __name__, url_prefix="/resumes")

@resumes_bp.route("/")
def index():
    candidate = get_candidate_context()
    resume_folder = Path("resumes")
    existing_files = []
    if resume_folder.exists():
        existing_files = [f.name for f in resume_folder.glob("*.pdf")] + [f.name for f in resume_folder.glob("*.docx")]

    return render_template(
        "resumes/index.html",
        candidate=candidate,
        files=existing_files,
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

        parsed_dict = {
            "candidate_name": resume_data.name or "Candidate",
            "email": resume_data.email or "candidate@gmail.com",
            "phone": resume_data.phone or "+91 9182679641",
            "linkedin": resume_data.linkedin or "",
            "github": resume_data.github or "",
            "portfolio": resume_data.portfolio or "",
            "preferred_role": resume_data.preferred_role or "Data Analyst",
            "preferred_location": resume_data.preferred_location or "Hyderabad",
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

        flash(f"Resume '{file.filename}' uploaded and parsed successfully! ATS Score: {parsed_dict['ats_score']}%", "success")
        return redirect(url_for("resumes.parsed"))
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
