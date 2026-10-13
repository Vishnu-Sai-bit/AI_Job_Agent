"""
==========================================================
AI Job Copilot - User Model
==========================================================
"""

from datetime import datetime, timezone
import hashlib
from flask_login import UserMixin
from app.extensions import db

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(64), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    full_name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), default="candidate")
    auth_provider = db.Column(db.String(64), default="local")
    google_id = db.Column(db.String(128), nullable=True)
    avatar_url = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def name(self) -> str:
        return self.full_name

    @name.setter
    def name(self, value: str):
        self.full_name = value

    def set_password(self, password: str):
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return self.password_hash == hash_password(password)
