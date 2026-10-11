"""
==========================================================
AI Job Copilot - Interview Model
==========================================================
"""

from datetime import datetime, timezone
from app.extensions import db

class Interview(db.Model):
    __tablename__ = "interviews"

    id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey("users.id"), nullable=True)
    role = db.Column(db.String(128), nullable=False)
    company = db.Column(db.String(128), default="Target Enterprise")
    round_type = db.Column(db.String(64), default="Technical Deep Dive")
    question_count = db.Column(db.Integer, default=4)
    questions_data = db.Column(db.JSON, default=list)
    score = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
