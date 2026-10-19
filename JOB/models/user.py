from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db, login_manager

def utc_now():
    return datetime.now(timezone.utc)

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    # Relationships
    candidate_profile = db.relationship("CandidateProfile", backref="user", uselist=False, cascade="all, delete-orphan")
    resumes = db.relationship("Resume", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    job_matches = db.relationship("JobMatch", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    saved_jobs = db.relationship("SavedJob", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    applications = db.relationship("Application", backref="user", cascade="all, delete-orphan", lazy="dynamic")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_active_resume(self):
        from models.resume import Resume
        return self.resumes.filter_by(is_active=True).first() or self.resumes.order_by(Resume.uploaded_at.desc()).first()

    def __repr__(self):
        return f"<User {self.email}>"


class CandidateProfile(db.Model):
    __tablename__ = "candidate_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = db.Column(db.String(150), default="")
    phone = db.Column(db.String(50), default="")
    location = db.Column(db.String(150), default="")
    headline = db.Column(db.String(255), default="")
    summary = db.Column(db.Text, default="")
    
    # Structured intelligence
    skills = db.Column(db.JSON, default=list)  # list of strings
    experience_years = db.Column(db.Float, default=0.0)
    education = db.Column(db.JSON, default=list)
    projects = db.Column(db.JSON, default=list)
    certifications = db.Column(db.JSON, default=list)

    # User Preferences
    preferred_titles = db.Column(db.JSON, default=list)
    preferred_countries = db.Column(db.JSON, default=list)
    preferred_cities = db.Column(db.JSON, default=list)
    work_modes = db.Column(db.JSON, default=lambda: ["remote", "hybrid", "on-site"])
    min_salary = db.Column(db.Float, nullable=True)
    max_salary = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), default="USD")
    experience_level = db.Column(db.String(50), default="mid")
    employment_types = db.Column(db.JSON, default=lambda: ["full-time"])
    visa_sponsorship_required = db.Column(db.Boolean, default=False)
    
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    def __repr__(self):
        return f"<CandidateProfile user_id={self.user_id} name='{self.full_name}'>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
