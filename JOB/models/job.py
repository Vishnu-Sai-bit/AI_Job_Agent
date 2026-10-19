from datetime import datetime, timezone
from extensions import db

def utc_now():
    return datetime.now(timezone.utc)

class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey("job_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Source Identifiers (Core grounding requirement)
    source_platform = db.Column(db.String(50), nullable=False, index=True)
    source_company_key = db.Column(db.String(100), nullable=False)
    source_job_id = db.Column(db.String(150), nullable=False, index=True)
    
    # Job Information
    title = db.Column(db.String(255), nullable=False, index=True)
    company = db.Column(db.String(150), nullable=False, index=True)
    department = db.Column(db.String(150), default="")
    location = db.Column(db.String(255), default="", index=True)
    country = db.Column(db.String(100), default="")
    city = db.Column(db.String(100), default="")
    work_mode = db.Column(db.String(50), default="on-site")
    employment_type = db.Column(db.String(50), default="full-time")
    experience_level = db.Column(db.String(50), default="any")
    
    # Compensation
    salary_min = db.Column(db.Float, nullable=True)
    salary_max = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), default="USD")
    
    # Job Description & Requirements
    description = db.Column(db.Text, default="")
    raw_description = db.Column(db.Text, default="")
    required_skills = db.Column(db.JSON, default=list)
    preferred_skills = db.Column(db.JSON, default=list)
    
    # Direct Official Links (Core system requirement)
    original_url = db.Column(db.String(1000), nullable=False)
    apply_url = db.Column(db.String(1000), nullable=False)
    canonical_url = db.Column(db.String(1000), nullable=True)
    
    # Timestamps & Status
    published_at = db.Column(db.DateTime, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    last_verified_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    status = db.Column(db.String(50), default="active", index=True)
    
    source_metadata = db.Column(db.JSON, default=dict)

    # Relationships
    matches = db.relationship("JobMatch", backref="job", cascade="all, delete-orphan", lazy="dynamic")
    saved_by = db.relationship("SavedJob", backref="job", cascade="all, delete-orphan", lazy="dynamic")
    applications = db.relationship("Application", backref="job", cascade="all, delete-orphan", lazy="dynamic")
    verification_logs = db.relationship("VerificationLog", backref="job", cascade="all, delete-orphan", lazy="dynamic")

    __table_args__ = (
        db.UniqueConstraint("source_id", "source_job_id", name="uq_source_job"),
    )

    def __repr__(self):
        return f"<Job id={self.id} title='{self.title}' company='{self.company}' source={self.source_platform}>"


class VerificationLog(db.Model):
    __tablename__ = "verification_logs"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    checked_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    result = db.Column(db.String(50), nullable=False)
    http_status = db.Column(db.Integer, nullable=True)
    destination_url = db.Column(db.String(1000), nullable=True)
    details = db.Column(db.Text, default="")

    def __repr__(self):
        return f"<VerificationLog job_id={self.job_id} result={self.result} status={self.http_status}>"
