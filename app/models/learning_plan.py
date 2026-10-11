"""
==========================================================
AI Job Copilot - Learning Plan Model
==========================================================
"""

from datetime import datetime, timezone
from app.extensions import db

class LearningPlan(db.Model):
    __tablename__ = "learning_plans"

    id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey("users.id"), nullable=True)
    target_role = db.Column(db.String(128), nullable=False)
    skill_gaps = db.Column(db.JSON, default=list)
    roadmaps_data = db.Column(db.JSON, default=list)
    completed_milestones = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
