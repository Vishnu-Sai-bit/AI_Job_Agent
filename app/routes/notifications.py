"""
==========================================================
AI Job Copilot - Notifications Route Blueprint
==========================================================
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.routes.main import get_candidate_context

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")

mock_notifications = [
    {
        "id": "notif_1",
        "title": "High Match Job Discovered!",
        "message": "Junior Data Analyst at GlobalCorp matches 92% of your verified skills.",
        "category": "job_match",
        "time": "10 mins ago",
        "is_read": False
    },
    {
        "id": "notif_2",
        "title": "Application Follow-up Due",
        "message": "It has been 5 days since you saved/applied to Scout Inc. Consider sending a follow-up note.",
        "category": "reminder",
        "time": "2 hours ago",
        "is_read": False
    },
    {
        "id": "notif_3",
        "title": "ATS Score Updated",
        "message": "Your latest parsed resume achieved an ATS compatibility score of 79.0%.",
        "category": "ats",
        "time": "1 day ago",
        "is_read": True
    }
]

@notifications_bp.route("/")
def index():
    candidate = get_candidate_context()
    return render_template(
        "notifications/index.html",
        candidate=candidate,
        notifications=mock_notifications,
        active_tab="notifications"
    )

@notifications_bp.route("/mark-all-read", methods=["POST", "GET"])
@notifications_bp.route("/read-all", methods=["POST", "GET"])
def mark_all_read():
    for n in mock_notifications:
        n["is_read"] = True
    flash("All notifications marked as read.", "info")
    return redirect(url_for("notifications.index"))
