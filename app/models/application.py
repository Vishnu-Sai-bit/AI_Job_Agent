"""
==========================================================
AI Job Copilot - Application Model
==========================================================
"""

from datetime import datetime, timezone
from app.extensions import db

class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey("users.id"), nullable=True)
    job_id = db.Column(db.String(64), nullable=True)
    company = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    stage = db.Column(db.String(64), default="saved")
    salary = db.Column(db.String(128), nullable=True)
    applied_date = db.Column(db.String(64), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
