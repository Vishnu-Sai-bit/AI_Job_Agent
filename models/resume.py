"""
==========================================================
AI JobAgent - Resume Model
Author : Beere Vishnu Sai

Description:
    Resume data model used throughout the application.
==========================================================
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any


# ==========================================================
# Resume Data Model
# ==========================================================

@dataclass
class ResumeData:
    """
    Standard resume object used across the AI JobAgent.

    This object is created by resume_analyzer.py and then
    passed to ATS Calculator, Job Matcher, Search Engine,
    API, and Streamlit UI.
    """

    # ------------------------------------------------------
    # Personal Information
    # ------------------------------------------------------

    name: str = ""

    email: str = ""

    phone: str = ""

    linkedin: str = ""

    github: str = ""

    portfolio: str = ""

    location: str = ""

    # ------------------------------------------------------
    # Career Information
    # ------------------------------------------------------

    career_level: str = ""

    experience_years: float = 0.0

    preferred_role: str = ""

    preferred_location: str = ""

    current_company: str = ""

    current_designation: str = ""

    notice_period: str = ""

    expected_salary: int | None = None

    # ------------------------------------------------------
    # Skills
    # ------------------------------------------------------

    skills: List[str] = field(default_factory=list)

    soft_skills: List[str] = field(default_factory=list)

    tools: List[str] = field(default_factory=list)

    technologies: List[str] = field(default_factory=list)

    # ------------------------------------------------------
    # Education
    # ------------------------------------------------------

    education: List[Dict[str, Any]] = field(default_factory=list)

    # Example
    #
    # [
    #     {
    #         "degree": "...",
    #         "college": "...",
    #         "year": "...",
    #         "cgpa": "..."
    #     }
    # ]

    # ------------------------------------------------------
    # Experience
    # ------------------------------------------------------

    experience: List[Dict[str, Any]] = field(default_factory=list)

    # ------------------------------------------------------
    # Projects
    # ------------------------------------------------------

    projects: List[Dict[str, Any]] = field(default_factory=list)

    # ------------------------------------------------------
    # Certifications
    # ------------------------------------------------------

    certifications: List[Dict[str, Any]] = field(default_factory=list)

    # ------------------------------------------------------
    # Languages
    # ------------------------------------------------------

    languages: List[str] = field(default_factory=list)

    # ------------------------------------------------------
    # ATS
    # ------------------------------------------------------

    ats_score: float = 0.0

    missing_skills: List[str] = field(default_factory=list)

    recommended_courses: List[str] = field(default_factory=list)

    recommended_certifications: List[str] = field(default_factory=list)

    # ------------------------------------------------------
    # Summary
    # ------------------------------------------------------

    career_summary: str = ""

    raw_resume_text: str = ""

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
        Convert ResumeData object to dictionary.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Create ResumeData object from dictionary.
        """
        return cls(**data)

    def total_skills(self) -> int:
        """
        Total technical skills.
        """
        return len(self.skills)

    def total_projects(self) -> int:
        """
        Total projects.
        """
        return len(self.projects)

    def total_certifications(self) -> int:
        """
        Total certifications.
        """
        return len(self.certifications)

    def total_education(self) -> int:
        """
        Total education records.
        """
        return len(self.education)
    
    def total_experience(self) -> int:
        """
        Total experience records.
        """

        return len(self.experience)

    def is_fresher(self) -> bool:
        """
        Check whether candidate is a fresher.
        """
        return self.experience_years <= 0

    def has_contact_details(self) -> bool:
        """
        Check if required contact information exists.
        """
        return bool(self.name and self.email and self.phone)
    
    def has_resume_text(self) -> bool:
        """
        Check whether resume text exists.
        """

        return bool(self.raw_resume_text.strip())
    

    def add_skill(self, skill: str):
        """
        Add a skill if it doesn't already exist.
        """

        if not skill:

            return

        skill = skill.strip()

        if skill.lower() not in {

            s.lower()

            for s in self.skills

        }:

            self.skills.append(skill)

    def add_project(self, project: Dict[str, Any]):
        """
        Add a project.
        """
        if project:
            self.projects.append(project)

    def add_certification(self, certification: Dict[str, Any]):
        """
        Add a certification.
        """
        if certification:
            self.certifications.append(certification)

    def __str__(self) -> str:
        """
        String representation.
        """
        return (
            f"ResumeData("
            f"name='{self.name}', "
            f"role='{self.preferred_role}', "
            f"skills={len(self.skills)}, "
            f"experience={self.experience_years} years)"
        )