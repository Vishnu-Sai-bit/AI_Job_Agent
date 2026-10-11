"""
==========================================================
AI Job Copilot - Application Factory
==========================================================
"""

import os
from pathlib import Path
from flask import Flask
from config import BASE_DIR
from app.extensions import db, login_manager
from app.routes import register_blueprints

def create_app():
    """Application factory for AI Job Copilot full-stack website."""
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    # Configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "ai-job-copilot-secret-key-9182679641")
    
    # Database configuration (SQLite local fallback or PostgreSQL if configured)
    db_path = BASE_DIR / "data" / "job_copilot.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    database_url = os.getenv("DATABASE_URL", f"sqlite:///{db_path}")
    
    # Handle postgres:// vs postgresql:// compatibility if needed
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register all feature blueprints
    register_blueprints(app)

    # Register context processors / custom Jinja filters
    @app.context_processor
    def utility_processor():
        from app.routes.notifications import mock_notifications
        unread_count = sum(1 for n in mock_notifications if not n.get("is_read"))
        return {
            "round": round,
            "min": min,
            "max": max,
            "enumerate": enumerate,
            "len": len,
            "navbar_notifications": mock_notifications,
            "unread_notifications_count": unread_count,
        }

    # Create tables
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.warning(f"Database initialization warning: {e}")

    return app
