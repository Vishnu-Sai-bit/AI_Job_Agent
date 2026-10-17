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

    # ATS-Aware Linking & Verification Fields
    ats_provider = db.Column(db.String(64), default="Company Career Portal", nullable=True)
    external_job_id = db.Column(db.String(128), nullable=True)
    official_job_url = db.Column(db.String(1024), nullable=True)
    apply_url = db.Column(db.String(1024), nullable=True)
    source_url = db.Column(db.String(1024), nullable=True)
    url_verified = db.Column(db.Boolean, default=False)
    last_verified_at = db.Column(db.DateTime, nullable=True)
    job_status = db.Column(db.String(32), default="open")

    @property
    def company_name(self):
        return self.company

    @property
    def job_title(self):
        return self.title


