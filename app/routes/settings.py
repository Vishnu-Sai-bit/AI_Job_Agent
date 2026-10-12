"""
==========================================================
AI Job Copilot - Settings Route Blueprint
==========================================================
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.routes.main import get_candidate_context

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")

@settings_bp.route("/", methods=["GET", "POST"])
@settings_bp.route("/update", methods=["GET", "POST"])
def index():
    candidate = get_candidate_context()

    if request.method == "POST":
        flash("Account & Security preferences updated successfully!", "success")
        return redirect(url_for("settings.index"))

    return render_template(
        "settings/index.html",
        candidate=candidate,
        active_tab="settings"
    )
