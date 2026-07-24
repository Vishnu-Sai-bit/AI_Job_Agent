"""
==========================================================
AI JobAgent - Dashboard Model
Author : Beere Vishnu Sai

Description:
    Dashboard statistics model used by Streamlit,
    FastAPI and Reports.
==========================================================
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any


# ==========================================================
# Dashboard Statistics Model
# ==========================================================

@dataclass
class DashboardStats:
    """
    Dashboard summary for the AI JobAgent.

    Used by:
        • Streamlit Dashboard
        • FastAPI
        • PDF Reports
        • Analytics
    """

    # ------------------------------------------------------
    # Resume Statistics
    # ------------------------------------------------------

    candidate_name: str = ""

    preferred_role: str = ""

    experience_years: float = 0.0

    ats_score: float = 0.0

    # ------------------------------------------------------
    # Skills
    # ------------------------------------------------------

    total_skills: int = 0

    matching_skills: int = 0

    missing_skills: int = 0

    # ------------------------------------------------------
    # Projects & Certifications
    # ------------------------------------------------------

    total_projects: int = 0

    total_certifications: int = 0

    total_education: int = 0

    # ------------------------------------------------------
    # Job Statistics
    # ------------------------------------------------------

    total_jobs_found: int = 0

    total_jobs_returned: int = 0

    average_match_score: float = 0.0

    highest_match_score: float = 0.0

    lowest_match_score: float = 0.0

    # ------------------------------------------------------
    # Provider Statistics
    # ------------------------------------------------------

    providers_used: List[str] = field(default_factory=list)

    provider_job_count: Dict[str, int] = field(default_factory=dict)

    # ------------------------------------------------------
    # Charts
    # ------------------------------------------------------

    skill_distribution: Dict[str, int] = field(default_factory=dict)

    match_distribution: Dict[str, int] = field(default_factory=dict)

    location_distribution: Dict[str, int] = field(default_factory=dict)

    work_type_distribution: Dict[str, int] = field(default_factory=dict)

    # ------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------

    recommended_courses: List[str] = field(default_factory=list)

    recommended_certifications: List[str] = field(default_factory=list)

    suggestions: List[str] = field(default_factory=list)

    # ------------------------------------------------------
    # Status
    # ------------------------------------------------------

    status: str = "success"

    message: str = ""

    # ======================================================
    # Utility Methods
    # ======================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert DashboardStats to dictionary.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Create DashboardStats from dictionary.
        """
        return cls(**data)

    # ------------------------------------------------------

    def add_provider(self, provider: str):

        if provider and provider not in self.providers_used:

            self.providers_used.append(provider)

    # ------------------------------------------------------

    def increment_provider(self, provider: str):

        self.provider_job_count[provider] = (

            self.provider_job_count.get(provider, 0) + 1

        )

    # ------------------------------------------------------

    def add_suggestion(self, suggestion: str):

        if suggestion and suggestion not in self.suggestions:

            self.suggestions.append(suggestion)

    # ------------------------------------------------------

    def add_course(self, course: str):

        if course and course not in self.recommended_courses:

            self.recommended_courses.append(course)

    # ------------------------------------------------------

    def add_certification(self, certification: str):

        if (

            certification

            and certification

            not in self.recommended_certifications

        ):

            self.recommended_certifications.append(

                certification

            )

    # ------------------------------------------------------

    def __str__(self):

        return (

            f"DashboardStats("

            f"ATS={self.ats_score}, "

            f"Jobs={self.total_jobs_returned}, "

            f"Average Match={self.average_match_score})"

        )