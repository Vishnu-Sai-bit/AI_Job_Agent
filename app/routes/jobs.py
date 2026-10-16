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

def is_role_relevant(job_title: str, target_role: str) -> tuple:
    """Check if job title matches candidate role or its related domain aliases."""
    if not target_role:
        return True, 75.0
    
    t_lower = target_role.lower().strip()
    j_lower = job_title.lower().strip()
    
    if t_lower in j_lower:
        return True, 100.0
        
    from services.matcher.job_matcher import ROLE_ALIASES
    
    for base_role, aliases in ROLE_ALIASES.items():
        if base_role in t_lower or t_lower in base_role:
            if any(alias in j_lower for alias in aliases):
                return True, 85.0
                
    t_words = [w for w in t_lower.split() if len(w) > 2]
    overlap = sum(1 for w in t_words if w in j_lower)
    if overlap > 0:
        return True, round(50.0 + (overlap / len(t_words)) * 35.0, 1)
        
    return False, 0.0

def check_experience_fit(cand_exp: float, job_exp_str: str) -> tuple:
    """Calculate experience alignment."""
    import re
    if not job_exp_str:
        return True, 85.0, "General Exp"
    
    nums = re.findall(r"\d+", job_exp_str)
    if not nums:
        return True, 85.0, job_exp_str
        
    min_exp = float(nums[0])
    max_exp = float(nums[1]) if len(nums) > 1 else (min_exp + 3.0)
    
    if min_exp <= cand_exp <= max_exp:
        return True, 100.0, f"Aligned ({job_exp_str} fits your {cand_exp:g} yrs)"
    elif cand_exp >= max_exp:
        return True, 90.0, f"Qualified ({cand_exp:g} yrs qualifies for {job_exp_str})"
    elif cand_exp >= (min_exp - 1.0):
        return True, 75.0, f"Target Fit ({job_exp_str})"
    else:
        return False, 30.0, f"Requires {job_exp_str}"

