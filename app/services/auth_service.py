"""
==========================================================
AI Job Copilot - Auth Service
==========================================================
"""

from typing import Optional
import uuid
from app.extensions import db
from app.models.user import User

class AuthService:
    @staticmethod
    def authenticate(email: str, password: str) -> Optional[User]:
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    def register_user(email: str, password: str, full_name: str, role: str = "candidate") -> User:
        user = User(
            id=f"usr_{uuid.uuid4().hex[:12]}",
            email=email,
            full_name=full_name,
            role=role
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

auth_service = AuthService()
