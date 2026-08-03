"""
==========================================================
AI JobAgent - PostgreSQL & SQL Database Management Layer
Author : Beere Vishnu Sai

Description:
    Provides production-grade PostgreSQL persistence for Users,
    Candidate Profiles, Application CRM, Jobs, and Mock Interview
    evaluations using SQLAlchemy & psycopg2 with automated schema DDL
    and SQLite fallback.
==========================================================
"""

import os
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from utils.logger import logger

# SQLAlchemy imports
try:
    from sqlalchemy import create_engine, Column, String, Text, Float, Integer, DateTime, JSON, inspect
    from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
    from sqlalchemy.exc import SQLAlchemyError
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

Base = declarative_base() if SQLALCHEMY_AVAILABLE else object


if SQLALCHEMY_AVAILABLE:
    class UserModel(Base):
        __tablename__ = "users"
        id = Column(String(64), primary_key=True, index=True)
        email = Column(String(255), unique=True, index=True, nullable=False)
        name = Column(String(255), nullable=True)
        password_hash = Column(String(255), nullable=True)
        role = Column(String(64), default="candidate")
        hub = Column(String(128), default="Hyderabad, India")
        auth_provider = Column(String(64), default="email")
        google_id = Column(String(128), nullable=True)
        avatar_url = Column(String(512), nullable=True)
        created_at = Column(String(64), nullable=True)
        last_login = Column(String(64), nullable=True)
        updated_at = Column(String(64), nullable=True)

    class CandidateProfileModel(Base):
        __tablename__ = "candidate_profiles"
        id = Column(String(64), primary_key=True, index=True)
        user_id = Column(String(64), index=True, nullable=False)
        profile = Column(JSON, nullable=False)
        updated_at = Column(String(64), nullable=True)

    class ApplicationModel(Base):
        __tablename__ = "applications"
        id = Column(String(64), primary_key=True, index=True)
        user_id = Column(String(64), index=True, nullable=True)
        company = Column(String(255), nullable=False)
        title = Column(String(255), nullable=False)
        location = Column(String(255), nullable=True)
        status = Column(String(64), default="Applied")
        match_score = Column(Float, default=0.0)
        salary = Column(String(128), nullable=True)
        applied_date = Column(String(64), nullable=True)
        notes = Column(Text, nullable=True)
        created_at = Column(String(64), nullable=True)
        updated_at = Column(String(64), nullable=True)

    class JobModel(Base):
        __tablename__ = "jobs"
        id = Column(String(64), primary_key=True, index=True)
        title = Column(String(255), nullable=False)
        company = Column(String(255), nullable=False)
        location = Column(String(255), nullable=True)
        salary = Column(String(128), nullable=True)
        match_score = Column(Float, default=0.0)
        skills = Column(JSON, nullable=True)
        description = Column(Text, nullable=True)
        created_at = Column(String(64), nullable=True)

    class MockInterviewModel(Base):
        __tablename__ = "mock_interviews"
        id = Column(String(64), primary_key=True, index=True)
        user_id = Column(String(64), index=True, nullable=True)
        role = Column(String(255), nullable=True)
        overall_score = Column(Float, default=0.0)
        answers = Column(JSON, nullable=True)
        feedback = Column(Text, nullable=True)
        created_at = Column(String(64), nullable=True)


