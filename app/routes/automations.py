"""
==========================================================
AI Job Copilot - Automation Center Routes
==========================================================
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.routes.main import get_candidate_context

automations_bp = Blueprint("automations", __name__, url_prefix="/automations")

# In-memory default automation settings
automation_settings = {
    "daily_digest": True,
    "min_match_threshold": 75,
    "preferred_sources": ["LinkedIn", "Naukri", "Indeed"],
    "auto_followup_reminder_days": 5,
    "email_alerts": True,
    "target_roles": ["Data Analyst", "Business Analyst", "BI Developer"],
    "target_locations": ["Hyderabad", "Bengaluru", "Remote (India)"]
}

@automations_bp.route("/", methods=["GET", "POST"])
def index():
    candidate = get_candidate_context()

    if request.method == "POST":
        automation_settings["daily_digest"] = "daily_digest" in request.form
        automation_settings["email_alerts"] = "email_alerts" in request.form
        try:
            automation_settings["min_match_threshold"] = int(request.form.get("min_match_threshold", 75))
            automation_settings["auto_followup_reminder_days"] = int(request.form.get("auto_followup_reminder_days", 5))
        except ValueError:
            pass

        sources = request.form.getlist("sources")
        if sources:
            automation_settings["preferred_sources"] = sources

        flash("Automation preferences successfully updated!", "success")
        return redirect(url_for("automations.index"))

    return render_template(
        "automations/index.html",
        candidate=candidate,
        settings=automation_settings,
        active_tab="automations"
    )
