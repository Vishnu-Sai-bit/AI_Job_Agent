"""
==========================================================
AI Job Copilot - Applications CRM Routes
==========================================================
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from services.crm.application_crm import (
    get_all_applications,
    add_or_update_application,
    delete_application as crm_delete,
    generate_followup_message
)

applications_bp = Blueprint("applications", __name__, url_prefix="/applications")

@applications_bp.route("/")
def index():
    apps = get_all_applications()
    for a in apps:
        if not a.get("stage"):
            a["stage"] = a.get("status", "saved")
        if not a.get("applied_date"):
            a["applied_date"] = a.get("date_applied", "Recent")
    stages = ["saved", "applied", "interview", "offer", "rejected"]
    counts = {s: sum(1 for a in apps if a.get("stage") == s) for s in stages}

    return render_template(
        "applications/index.html",
        applications=apps,
        counts=counts,
        stages=stages,
        active_tab="applications"
    )

@applications_bp.route("/update-stage", methods=["POST"])
def update_stage():
    app_id = request.form.get("app_id")
    new_stage = request.form.get("stage")

    apps = get_all_applications()
    target = next((a for a in apps if a.get("id") == app_id), None)
    if target:
        target["stage"] = new_stage
        target["status"] = new_stage
        add_or_update_application(target)
        flash(f"Application stage updated to '{new_stage}'!", "success")
    return redirect(url_for("applications.index"))

@applications_bp.route("/delete/<app_id>", methods=["POST"])
def delete_app(app_id):
    crm_delete(app_id)
    flash("Application record removed.", "info")
    return redirect(url_for("applications.index"))

@applications_bp.route("/followup/<app_id>")
def followup(app_id):
    apps = get_all_applications()
    target = next((a for a in apps if a.get("id") == app_id), None)
    msg = ""
    if target:
        msg = generate_followup_message(
            candidate_name="Vishnu Sai",
            company_name=target.get("company", "Target MNC"),
            role_title=target.get("role", "Data Analyst"),
            applied_date=target.get("applied_date", "recent")
        )
    return jsonify({"status": "success", "message": msg})
