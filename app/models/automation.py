"""
==========================================================
AI Job Copilot - Automation Model
==========================================================
"""

from datetime import datetime, timezone
from app.extensions import db

class Automation(db.Model):
    __tablename__ = "automations"

    id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey("users.id"), nullable=True)
    daily_digest = db.Column(db.Boolean, default=True)
    min_match_threshold = db.Column(db.Integer, default=75)
    followup_reminder_days = db.Column(db.Integer, default=5)
    email_alerts = db.Column(db.Boolean, default=True)
    preferred_sources = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
