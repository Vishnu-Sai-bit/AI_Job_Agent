import os
import uuid
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models.resume import Resume
from utils.file_validation import validate_uploaded_file
from utils.text_extraction import extract_text
from services.resume_parser import ResumeParser
from services.ats_scorer import ATSScorer
from services.gemini_service import GeminiService
from tasks.recompute_matches import recompute_user_matches
from utils.logging_config import logger

resume_bp = Blueprint("resume", __name__, url_prefix="/resume")

@resume_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload_resume():
    if request.method == "POST":
        if "resume_file" not in request.files:
            flash("No file part in the request.", "danger")
            return redirect(request.url)

        file = request.files["resume_file"]
        is_valid, err_msg, ext = validate_uploaded_file(file)
        if not is_valid:
            flash(err_msg or "Invalid file upload.", "danger")
            return redirect(request.url)

        # Ensure upload folder exists outside static
        upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Secure unique filename
        original_name = secure_filename(file.filename)
        unique_name = f"user_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
        save_path = upload_dir / unique_name
        file.save(str(save_path))

        # Extract text
        raw_text, extract_err = extract_text(str(save_path), ext)
        if extract_err or not raw_text.strip():
            # Clean up corrupted file
            if save_path.exists():
                save_path.unlink()
            flash(extract_err or "Unable to extract text from document.", "danger")
            return redirect(request.url)

        # Parse structured intelligence (deterministic baseline)
        parser = ResumeParser()
        parsed_data = parser.parse(raw_text)

        # Deep Gemini AI extraction & critique if API key is configured
        gemini = GeminiService()
        gemini_result = None
        if gemini.is_available():
            try:
                gemini_result = gemini.analyze_resume_deep(raw_text)
                if gemini_result and gemini_result.get("parsed_data"):
                    g_data = gemini_result["parsed_data"]
                    for k in ["name", "email", "phone", "location", "headline", "summary", "experience_years"]:
                        if g_data.get(k):
                            parsed_data[k] = g_data[k]
                    if g_data.get("skills"):
                        parsed_data["skills"] = sorted(list(set(parsed_data.get("skills", []) + g_data["skills"])))
                    if g_data.get("skills_by_category"):
                        parsed_data["skills_by_category"] = g_data["skills_by_category"]
                    if g_data.get("experience"):
                        parsed_data["experience"] = g_data["experience"]
                    if g_data.get("projects"):
                        parsed_data["projects"] = g_data["projects"]
                    if g_data.get("education"):
                        parsed_data["education"] = g_data["education"]
                    if g_data.get("certifications"):
                        parsed_data["certifications"] = g_data["certifications"]
            except Exception as e:
                logger.error(f"Gemini resume intelligence error: {e}")

        # Compute ATS quality score
        scorer = ATSScorer()
        ats_report = scorer.score_resume(raw_text, parsed_data)
        if gemini_result and gemini_result.get("ai_critique"):
            ats_report["gemini_critique"] = gemini_result["ai_critique"]

        # Deactivate old resumes
        Resume.query.filter_by(user_id=current_user.id, is_active=True).update({"is_active": False})

        # Save new resume record
        resume = Resume(
            user_id=current_user.id,
            filename=original_name,
            file_path=str(save_path),
            file_type=ext,
            file_size_bytes=save_path.stat().st_size,
            raw_text=raw_text,
            parsed_data=parsed_data,
            readability_score=ats_report["breakdown"]["readability"],
            completeness_score=ats_report["breakdown"]["completeness"],
            ats_quality_score=ats_report["overall_score"],
            ats_feedback=ats_report,
            is_active=True
        )
        db.session.add(resume)

        # Sync with candidate profile
        profile = current_user.candidate_profile
        if not profile.full_name and parsed_data.get("name"):
            profile.full_name = parsed_data["name"]
        if not profile.phone and parsed_data.get("phone"):
            profile.phone = parsed_data["phone"]
        if not profile.location and parsed_data.get("location"):
            profile.location = parsed_data["location"]
        if not profile.headline and parsed_data.get("headline"):
            profile.headline = parsed_data["headline"]
        if not profile.summary and parsed_data.get("summary"):
            profile.summary = parsed_data["summary"]

        # Merge new skills
        existing_skills = set(profile.skills or [])
        new_skills = set(parsed_data.get("skills", []))
        profile.skills = sorted(list(existing_skills.union(new_skills)))

        if parsed_data.get("experience_years"):
            profile.experience_years = parsed_data["experience_years"]
        if parsed_data.get("education"):
            profile.education = parsed_data["education"]
        if parsed_data.get("projects"):
            profile.projects = parsed_data["projects"]
        if parsed_data.get("certifications"):
            profile.certifications = parsed_data["certifications"]

        db.session.commit()

        # Recalculate job compatibility matches immediately
        recompute_user_matches(current_user, resume)

        flash("Resume uploaded and analyzed successfully!", "success")
        return redirect(url_for("resume.resume_analysis"))

    resumes = current_user.resumes.order_by(Resume.uploaded_at.desc()).all()
    return render_template("resume_upload.html", resumes=resumes)


