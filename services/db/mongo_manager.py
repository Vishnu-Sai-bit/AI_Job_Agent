"""
==========================================================
AI JobAgent - MongoDB & Database Management Layer
Author : Beere Vishnu Sai

Description:
    Provides scalable persistence for Users, Candidate Profiles,
    Application CRM, Jobs, and Mock Interview evaluations.
    Supports MongoDB (Local / Atlas) with graceful fallback
    to JSON local persistence if MongoDB is offline.
==========================================================
"""

import os
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from utils.logger import logger

# Check for pymongo availability
try:
    from pymongo import MongoClient, ASCENDING, DESCENDING
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False


class DatabaseManager:
    """
    Unified Database Manager supporting MongoDB with automated local JSON fallback.
    """
    def __init__(self):
        self.mongo_uri = os.getenv("MONGODB_URI", os.getenv("MONGO_URI", "mongodb://localhost:27017"))
        self.db_name = os.getenv("MONGODB_DB", "ai_job_agent")
        self.client = None
        self.db = None
        self.is_connected = False
        self.storage_mode = "local_json"
        
        # Local JSON data paths for fallback
        self.data_dir = Path(__file__).resolve().parent.parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.users_file = self.data_dir / "users.json"
        self.applications_file = self.data_dir / "applications.json"
        self.profiles_file = self.data_dir / "candidate_profiles.json"
        self.mock_history_file = self.data_dir / "mock_interviews.json"

        self._init_local_files()
        self._init_connection()

    def _init_local_files(self):
        """Ensure local fallback JSON files exist with valid structures."""
        for path in [self.users_file, self.applications_file, self.profiles_file, self.mock_history_file]:
            if not path.exists():
                with open(path, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=2)

    def _init_connection(self):
        """Attempt connection to MongoDB with quick timeout."""
        if not PYMONGO_AVAILABLE:
            logger.warning("pymongo is not installed. Running in local JSON storage mode.")
            self.storage_mode = "local_json"
            self.is_connected = False
            return

        try:
            # Set 2-second server selection timeout to avoid blocking server boot
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=2000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.is_connected = True
            self.storage_mode = "mongodb"
            
            # Setup collections & indexes
            self.db.users.create_index([("email", ASCENDING)], unique=True)
            self.db.applications.create_index([("id", ASCENDING)])
            self.db.applications.create_index([("user_id", ASCENDING)])
            self.db.candidate_profiles.create_index([("user_id", ASCENDING)])
            
            logger.info(f"MongoDB connected successfully to database: {self.db_name}")
        except Exception as e:
            logger.info(f"MongoDB not reachable ({e}). Operating seamlessly in high-performance local JSON mode.")
            self.client = None
            self.db = None
            self.is_connected = False
            self.storage_mode = "local_json"

    def get_status(self) -> Dict[str, Any]:
        """Return current database connection status."""
        return {
            "storage_mode": self.storage_mode,
            "connected": self.is_connected,
            "database_name": self.db_name if self.is_connected else "Local File Store",
            "mongo_available": PYMONGO_AVAILABLE
        }

    # ==========================================================
    # USER OPERATIONS
    # ==========================================================
    def create_user(self, user_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user account."""
        user_doc.setdefault("id", f"usr_{uuid.uuid4().hex[:12]}")
        user_doc.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        user_doc.setdefault("last_login", datetime.now(timezone.utc).isoformat())

        if self.is_connected and self.db is not None:
            try:
                # Remove MongoDB _id if present in return
                doc_copy = dict(user_doc)
                self.db.users.insert_one(doc_copy)
                doc_copy.pop("_id", None)
                return doc_copy
            except Exception as e:
                logger.error(f"MongoDB create_user failed: {e}")

        # Local JSON Fallback
        users = self._read_json(self.users_file)
        if any(u.get("email") == user_doc.get("email") for u in users):
            raise ValueError(f"User with email '{user_doc.get('email')}' already exists.")
        users.append(user_doc)
        self._write_json(self.users_file, users)
        return user_doc

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Retrieve user by email address."""
        if not email:
            return None
        clean_email = email.strip().lower()

        if self.is_connected and self.db is not None:
            try:
                user = self.db.users.find_one({"email": clean_email})
                if user:
                    user.pop("_id", None)
                    return user
            except Exception as e:
                logger.error(f"MongoDB get_user_by_email error: {e}")

        users = self._read_json(self.users_file)
        for u in users:
            if u.get("email", "").strip().lower() == clean_email:
                return u
        return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user by ID."""
        if self.is_connected and self.db is not None:
            try:
                user = self.db.users.find_one({"id": user_id})
                if user:
                    user.pop("_id", None)
                    return user
            except Exception as e:
                logger.error(f"MongoDB get_user_by_id error: {e}")

        users = self._read_json(self.users_file)
        for u in users:
            if u.get("id") == user_id:
                return u
        return None

    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing user."""
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        if self.is_connected and self.db is not None:
            try:
                self.db.users.update_one({"id": user_id}, {"$set": updates})
                return self.get_user_by_id(user_id)
            except Exception as e:
                logger.error(f"MongoDB update_user error: {e}")

        users = self._read_json(self.users_file)
        for i, u in enumerate(users):
            if u.get("id") == user_id:
                users[i].update(updates)
                self._write_json(self.users_file, users)
                return users[i]
        return None

    # ==========================================================
    # CANDIDATE PROFILE OPERATIONS
    # ==========================================================
    def save_candidate_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save or update structured candidate profile."""
        doc = {
            "user_id": user_id,
            "profile": profile_data,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        if self.is_connected and self.db is not None:
            try:
                self.db.candidate_profiles.update_one(
                    {"user_id": user_id},
                    {"$set": doc},
                    upsert=True
                )
                return doc
            except Exception as e:
                logger.error(f"MongoDB save_candidate_profile error: {e}")

        profiles = self._read_json(self.profiles_file)
        updated = False
        for i, p in enumerate(profiles):
            if p.get("user_id") == user_id:
                profiles[i] = doc
                updated = True
                break
        if not updated:
            profiles.append(doc)
        self._write_json(self.profiles_file, profiles)
        return doc

    def get_candidate_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get candidate profile by user ID."""
        if self.is_connected and self.db is not None:
            try:
                prof = self.db.candidate_profiles.find_one({"user_id": user_id})
                if prof:
                    prof.pop("_id", None)
                    return prof.get("profile")
            except Exception as e:
                logger.error(f"MongoDB get_candidate_profile error: {e}")

        profiles = self._read_json(self.profiles_file)
        for p in profiles:
            if p.get("user_id") == user_id:
                return p.get("profile")
        return None

    # ==========================================================
    # APPLICATION CRM OPERATIONS
    # ==========================================================
    def get_applications(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get applications, optionally filtered by user ID."""
        if self.is_connected and self.db is not None:
            try:
                query = {"user_id": user_id} if user_id else {}
                apps = list(self.db.applications.find(query).sort("date_applied", DESCENDING))
                for a in apps:
                    a.pop("_id", None)
                return apps
            except Exception as e:
                logger.error(f"MongoDB get_applications error: {e}")

        apps = self._read_json(self.applications_file)
        if user_id:
            return [a for a in apps if a.get("user_id") == user_id]
        return apps

    def save_application(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or update a job application record."""
        app_id = app_data.get("id") or f"app_{uuid.uuid4().hex[:8]}"
        app_data["id"] = app_id
        app_data.setdefault("date_applied", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        app_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        if self.is_connected and self.db is not None:
            try:
                doc_copy = dict(app_data)
                self.db.applications.update_one(
                    {"id": app_id},
                    {"$set": doc_copy},
                    upsert=True
                )
                doc_copy.pop("_id", None)
                return doc_copy
            except Exception as e:
                logger.error(f"MongoDB save_application error: {e}")

        apps = self._read_json(self.applications_file)
        for i, a in enumerate(apps):
            if a.get("id") == app_id:
                apps[i].update(app_data)
                self._write_json(self.applications_file, apps)
                return apps[i]

        apps.append(app_data)
        self._write_json(self.applications_file, apps)
        return app_data

    def delete_application(self, app_id: str) -> bool:
        """Delete an application record."""
        if self.is_connected and self.db is not None:
            try:
                res = self.db.applications.delete_one({"id": app_id})
                return res.deleted_count > 0
            except Exception as e:
                logger.error(f"MongoDB delete_application error: {e}")

        apps = self._read_json(self.applications_file)
        init_len = len(apps)
        apps = [a for a in apps if a.get("id") != app_id]
        if len(apps) < init_len:
            self._write_json(self.applications_file, apps)
            return True
        return False

    # ==========================================================
    # JSON HELPER METHODS
    # ==========================================================
    def _read_json(self, path: Path) -> List[Dict[str, Any]]:
        if not path.exists():
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_json(self, path: Path, data: Any):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write to {path}: {e}")


# Singleton instance
db_manager = DatabaseManager()