@jobs_bp.route("/")
def index():
    candidate = get_candidate_context()
    has_resume = bool(candidate.get("has_resume"))
    candidate_skills = {s.lower().strip() for s in candidate.get("skills", [])}
    candidate_role = candidate.get("preferred_role", "").strip()
    candidate_exp = float(candidate.get("experience_years", 0) or 0)
    candidate_loc = candidate.get("preferred_location", "").strip()

    # Pre-populate filters from candidate resume if user has not entered a custom query
    requested_role = request.args.get("role")
    role_filter = requested_role.strip() if requested_role is not None else (candidate_role if has_resume else "")
    
    requested_loc = request.args.get("location")
    loc_filter = requested_loc.strip() if requested_loc is not None else ""
    
    exp_filter = request.args.get("experience", "").strip()
    mode_filter = request.args.get("mode", "").strip()
    fetch_live = request.args.get("live", "").lower() in ("true", "1", "yes")

    raw_jobs = load_verified_jobs()

    # Auto-fetch live jobs when resume is present OR when explicitly requested
    # This ensures personalized matches come from multiple live portals
    should_fetch_live = fetch_live or (has_resume and len(raw_jobs) < 25)
    if should_fetch_live:
        try:
            from services.jobs.live_job_aggregator import aggregate_live_jobs
            live_res = aggregate_live_jobs(
                role=role_filter or candidate_role or "Data Analyst",
                location=loc_filter or candidate_loc or "India",
                candidate_skills=list(candidate_skills),
                max_total=100
            )
            live_jobs = live_res.get("jobs", [])
            seen_combos = {f"{(j.get('title') or '').lower()}::{(j.get('company') or '').lower()}" for j in raw_jobs}
            added = 0
            for lj in live_jobs:
                combo = f"{(lj.get('title') or '').lower()}::{(lj.get('company') or '').lower()}"
                if combo not in seen_combos:
                    seen_combos.add(combo)
                    raw_jobs.append(lj)
                    added += 1
            if fetch_live:
                flash(f"Fetched {added} additional live job postings from active APIs!", "success")
        except Exception as e:
            if fetch_live:
                flash(f"Live aggregation notice: {e}", "info")

    active_target_role = role_filter or candidate_role
    scored_jobs = []

    schedule_filter = request.args.get("schedule", "").strip().lower()
    workstyle_filter = (request.args.get("workstyle") or request.args.get("mode", "")).strip().lower()
    if workstyle_filter:
        mode_filter = workstyle_filter

    for j in raw_jobs:
        j_title = j.get("title", "")
        j_loc = j.get("location", "")
        j_exp = j.get("experience", "1-3 yrs")
        j_skills = j.get("skills", [])
        
        # 1. Role keyword filter (Applies whether has_resume or not!)
        if requested_role:
            q = requested_role.lower().strip()
            q_terms = [t for t in q.replace("/", " ").replace("-", " ").split() if len(t) > 2]
            
            in_title = q in j_title.lower()
            in_skills = any(q in s.lower() for s in j_skills)
            in_company = q in (j.get("company") or "").lower()
            terms_in_title = any(t in j_title.lower() for t in q_terms) if q_terms else False
            terms_in_skills = any(any(t in s.lower() for t in q_terms) for s in j_skills) if q_terms else False
            
            if not (in_title or in_skills or in_company or terms_in_title or terms_in_skills):
                continue

        # 2. Work style / Mode filter
        if mode_filter == "remote" and "remote" not in j_loc.lower():
            continue
        elif mode_filter in ["office", "onsite"] and ("remote" in j_loc.lower() or "hybrid" in j_loc.lower()):
            continue
        elif mode_filter == "hybrid" and "hybrid" not in j_loc.lower():
            continue

        # 3. Schedule filter
        if schedule_filter:
            j_sched_text = (j_exp + " " + j_title + " " + (j.get("description") or "")).lower()
            if schedule_filter == "full-time" and not any(k in j_sched_text for k in ["full-time", "full day", "fulltime"]):
                continue
            elif schedule_filter == "part-time" and not any(k in j_sched_text for k in ["part-time", "parttime"]):
                continue
            elif schedule_filter == "internship" and not any(k in j_sched_text for k in ["intern", "internship", "fresher"]):
                continue
            elif schedule_filter == "project" and not any(k in j_sched_text for k in ["project", "contract", "freelance"]):
                continue

        # 4. Location filter if specified
        if loc_filter and loc_filter.lower() not in j_loc.lower():
            continue

        # 5. Experience dropdown filter if selected
        if exp_filter:
            if exp_filter == "0-2" and not any(k in j_exp for k in ["0-2", "1-2", "0-1", "fresher", "intern"]):
                continue
            elif exp_filter == "2-5" and not any(k in j_exp for k in ["2-4", "2-5", "1-3", "3-5"]):
                continue
            elif exp_filter == "5+" and not any(k in j_exp for k in ["5+", "5-8", "6+", "7+", "senior", "lead"]):
                continue

        # Skill matching
        matching, missing = match_skills(j_skills, candidate_skills)
        skill_pct = (len(matching) / len(j_skills) * 100.0) if j_skills else (75.0 if has_resume else 50.0)

        # Role relevance & Experience fit
        is_rel, role_score = is_role_relevant(j_title, active_target_role)
        is_exp_fit, exp_score, exp_note = check_experience_fit(candidate_exp, j_exp)

        # Multi-factor score: 40% role relevance + 40% skills alignment + 20% experience fit
        match_score = round(0.40 * role_score + 0.40 * skill_pct + 0.20 * exp_score, 1)
        match_score = min(100.0, max(30.0, match_score))

        scored_jobs.append({
            "id": j.get("id"),
            "title": j_title,
            "company": j.get("company"),
            "location": j_loc,
            "salary": j.get("salary", "Competitive"),
            "experience": j_exp,
            "experience_fit_note": exp_note if has_resume else "",
            "source": j.get("source", "Verified Portal"),
            "url": j.get("url", "https://careers.google.com"),
            "description": j.get("description", ""),
            "matching_skills": matching if has_resume else [],
            "missing_skills": missing if has_resume else [],
            "skills": j_skills,
            "match_score": match_score if has_resume else None
        })

    if has_resume:
        scored_jobs.sort(key=lambda x: x["match_score"] or 0, reverse=True)

    # Dynamic location segment counts for matching jobs
    remote_count = sum(1 for j in scored_jobs if "remote" in (j.get("location") or "").lower())
    hyd_count = sum(1 for j in scored_jobs if "hyderabad" in (j.get("location") or "").lower())
    blr_count = sum(1 for j in scored_jobs if any(b in (j.get("location") or "").lower() for b in ["bangalore", "bengaluru"]))

    return render_template(
        "jobs/index.html",
        jobs=scored_jobs,
        candidate=candidate,
        has_resume=has_resume,
        role_filter=role_filter,
        loc_filter=loc_filter,
        exp_filter=exp_filter,
        schedule_filter=schedule_filter,
        workstyle_filter=workstyle_filter,
        remote_count=remote_count,
        hyd_count=hyd_count,
        blr_count=blr_count,
        total_count=len(scored_jobs),
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
