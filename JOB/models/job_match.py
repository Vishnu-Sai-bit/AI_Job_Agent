from datetime import datetime, timezone
from extensions import db

def utc_now():
    return datetime.now(timezone.utc)

class JobMatch(db.Model):
    __tablename__ = "job_matches"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Explainable match formula result
    match_score = db.Column(db.Float, nullable=False, index=True)
    score_breakdown = db.Column(db.JSON, default=dict)
    skill_match_details = db.Column(db.JSON, default=dict)
    match_explanation = db.Column(db.Text, default="")
    eligibility_flags = db.Column(db.JSON, default=list)
    
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "resume_id", "job_id", name="uq_user_resume_job_match"),
    )

    def __repr__(self):
        return f"<JobMatch user_id={self.user_id} job_id={self.job_id} score={self.match_score}>"


class SavedJob(db.Model):
    __tablename__ = "saved_jobs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    notes = db.Column(db.Text, default="")
    saved_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "job_id", name="uq_user_saved_job"),
    )

    def __repr__(self):
        return f"<SavedJob user_id={self.user_id} job_id={self.job_id}>"
