"""
==========================================================
AI Job Copilot - Job Match Model
==========================================================
"""

from datetime import datetime, timezone
from app.extensions import db

class JobMatch(db.Model):
    __tablename__ = "job_matches"

    id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey("users.id"), nullable=True)
    job_id = db.Column(db.String(64), db.ForeignKey("jobs.id"), nullable=False)
    match_score = db.Column(db.Float, nullable=False)
    role_fit = db.Column(db.Float, default=0.0)
    skill_fit = db.Column(db.Float, default=0.0)
    matching_skills = db.Column(db.JSON, default=list)
    missing_skills = db.Column(db.JSON, default=list)
    explanation = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
