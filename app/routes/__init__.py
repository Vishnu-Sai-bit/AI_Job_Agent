"""
==========================================================
AI Job Copilot - Blueprint Registration Helper
==========================================================
"""

from app.routes.auth import auth_bp
from app.routes.main import main_bp
from app.routes.dashboard import dashboard_bp
from app.routes.jobs import jobs_bp
from app.routes.ai_job_agent import ai_job_agent_bp
from app.routes.resumes import resumes_bp
from app.routes.resume_analysis import resume_analysis_bp
from app.routes.job_matching import job_matching_bp
from app.routes.resume_tailoring import resume_tailoring_bp
from app.routes.applications import applications_bp
from app.routes.interviews import interviews_bp
from app.routes.career_intelligence import career_bp
from app.routes.learning import learning_bp
from app.routes.assistant import assistant_bp
from app.routes.analytics import analytics_bp
from app.routes.automations import automations_bp
from app.routes.notifications import notifications_bp
from app.routes.profile import profile_bp
from app.routes.settings import settings_bp

def register_blueprints(app):
    """Registers all 18 feature blueprints on the Flask application."""
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(ai_job_agent_bp)
    app.register_blueprint(resumes_bp)
    app.register_blueprint(resume_analysis_bp)
    app.register_blueprint(job_matching_bp)
    app.register_blueprint(resume_tailoring_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(interviews_bp)
    app.register_blueprint(career_bp)
    app.register_blueprint(learning_bp)
    app.register_blueprint(assistant_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(automations_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(settings_bp)
