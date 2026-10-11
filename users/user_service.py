"""
==========================================================
AI JobAgent - User Lifecycle & Authentication Service
Author : Beere Vishnu Sai
Description:
    Service module managing user accounts, authentication tokens,
    session verification, and user profile management.
==========================================================
"""

from typing import Dict, Any, Optional
from services.auth.auth_service import auth_service
from users.candidate_profile import CandidateProfile

class UserService:
    """
    Dedicated user service managing candidate accounts and authentication.
    """
    def __init__(self):
        self.auth = auth_service

    def register_user(self, email: str, password: str, full_name: str) -> Dict[str, Any]:
        return self.auth.register(email=email, password=password, full_name=full_name)

    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        return self.auth.login(email=email, password=password)

    def create_guest_session(self) -> Dict[str, Any]:
        return self.auth.create_guest_session()

    def get_current_user(self, token: str) -> Optional[Dict[str, Any]]:
        return self.auth.get_current_user(token)

    def is_user_authenticated(self, token: str) -> bool:
        user = self.get_current_user(token)
        return user is not None

    def get_user_profile(self, user_id: str) -> CandidateProfile:
        return CandidateProfile(user_id=user_id)

user_service = UserService()
