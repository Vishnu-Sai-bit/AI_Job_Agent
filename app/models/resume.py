"""
==========================================================
AI Job Copilot - Resume Model
==========================================================
"""

from datetime import datetime, timezone
from app.extensions import db

class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey("users.id"), nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    ats_score = db.Column(db.Float, default=0.0)
    parsed_data = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
