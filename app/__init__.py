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
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.jinja_env.auto_reload = True

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Respect reverse proxy headers (Render, Vercel, Nginx)
    try:
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    except Exception:
        pass

    # Register all feature blueprints
    register_blueprints(app)

    # Register context processors / custom Jinja filters
    @app.context_processor
    def utility_processor():
        from app.routes.notifications import mock_notifications
        from app.routes.main import get_candidate_context
        unread_count = sum(1 for n in mock_notifications if not n.get("is_read"))
        return {
            "round": round,
            "min": min,
            "max": max,
            "enumerate": enumerate,
            "len": len,
            "navbar_notifications": mock_notifications,
            "unread_notifications_count": unread_count,
            "candidate": get_candidate_context(),
        }

    # Register custom error handlers
    @app.errorhandler(404)
    def handle_404(e):
        from flask import render_template
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def handle_500(e):
        from flask import render_template
        return render_template("errors/500.html"), 500

    # Ensure database tables and columns are up to date
    with app.app_context():
        try:
            db.create_all()
            # Automatic schema healing for existing databases
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            if "users" in inspector.get_table_names():
                existing_cols = {col["name"] for col in inspector.get_columns("users")}
                missing_columns = [
                    ("full_name", "VARCHAR(255) DEFAULT 'Candidate'"),
                    ("role", "VARCHAR(32) DEFAULT 'candidate'"),
                    ("auth_provider", "VARCHAR(64) DEFAULT 'local'"),
                    ("google_id", "VARCHAR(128)"),
                    ("avatar_url", "VARCHAR(512)"),
                ]
                with db.engine.connect() as conn:
                    for col_name, col_type in missing_columns:
                        if col_name not in existing_cols:
                            try:
                                conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                                conn.commit()
                                app.logger.info(f"Auto-migrated database column: users.{col_name}")
                            except Exception as alter_err:
                                app.logger.warning(f"Column auto-migration notice ({col_name}): {alter_err}")
        except Exception as e:
            app.logger.warning(f"Database initialization warning: {e}")

    return app

# Create Flask application instance
flask_app = create_app()

# Wrap with WSGIMiddleware so ASGI runners (such as Render's 'uvicorn app:app') run Flask seamlessly
try:
    from starlette.middleware.wsgi import WSGIMiddleware
    app = WSGIMiddleware(flask_app)
except Exception:
    app = flask_app
