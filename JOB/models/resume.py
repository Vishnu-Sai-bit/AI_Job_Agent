from datetime import datetime, timezone
from extensions import db

def utc_now():
    return datetime.now(timezone.utc)

class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)  # pdf, docx
    file_size_bytes = db.Column(db.Integer, default=0)
    
    # Extracted data
    raw_text = db.Column(db.Text, default="")
    parsed_data = db.Column(db.JSON, default=dict)
    
    # Quality & ATS scores
    readability_score = db.Column(db.Float, default=0.0)  # 0 to 100
    completeness_score = db.Column(db.Float, default=0.0) # 0 to 100
    ats_quality_score = db.Column(db.Float, default=0.0)  # overall resume quality
    ats_feedback = db.Column(db.JSON, default=dict)       # detailed breakdown & improvement tips
    
    is_active = db.Column(db.Boolean, default=True)
    uploaded_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    # Relationships
    matches = db.relationship("JobMatch", backref="resume", cascade="all, delete-orphan", lazy="dynamic")

    def __repr__(self):
        return f"<Resume id={self.id} user_id={self.user_id} filename='{self.filename}'>"
