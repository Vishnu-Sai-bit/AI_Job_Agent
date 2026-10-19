from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions import db
from models.job import Job
from models.job_match import JobMatch
from models.job_source import JobSource
from models.application import Application
from tasks.recompute_matches import recompute_user_matches

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))
    
    total_jobs = Job.query.filter_by(status="active").count()
    total_sources = JobSource.query.filter_by(is_active=True).count()
    return render_template("index.html", total_jobs=total_jobs, total_sources=total_sources)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    profile = current_user.candidate_profile
    active_resume = current_user.get_active_resume()
    
    # Calculate profile completeness
    completeness = 20
    if profile.full_name:
        completeness += 15
    if profile.skills and len(profile.skills) > 0:
        completeness += 25
    if active_resume:
        completeness += 25
    if profile.preferred_titles and len(profile.preferred_titles) > 0:
        completeness += 15
    completeness = min(100, completeness)

    # Top recommended jobs
    top_matches = []
    if active_resume:
        top_matches = JobMatch.query.filter_by(
            user_id=current_user.id,
            resume_id=active_resume.id
        ).join(Job).filter(Job.status == "active").order_by(JobMatch.match_score.desc()).limit(5).all()

    # Recent saved jobs
    saved_jobs = current_user.saved_jobs.order_by(db.desc("saved_at")).limit(5).all()

    # Application stage counts
    app_counts = {
        "saved": 0,
        "prepared": 0,
        "applied": 0,
        "interviewing": 0,
        "offer": 0,
        "rejected": 0
    }
    applications = current_user.applications.all()
    for app in applications:
        if app.status in app_counts:
            app_counts[app.status] += 1

    total_active_jobs = Job.query.filter_by(status="active").count()

    return render_template(
        "dashboard.html",
        profile=profile,
        resume=active_resume,
        completeness=completeness,
        top_matches=top_matches,
        saved_jobs=saved_jobs,
        app_counts=app_counts,
        total_applications=len(applications),
        total_active_jobs=total_active_jobs
    )


@dashboard_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    profile = current_user.candidate_profile
    if request.method == "POST":
        profile.full_name = request.form.get("full_name", "").strip()
        profile.phone = request.form.get("phone", "").strip()
        profile.location = request.form.get("location", "").strip()
        profile.headline = request.form.get("headline", "").strip()
        profile.summary = request.form.get("summary", "").strip()
        
        # Parse titles
        titles_raw = request.form.get("preferred_titles", "")
        profile.preferred_titles = [t.strip() for t in titles_raw.split(",") if t.strip()]

        # Parse locations
        countries_raw = request.form.get("preferred_countries", "")
        profile.preferred_countries = [c.strip() for c in countries_raw.split(",") if c.strip()]

        cities_raw = request.form.get("preferred_cities", "")
        profile.preferred_cities = [c.strip() for c in cities_raw.split(",") if c.strip()]

        # Work modes
        modes = request.form.getlist("work_modes")
        profile.work_modes = modes if modes else ["remote", "hybrid", "on-site"]

        profile.experience_level = request.form.get("experience_level", "mid")
        profile.visa_sponsorship_required = bool(request.form.get("visa_sponsorship_required"))

        min_sal = request.form.get("min_salary")
        profile.min_salary = float(min_sal) if min_sal and min_sal.strip() else None

        db.session.commit()

        # Recompute matches with updated preferences
        if current_user.get_active_resume():
            recompute_user_matches(current_user)

        flash("Profile and preferences updated successfully.", "success")
        return redirect(url_for("dashboard.settings"))

    return render_template("settings.html", profile=profile)
