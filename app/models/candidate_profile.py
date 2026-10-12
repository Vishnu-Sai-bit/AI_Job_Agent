"""
==========================================================
AI Job Copilot - Candidate Profile Model
==========================================================
"""

from datetime import datetime, timezone
from app.extensions import db

class CandidateProfile(db.Model):
    __tablename__ = "candidate_profiles"

    id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey("users.id"), nullable=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(64), nullable=True)
    preferred_role = db.Column(db.String(128), default="Data Analyst")
    preferred_location = db.Column(db.String(128), default="Hyderabad")
    experience_years = db.Column(db.Float, default=0.0)
    skills = db.Column(db.JSON, default=list)
    education = db.Column(db.JSON, default=list)
    projects = db.Column(db.JSON, default=list)
    certifications = db.Column(db.JSON, default=list)
    ats_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