@resume_bp.route("/analysis")
@login_required
def resume_analysis():
    resume = current_user.get_active_resume()
    if not resume:
        flash("Please upload a resume first to view the extracted intelligence.", "info")
        return redirect(url_for("resume.upload_resume"))

    profile = current_user.candidate_profile
    return render_template("resume_analysis.html", resume=resume, profile=profile)


@resume_bp.route("/update-profile", methods=["POST"])
@login_required
def update_parsed_profile():
    profile = current_user.candidate_profile
    resume = current_user.get_active_resume()

    profile.full_name = request.form.get("full_name", profile.full_name)
    profile.headline = request.form.get("headline", profile.headline)
    profile.location = request.form.get("location", profile.location)
    profile.summary = request.form.get("summary", profile.summary)
    
    skills_raw = request.form.get("skills", "")
    profile.skills = [s.strip() for s in skills_raw.split(",") if s.strip()]

    try:
        profile.experience_years = float(request.form.get("experience_years", profile.experience_years))
    except ValueError:
        pass

    db.session.commit()

    if resume:
        recompute_user_matches(current_user, resume)

    flash("Resume profile updated and job matches refreshed.", "success")
    return redirect(url_for("resume.resume_analysis"))


@resume_bp.route("/delete/<int:resume_id>", methods=["POST"])
@login_required
def delete_resume(resume_id):
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    
    # Remove file from disk
    try:
        if os.path.exists(resume.file_path):
            os.remove(resume.file_path)
    except Exception:
        pass

    db.session.delete(resume)
    db.session.commit()
    flash("Resume and stored parsing data deleted.", "info")
    return redirect(url_for("resume.upload_resume"))


@resume_bp.route("/analyze-with-gemini", methods=["POST"])
@login_required
def analyze_with_gemini():
    resume = current_user.get_active_resume()
    if not resume:
        flash("Please upload a resume first.", "warning")
        return redirect(url_for("resume.upload_resume"))

    gemini = GeminiService()
    if not gemini.is_available():
        flash("Gemini API Key is not configured. Please add GEMINI_API_KEY to your .env file.", "warning")
        return redirect(url_for("resume.resume_analysis"))

    result = gemini.analyze_resume_deep(resume.raw_text or "")
    if not result:
        flash("Gemini AI was unable to process the resume text. Please verify your GEMINI_API_KEY in .env.", "danger")
        return redirect(url_for("resume.resume_analysis"))

    # Update parsed data
    parsed_data = dict(resume.parsed_data or {})
    g_data = result.get("parsed_data", {})
    for k in ["name", "email", "phone", "location", "headline", "summary", "experience_years"]:
        if g_data.get(k):
            parsed_data[k] = g_data[k]
    if g_data.get("skills"):
        parsed_data["skills"] = sorted(list(set(parsed_data.get("skills", []) + g_data["skills"])))
    if g_data.get("skills_by_category"):
        parsed_data["skills_by_category"] = g_data["skills_by_category"]
    if g_data.get("experience"):
        parsed_data["experience"] = g_data["experience"]
    if g_data.get("projects"):
        parsed_data["projects"] = g_data["projects"]
    if g_data.get("education"):
        parsed_data["education"] = g_data["education"]
    if g_data.get("certifications"):
        parsed_data["certifications"] = g_data["certifications"]

    resume.parsed_data = parsed_data

    # Update ATS feedback with Gemini critique
    ats_feedback = dict(resume.ats_feedback or {})
    if result.get("ai_critique"):
        ats_feedback["gemini_critique"] = result["ai_critique"]
    resume.ats_feedback = ats_feedback

    # Update candidate profile
    profile = current_user.candidate_profile
    if profile:
        if parsed_data.get("name"):
            profile.full_name = parsed_data["name"]
        if parsed_data.get("headline"):
            profile.headline = parsed_data["headline"]
        if parsed_data.get("summary"):
            profile.summary = parsed_data["summary"]
        if parsed_data.get("skills"):
            profile.skills = parsed_data["skills"]
        if parsed_data.get("experience_years"):
            profile.experience_years = parsed_data["experience_years"]
        if parsed_data.get("projects"):
            profile.projects = parsed_data["projects"]
        if parsed_data.get("education"):
            profile.education = parsed_data["education"]

    db.session.commit()

    # Recalculate job compatibility matches immediately
    recompute_user_matches(current_user, resume)

    flash("Resume successfully analyzed with Google Gemini AI!", "success")
    return redirect(url_for("resume.resume_analysis"))
