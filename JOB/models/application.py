from datetime import datetime, timezone
from extensions import db

def utc_now():
    return datetime.now(timezone.utc)

class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Status progression: saved, prepared, applied, interviewing, offer, rejected, withdrawn
    status = db.Column(db.String(50), default="prepared", nullable=False, index=True)
    is_integration_verified = db.Column(db.Boolean, default=False)
    
    submitted_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, default="")
    next_action_at = db.Column(db.DateTime, nullable=True)
    next_action_description = db.Column(db.String(255), default="")
    
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    documents = db.relationship("ApplicationDocument", backref="application", cascade="all, delete-orphan", lazy="dynamic")

    __table_args__ = (
        db.UniqueConstraint("user_id", "job_id", name="uq_user_job_application"),
    )

    def __repr__(self):
        return f"<Application user_id={self.user_id} job_id={self.job_id} status='{self.status}'>"


class ApplicationDocument(db.Model):
    __tablename__ = "application_documents"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    document_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, default="")
    file_path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    def __repr__(self):
        return f"<ApplicationDocument id={self.id} app_id={self.application_id} type='{self.document_type}'>"
