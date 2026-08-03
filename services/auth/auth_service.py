"""
==========================================================
AI JobAgent - User Authentication & JWT Service
Author : Beere Vishnu Sai

Description:
    Provides secure user authentication, password hashing (PBKDF2-HMAC-SHA256),
    JWT session token generation, validation, and user profile management.
==========================================================
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any
import jwt
from services.db.mongo_manager import db_manager
from utils.logger import logger

JWT_SECRET = os.getenv("JWT_SECRET", "ai_job_agent_jwt_secret_key_2026_super_secure_vault")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 7


class AuthService:
    """
    Handles user registration, login, password security, and JWT lifecycle.
    """

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> str:
        """
        Hash password securely with PBKDF2 HMAC-SHA256 and a random salt.
        Returns 'salt$hash'.
        """
        if not salt:
            salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}${key.hex()}"

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """
        Verify password against stored salt$hash.
        """
        try:
            salt, _ = stored_hash.split("$", 1)
            recalculated = AuthService.hash_password(password, salt=salt)
            return secrets.compare_digest(recalculated, stored_hash)
        except Exception:
            return False

    @staticmethod
    def generate_token(user_id: str, email: str, name: str) -> str:
        """
        Generate a signed JWT token valid for 7 days.
        """
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "email": email,
            "name": name,
            "iat": now,
            "exp": now + timedelta(days=JWT_EXPIRATION_DAYS)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and verify JWT token. Returns payload or None if invalid/expired.
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            logger.debug(f"JWT Verification failed: {e}")
            return None

    @classmethod
    def register_user(cls, name: str, email: str, password: str) -> Dict[str, Any]:
        """
        Register a new user account.
        """
        clean_email = email.strip().lower()
        if not clean_email or "@" not in clean_email:
            raise ValueError("A valid email address is required.")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")

        existing = db_manager.get_user_by_email(clean_email)
        if existing:
            raise ValueError(f"An account with email '{clean_email}' already exists.")

        pwd_hash = cls.hash_password(password)
        user_doc = {
            "name": name.strip() or "Candidate",
            "email": clean_email,
            "password_hash": pwd_hash,
            "role": "candidate",
            "hub": "Hyderabad, India"
        }

        created = db_manager.create_user(user_doc)
        token = cls.generate_token(created["id"], created["email"], created["name"])

        # Strip password_hash before returning
        safe_user = {k: v for k, v in created.items() if k != "password_hash"}
        return {
            "success": True,
            "token": token,
            "user": safe_user,
            "message": "Account created successfully."
        }

    @classmethod
    def login_user(cls, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with email and password.
        """
        clean_email = email.strip().lower()
        user = db_manager.get_user_by_email(clean_email)
        if not user:
            raise ValueError("Invalid email or password.")

        if not cls.verify_password(password, user.get("password_hash", "")):
            raise ValueError("Invalid email or password.")

        db_manager.update_user(user["id"], {"last_login": datetime.utcnow().isoformat()})
        token = cls.generate_token(user["id"], user["email"], user.get("name", "Candidate"))
        safe_user = {k: v for k, v in user.items() if k != "password_hash"}

        return {
            "success": True,
            "token": token,
            "user": safe_user,
            "message": "Login successful."
        }

    @classmethod
    def create_guest_session(cls) -> Dict[str, Any]:
        """
        Create a fast, frictionless guest session for instant testing.
        """
        guest_email = f"guest_{secrets.token_hex(4)}@jobagent.ai"
        user_doc = {
            "name": "Guest Candidate",
            "email": guest_email,
            "password_hash": cls.hash_password(secrets.token_urlsafe(16)),
            "role": "guest",
            "hub": "Remote / Hybrid"
        }
        created = db_manager.create_user(user_doc)
        token = cls.generate_token(created["id"], created["email"], created["name"])
        safe_user = {k: v for k, v in created.items() if k != "password_hash"}
        return {
            "success": True,
            "token": token,
            "user": safe_user,
            "message": "Guest session activated."
        }

    @classmethod
    def authenticate_google_user(cls, name: str, email: str, google_id: Optional[str] = None, avatar_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Authenticate or automatically create user via Google OAuth.
        """
        clean_email = email.strip().lower()
        if not clean_email or "@" not in clean_email:
            raise ValueError("A valid Google email address is required.")

        user = db_manager.get_user_by_email(clean_email)
        now_iso = datetime.now(timezone.utc).isoformat()

        if user:
            # Update existing user profile with Google details
            update_data = {
                "last_login": now_iso,
                "auth_provider": "google",
                "google_id": google_id or user.get("google_id", f"goog_{secrets.token_hex(6)}"),
            }
            if avatar_url:
                update_data["avatar_url"] = avatar_url
            if name and (not user.get("name") or user.get("name") == "Candidate"):
                update_data["name"] = name.strip()

            db_manager.update_user(user["id"], update_data)
            user = db_manager.get_user_by_id(user["id"]) or user
            token = cls.generate_token(user["id"], user["email"], user.get("name", name))
            safe_user = {k: v for k, v in user.items() if k != "password_hash"}
            return {
                "success": True,
                "token": token,
                "user": safe_user,
                "message": f"Welcome back, {safe_user.get('name', 'Candidate')}! Signed in with Google."
            }
        else:
            # Create new user registered via Google
            user_doc = {
                "name": name.strip() or "Google Candidate",
                "email": clean_email,
                "password_hash": cls.hash_password(secrets.token_urlsafe(24)),
                "role": "candidate",
                "auth_provider": "google",
                "google_id": google_id or f"goog_{secrets.token_hex(6)}",
                "avatar_url": avatar_url or "",
                "hub": "Hyderabad, India",
                "created_at": now_iso,
                "last_login": now_iso
            }
            created = db_manager.create_user(user_doc)
            token = cls.generate_token(created["id"], created["email"], created["name"])
            safe_user = {k: v for k, v in created.items() if k != "password_hash"}
            return {
                "success": True,
                "token": token,
                "user": safe_user,
                "message": f"Account created successfully with Google. Welcome, {safe_user.get('name')}!"
            }


auth_service = AuthService()
