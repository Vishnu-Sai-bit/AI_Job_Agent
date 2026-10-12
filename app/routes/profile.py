"""
==========================================================
AI Job Copilot - Profile & Settings Routes
==========================================================
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
import json
from pathlib import Path
from app.routes.main import get_candidate_context

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

@profile_bp.route("/", methods=["GET", "POST"])
@profile_bp.route("/update", methods=["GET", "POST"])
def index():
    candidate = get_candidate_context()

    if request.method == "POST":
        candidate["candidate_name"] = request.form.get("candidate_name", candidate.get("candidate_name", "")).strip()
        candidate["email"] = request.form.get("email", candidate.get("email", "")).strip()
        candidate["phone"] = request.form.get("phone", candidate.get("phone", "")).strip()
        candidate["preferred_role"] = request.form.get("preferred_role", candidate.get("preferred_role", "")).strip()
        candidate["preferred_location"] = request.form.get("preferred_location", candidate.get("preferred_location", "")).strip()
        
        raw_skills = request.form.get("skills", "")
        if raw_skills:
            candidate["skills"] = [s.strip() for s in raw_skills.split(",") if s.strip()]

        try:
            candidate["experience_years"] = float(request.form.get("experience_years", candidate.get("experience_years", 0.5)))
        except ValueError:
            pass

        # Persist updated profile
        save_path = Path("data/default_parsed_resume.json")
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(candidate, f, indent=2)
            flash("Profile updated successfully!", "success")
        except Exception as e:
            flash(f"Error saving profile: {e}", "danger")

        return redirect(url_for("profile.index"))

    return render_template(
        "profile/index.html",
        candidate=candidate,
        skills_csv=", ".join(candidate.get("skills", [])),
        active_tab="profile"
    )
