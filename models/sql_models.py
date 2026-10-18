"""
==========================================================
AI Job Agent - SQLAlchemy Models (models/sql_models.py)
Stores real job listings, original source requisition IDs,
official URLs, application URLs, and verification metadata.
==========================================================
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def utc_now():
    """Return current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class Job(db.Model):
    """
    Core SQLAlchemy Job model storing verified vacancies from Greenhouse,
    Lever, Workday, and direct enterprise career platforms.
    Internal 'id' primary key selects the database record safely.
    'source_job_id' preserves the authentic external requisition ID.
    STRICT CONSTRAINT: Zero salary fields stored or exposed.
    """
    __tablename__ = "ai_agent_jobs"

    id = db.Column(db.Integer, primary_key=True)

    # Original job source details
    source_platform = db.Column(db.String(50), nullable=False)
    source_job_id = db.Column(db.String(200), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    location = db.Column(db.String(300))

    # Preserve source URLs separately
    original_url = db.Column(db.Text, nullable=False)
    apply_url = db.Column(db.Text)

    # Track source and freshness
    posted_at = db.Column(db.DateTime(timezone=True))
    first_seen_at = db.Column(
        db.DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )
    last_verified_at = db.Column(db.DateTime(timezone=True))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    link_status = db.Column(
        db.String(30), default="unverified", nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint("source_platform", "source_job_id", name="uq_source_platform_job_id"),
    )

    def to_dict(self):
        """Convert job model to dictionary."""
        return {
            "id": self.id,
            "source_platform": self.source_platform,
            "source_job_id": self.source_job_id,
            "company_name": self.company_name,
            "title": self.title,
            "location": self.location,
            "original_url": self.original_url,
            "apply_url": self.apply_url,
            "posted_at": self.posted_at.isoformat() if self.posted_at else None,
            "first_seen_at": self.first_seen_at.isoformat() if self.first_seen_at else None,
            "last_verified_at": self.last_verified_at.isoformat() if self.last_verified_at else None,
            "is_active": self.is_active,
            "link_status": self.link_status,
        }
