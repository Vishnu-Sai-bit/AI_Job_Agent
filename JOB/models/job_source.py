from datetime import datetime, timezone
from extensions import db

def utc_now():
    return datetime.now(timezone.utc)

class JobSource(db.Model):
    __tablename__ = "job_sources"

    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False, index=True)
    company_key = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    source_config = db.Column(db.JSON, default=dict)
    is_active = db.Column(db.Boolean, default=True, index=True)
    last_sync_at = db.Column(db.DateTime, nullable=True)
    sync_status = db.Column(db.String(50), default="idle")
    sync_error = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    # Relationships
    jobs = db.relationship("Job", backref="source", cascade="all, delete-orphan", lazy="dynamic")

    __table_args__ = (
        db.UniqueConstraint("platform", "company_key", name="uq_source_platform_company"),
    )

    def __repr__(self):
        return f"<JobSource platform='{self.platform}' company='{self.company_key}'>"
