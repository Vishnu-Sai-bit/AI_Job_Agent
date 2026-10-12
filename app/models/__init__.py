"""
==========================================================
AI Job Copilot - Models Module Exports
==========================================================
"""

from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.models.resume import Resume
from app.models.skill import Skill
from app.models.job import Job
from app.models.job_match import JobMatch
from app.models.application import Application
from app.models.interview import Interview
from app.models.learning_plan import LearningPlan
from app.models.notification import Notification
from app.models.automation import Automation

__all__ = [
    "User",
    "CandidateProfile",
    "Resume",
    "Skill",
    "Job",
    "JobMatch",
    "Application",
    "Interview",
    "LearningPlan",
    "Notification",
    "Automation",
]
