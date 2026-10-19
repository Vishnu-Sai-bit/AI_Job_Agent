from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models.job import Job
from models.job_match import JobMatch
from services.job_matcher import JobMatcher

ats_bp = Blueprint("ats", __name__, url_prefix="/ats")

@ats_bp.route("")
@login_required
def ats_report():
    resume = current_user.get_active_resume()
    if not resume:
        flash("Please upload a resume first to view your ATS quality assessment.", "info")
        return redirect(url_for("resume.upload_resume"))

    feedback = resume.ats_feedback or {}
    return render_template(
        "ats_report.html",
        resume=resume,
        feedback=feedback,
        profile=current_user.candidate_profile
    )


@ats_bp.route("/job/<int:job_id>")
@login_required
def job_ats_report(job_id):
    resume = current_user.get_active_resume()
    if not resume:
        flash("Please upload a resume first to evaluate job compatibility.", "info")
        return redirect(url_for("resume.upload_resume"))

    job = Job.query.get_or_404(job_id)
    match = JobMatch.query.filter_by(
        user_id=current_user.id,
        resume_id=resume.id,
        job_id=job.id
    ).first()

    if not match:
        matcher = JobMatcher()
        res = matcher.compute_match(resume, current_user.candidate_profile, job)
        match = JobMatch(
            user_id=current_user.id,
            resume_id=resume.id,
            job_id=job.id,
            match_score=res["match_score"],
            score_breakdown=res["score_breakdown"],
            skill_match_details=res["skill_match_details"],
            match_explanation=res["match_explanation"],
            eligibility_flags=res["eligibility_flags"]
        )

    return render_template(
        "ats_report.html",
        resume=resume,
        job=job,
        match=match,
        feedback=resume.ats_feedback or {},
        profile=current_user.candidate_profile
    )
