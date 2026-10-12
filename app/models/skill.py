"""
==========================================================
AI Job Copilot - Skill Model
==========================================================
"""

from datetime import datetime, timezone
from app.extensions import db

class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    category = db.Column(db.String(64), default="Technical")
    market_demand = db.Column(db.Float, default=50.0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
