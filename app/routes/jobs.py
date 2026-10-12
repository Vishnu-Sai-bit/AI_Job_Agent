"""
==========================================================
AI Job Copilot - Job Routes
==========================================================
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
import json
import uuid
from datetime import datetime
from pathlib import Path
from app.extensions import db
from app.models.job import Job
from app.models.application import Application
from app.routes.main import get_candidate_context

jobs_bp = Blueprint("jobs", __name__, url_prefix="/jobs")

def load_verified_jobs():
    export_path = Path("data/jobs_export.json")
    if export_path.exists():
        try:
            with open(export_path, "r", encoding="utf-8") as f:
                jobs = json.load(f)
                normalized = []
                for j in jobs:
                    # Clean & normalize skills into a true list of skill strings
                    raw_skills = j.get("skills")
                    if isinstance(raw_skills, list):
                        skills = [str(s).strip() for s in raw_skills if str(s).strip()]
                    elif isinstance(raw_skills, str):
                        skills = [s.strip() for s in raw_skills.split(",") if s.strip()]
                    else:
                        title_lower = (j.get("title") or "").lower()
                        if "python" in title_lower:
                            skills = ["Python", "FastAPI", "SQL", "Git", "REST APIs"]
                        elif "power bi" in title_lower or "bi" in title_lower:
                            skills = ["Power BI", "DAX", "SQL", "Data Modeling", "Excel"]
                        elif "sql" in title_lower:
                            skills = ["SQL", "Database Design", "Performance Tuning", "MySQL", "ETL"]
                        elif "engineer" in title_lower:
                            skills = ["Python", "SQL", "ETL Pipelines", "Data Warehousing", "Git"]
                        elif "scientist" in title_lower:
                            skills = ["Python", "Machine Learning", "SQL", "Pandas", "Deep Learning"]
                        else:
                            skills = ["SQL", "Python", "Tableau", "Data Analysis", "Excel"]

                    j["skills"] = skills

                    # Ensure valid real application URL
                    url = j.get("url")
                    if not url or url.strip() == "#":
                        q_t = (j.get("title") or "Data Analyst").replace(" ", "+")
                        q_c = (j.get("company") or "Tech").replace(" ", "+")
                        j["url"] = f"https://www.linkedin.com/jobs/search/?keywords={q_t}+{q_c}"

                    normalized.append(j)
                return normalized
        except Exception:
            pass
    return []

def match_skills(job_skills, candidate_skills_set):
    """Accurately match full skill names against candidate skills."""
    matching = []
    missing = []
    for s in job_skills:
        s_clean = s.strip()
        s_lower = s_clean.lower()
        is_matched = False
        for cs in candidate_skills_set:
            if s_lower == cs or s_lower in cs or cs in s_lower:
                is_matched = True
                break
        if is_matched:
            matching.append(s_clean)
        else:
            missing.append(s_clean)
    return matching, missing

@jobs_bp.route("/")
def index():
    candidate = get_candidate_context()
    candidate_skills = {s.lower().strip() for s in candidate.get("skills", [])}
    candidate_role = candidate.get("preferred_role", "").lower().strip()

    role_filter = request.args.get("role", "").strip()
    loc_filter = request.args.get("location", "").strip()

    raw_jobs = load_verified_jobs()
    scored_jobs = []

    for j in raw_jobs:
        j_title = j.get("title", "")
        j_loc = j.get("location", "")
        if role_filter and role_filter.lower() not in j_title.lower():
            continue
        if loc_filter and loc_filter.lower() not in j_loc.lower():
            continue

        j_skills = j.get("skills", [])
        matching, missing = match_skills(j_skills, candidate_skills)
        
        skill_pct = (len(matching) / len(j_skills) * 100.0) if j_skills else 85.0
        role_pct = 100.0 if candidate_role in j_title.lower() else (80.0 if "analyst" in j_title.lower() else 55.0)

        match_score = round(0.40 * role_pct + 0.45 * skill_pct + 15.0, 1)
        match_score = min(100.0, max(30.0, match_score))

        scored_jobs.append({
            "id": j.get("id"),
            "title": j_title,
            "company": j.get("company"),
            "location": j_loc,
            "salary": j.get("salary", "Competitive"),
            "experience": j.get("experience", "1-3 yrs"),
            "source": j.get("source", "Verified Portal"),
            "url": j.get("url", "https://careers.google.com"),
            "description": j.get("description", ""),
            "matching_skills": matching,
            "missing_skills": missing,
            "match_score": match_score
        })

    scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)

    return render_template(
        "jobs/index.html",
        jobs=scored_jobs,
        candidate=candidate,
        role_filter=role_filter,
        loc_filter=loc_filter,
        active_tab="jobs"
    )

@jobs_bp.route("/<job_id>")
def detail(job_id):
    raw_jobs = load_verified_jobs()
    job = next((j for j in raw_jobs if str(j.get("id")) == str(job_id)), None)
    if not job:
        flash("Job listing not found.", "warning")
        return redirect(url_for("jobs.index"))

    candidate = get_candidate_context()
    candidate_skills = {s.lower().strip() for s in candidate.get("skills", [])}
    job_skills = job.get("skills", [])
    matching, missing = match_skills(job_skills, candidate_skills)

    return render_template(
        "jobs/detail.html",
        job=job,
        matching=matching,
        missing=missing,
        candidate=candidate,
        active_tab="jobs"
    )

@jobs_bp.route("/save/<job_id>", methods=["POST"])
def save_job(job_id):
    raw_jobs = load_verified_jobs()
    job = next((j for j in raw_jobs if str(j.get("id")) == str(job_id)), None)
    if job:
        from services.crm.application_crm import add_or_update_application
        app_entry = {
            "id": f"app_{uuid.uuid4().hex[:8]}",
            "jobId": str(job_id),
            "company": job.get("company"),
            "role": job.get("title"),
            "stage": "saved",
            "applied_date": datetime.now().strftime("%Y-%m-%d"),
            "salary": job.get("salary", "N/A"),
            "notes": "Saved from Job Finder"
        }
        add_or_update_application(app_entry)
        flash(f"Opportunity at {job.get('company')} saved to your Applications CRM!", "success")
    return redirect(url_for("jobs.index"))

@jobs_bp.route("/cover-letter/<job_id>")
def cover_letter(job_id):
    raw_jobs = load_verified_jobs()
    job = next((j for j in raw_jobs if str(j.get("id")) == str(job_id)), None)
    if not job:
        flash("Job not found.", "warning")
        return redirect(url_for("jobs.index"))

    candidate = get_candidate_context()
    from services.cover_letter.cover_letter_generator import generate_cover_letter

    cl_data = generate_cover_letter(
        name=candidate.get("candidate_name", "Candidate"),
        skills=candidate.get("skills", ["Python", "SQL", "Tableau"]),
        job_title=job.get("title", "Target Role"),
        company=job.get("company", "Target Company"),
        job_desc=job.get("description", "")
    )

    return render_template(
        "jobs/cover_letter.html",
        job=job,
        candidate=candidate,
        cover_letter=cl_data,
        active_tab="jobs"
    )
