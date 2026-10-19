import os
from flask import Flask
from config import config
from extensions import db, migrate, login_manager
from routes import (
    auth_bp,
    dashboard_bp,
    resume_bp,
    ats_bp,
    jobs_bp,
    applications_bp,
    assistant_bp
)
from tasks.refresh_jobs import ensure_default_sources

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config["default"]))

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register Route Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(ats_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(assistant_bp)

    # Initialize database tables and default job sources
    with app.app_context():
        db.create_all()
        try:
            ensure_default_sources()
        except Exception:
            pass

    return app

if __name__ == "__main__":
    application = create_app()
    port = int(os.getenv("PORT", 5000))
    application.run(host="127.0.0.1", port=port, debug=True)
