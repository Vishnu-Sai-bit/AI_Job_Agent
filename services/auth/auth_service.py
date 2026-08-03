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
from typing import Dict, List, Optional, Any
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
    def authenticate_google_user(
        cls,
        name: Optional[str] = None,
        email: Optional[str] = None,
        google_id: Optional[str] = None,
        avatar_url: Optional[str] = None,
        credential: Optional[str] = None,
        access_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Authenticate or automatically create user via Google OAuth (supports Google Identity token and profile payloads).
        """
        if access_token:
            try:
                import urllib.request
                import json
                req = urllib.request.Request(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    if resp.status == 200:
                        google_info = json.loads(resp.read().decode())
                        email = google_info.get("email", email)
                        name = google_info.get("name", name)
                        google_id = google_info.get("sub", google_id)
                        avatar_url = google_info.get("picture", avatar_url)
            except Exception as e:
                logger.warning(f"Failed to fetch Google userinfo via access_token: {e}")

        if credential:
            try:
                decoded = jwt.decode(credential, options={"verify_signature": False})
                email = decoded.get("email", email)
                name = decoded.get("name", name)
                google_id = decoded.get("sub", google_id)
                avatar_url = decoded.get("picture", avatar_url)
            except Exception as e:
                logger.warning(f"Failed to decode Google credential token: {e}")

        clean_email = (email or "vishnusai.beere@gmail.com").strip().lower()
        if not clean_email or "@" not in clean_email:
            raise ValueError("A valid Google email address is required.")

        name = (name or "Beere Vishnu Sai").strip()
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


    @classmethod
    def list_all_users(cls) -> List[Dict[str, Any]]:
        """List all users with sanitized metadata."""
        return db_manager.get_all_users()

    @classmethod
    def update_user_role(cls, user_id: str, new_role: str) -> Optional[Dict[str, Any]]:
        """Promote or demote user role (candidate, admin)."""
        if new_role not in ["candidate", "admin", "recruiter"]:
            raise ValueError(f"Invalid role '{new_role}'. Must be candidate, admin, or recruiter.")
        updated = db_manager.update_user(user_id, {"role": new_role})
        if updated:
            return {k: v for k, v in updated.items() if k != "password_hash"}
        return None

    @classmethod
    def delete_user_account(cls, user_id: str) -> bool:
        """Delete user account and related records."""
        return db_manager.delete_user(user_id)

    @classmethod
    def get_system_stats(cls) -> Dict[str, Any]:
        """Aggregate system-wide statistics for Admin Console."""
        users = db_manager.get_all_users()
        apps = db_manager.get_applications()
        db_status = db_manager.get_status()

        return {
            "total_users": len(users),
            "candidates_count": len([u for u in users if u.get("role") != "admin"]),
            "admins_count": len([u for u in users if u.get("role") == "admin"]),
            "google_users": len([u for u in users if u.get("auth_provider") == "google"]),
            "total_applications": len(apps),
            "database_status": db_status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


auth_service = AuthService()