class PostgresManager:
    """
    Production-grade PostgreSQL database manager with auto schema generation
    and session pooling.
    """
    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or os.getenv(
            "POSTGRES_URL",
            os.getenv("DATABASE_URL", "sqlite:///./data/job_copilot.db")
        )
        # Convert postgres:// to postgresql:// for modern SQLAlchemy compatibility
        if self.db_url.startswith("postgres://"):
            self.db_url = self.db_url.replace("postgres://", "postgresql://", 1)

        self.engine = None
        self.SessionLocal = None
        self.is_connected = False
        self.storage_mode = "postgresql" if "postgres" in self.db_url else "sqlite"
        self._init_connection()

    def _init_connection(self):
        """Initialize engine and create tables."""
        if not SQLALCHEMY_AVAILABLE:
            logger.warning("SQLAlchemy is not available.")
            return

        try:
            connect_args = {}
            if "sqlite" in self.db_url:
                connect_args = {"check_same_thread": False}

            self.engine = create_engine(
                self.db_url,
                connect_args=connect_args,
                pool_pre_ping=True
            )
            # Create all tables if not exists
            Base.metadata.create_all(bind=self.engine)
            self.SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))
            self.is_connected = True
            logger.info(f"PostgreSQL/SQL database connected successfully ({self.storage_mode}).")
        except Exception as e:
            logger.warning(f"PostgreSQL connection initialization failed ({e}).")
            self.is_connected = False

    def get_status(self) -> Dict[str, Any]:
        """Get database status."""
        return {
            "storage_mode": self.storage_mode,
            "connected": self.is_connected,
            "engine": "PostgreSQL / SQLAlchemy" if self.is_connected else "Offline",
            "db_url_masked": self.db_url.split("@")[-1] if "@" in self.db_url else "Local SQL"
        }

    # ==========================================================
    # USER CRUD
    # ==========================================================
    def create_user(self, user_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Create or register a user."""
        if not self.is_connected or not self.SessionLocal:
            raise RuntimeError("Database not connected.")

        user_doc.setdefault("id", f"usr_{uuid.uuid4().hex[:12]}")
        user_doc.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        user_doc.setdefault("last_login", datetime.now(timezone.utc).isoformat())

        session = self.SessionLocal()
        try:
            user = UserModel(
                id=user_doc["id"],
                email=user_doc["email"].strip().lower(),
                name=user_doc.get("name"),
                password_hash=user_doc.get("password_hash"),
                role=user_doc.get("role", "candidate"),
                hub=user_doc.get("hub", "Hyderabad, India"),
                auth_provider=user_doc.get("auth_provider", "email"),
                google_id=user_doc.get("google_id"),
                avatar_url=user_doc.get("avatar_url"),
                created_at=user_doc.get("created_at"),
                last_login=user_doc.get("last_login"),
                updated_at=user_doc.get("updated_at")
            )
            session.add(user)
            session.commit()
            return user_doc
        except Exception as e:
            session.rollback()
            raise ValueError(f"Failed to create user: {e}")
        finally:
            session.close()

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find user by email."""
        if not self.is_connected or not self.SessionLocal:
            return None

        clean_email = email.strip().lower()
        session = self.SessionLocal()
        try:
            user = session.query(UserModel).filter(UserModel.email == clean_email).first()
            if not user:
                return None
            return {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "password_hash": user.password_hash,
                "role": user.role,
                "hub": user.hub,
                "auth_provider": user.auth_provider,
                "google_id": user.google_id,
                "avatar_url": user.avatar_url,
                "created_at": user.created_at,
                "last_login": user.last_login
            }
        finally:
            session.close()

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Find user by ID."""
        if not self.is_connected or not self.SessionLocal:
            return None

        session = self.SessionLocal()
        try:
            user = session.query(UserModel).filter(UserModel.id == user_id).first()
            if not user:
                return None
            return {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "password_hash": user.password_hash,
                "role": user.role,
                "hub": user.hub,
                "auth_provider": user.auth_provider,
                "google_id": user.google_id,
                "avatar_url": user.avatar_url,
                "created_at": user.created_at,
                "last_login": user.last_login
            }
        finally:
            session.close()

    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing user record."""
        if not self.is_connected or not self.SessionLocal:
            return None

        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        session = self.SessionLocal()
        try:
            user = session.query(UserModel).filter(UserModel.id == user_id).first()
            if not user:
                return None
            for k, v in updates.items():
                if hasattr(user, k):
                    setattr(user, k, v)
            session.commit()
            return self.get_user_by_id(user_id)
        except Exception as e:
            session.rollback()
            logger.error(f"PostgreSQL update_user error: {e}")
            return None
        finally:
            session.close()

    # ==========================================================
    # APPLICATION CRM OPERATIONS
    # ==========================================================
    def save_application(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save job application."""
        if not self.is_connected or not self.SessionLocal:
            return app_data

        app_data.setdefault("id", f"app_{uuid.uuid4().hex[:8]}")
        app_data.setdefault("created_at", datetime.now(timezone.utc).isoformat())

        session = self.SessionLocal()
        try:
            app_obj = session.query(ApplicationModel).filter(ApplicationModel.id == app_data["id"]).first()
            if app_obj:
                for k, v in app_data.items():
                    if hasattr(app_obj, k):
                        setattr(app_obj, k, v)
            else:
                app_obj = ApplicationModel(
                    id=app_data["id"],
                    user_id=app_data.get("user_id"),
                    company=app_data.get("company", "Company"),
                    title=app_data.get("title", "Job Title"),
                    location=app_data.get("location", "India"),
                    status=app_data.get("status", "Applied"),
                    match_score=float(app_data.get("match_score", 0.0)),
                    salary=app_data.get("salary"),
                    applied_date=app_data.get("applied_date"),
                    notes=app_data.get("notes"),
                    created_at=app_data.get("created_at")
                )
                session.add(app_obj)
            session.commit()
            return app_data
        except Exception as e:
            session.rollback()
            logger.error(f"PostgreSQL save_application error: {e}")
            return app_data
        finally:
            session.close()

    def get_applications(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve applications."""
        if not self.is_connected or not self.SessionLocal:
            return []

        session = self.SessionLocal()
        try:
            query = session.query(ApplicationModel)
            if user_id:
                query = query.filter(ApplicationModel.user_id == user_id)
            results = query.all()
            return [
                {
                    "id": a.id,
                    "user_id": a.user_id,
                    "company": a.company,
                    "title": a.title,
                    "location": a.location,
                    "status": a.status,
                    "match_score": a.match_score,
                    "salary": a.salary,
                    "applied_date": a.applied_date,
                    "notes": a.notes,
                    "created_at": a.created_at
                }
                for a in results
            ]
        finally:
            session.close()


# Singleton instance
postgres_manager = PostgresManager()
