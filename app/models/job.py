"""
==========================================================
AI Job Copilot - Job Model
==========================================================
"""

from datetime import datetime, timezone
from app.extensions import db

class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.String(64), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    salary = db.Column(db.String(128), nullable=True)
    experience = db.Column(db.String(128), nullable=True)
    source = db.Column(db.String(64), default="Aggregator")
    url = db.Column(db.String(512), nullable=True)
    match_score = db.Column(db.Float, default=0.0)
    skills = db.Column(db.JSON, nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
