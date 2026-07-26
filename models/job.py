"""
==========================================================
AI JobAgent - Job Model
Author : Beere Vishnu Sai

Description:
    Standard job model used throughout the application.
==========================================================
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any


# ==========================================================
# Job Data Model
# ==========================================================

@dataclass
class JobData:
    """
    Standard job object shared across all providers,
    search engine, matcher, API and frontend.
    """

    # ------------------------------------------------------
    # Provider Information
    # ------------------------------------------------------

    provider: str = ""

    provider_id: str = ""

    # ------------------------------------------------------
    # Company Information
    # ------------------------------------------------------

    company: str = ""

    company_logo: str = ""

    company_website: str = ""

    # ------------------------------------------------------
    # Job Information
    # ------------------------------------------------------

    title: str = ""

    category: str = ""

    description: str = ""

    employment_type: str = ""

    work_type: str = ""

    # ------------------------------------------------------
    # Location
    # ------------------------------------------------------

    location: str = ""

    city: str = ""

    state: str = ""

    country: str = ""

    remote: bool = False

    featured: bool = False

    # ------------------------------------------------------
    # Salary
    # ------------------------------------------------------

    salary: str = "Not Mentioned"

    currency: str = ""

    min_salary: int | None = None

    max_salary: int | None = None

    # ------------------------------------------------------
    # Experience
    # ------------------------------------------------------

    experience: str = ""

    experience_years: float = 0.0

    # ------------------------------------------------------
    # Skills
    # ------------------------------------------------------

    skills: List[str] = field(default_factory=list)

    # ------------------------------------------------------
    # Dates
    # ------------------------------------------------------

    publication_date: str = ""

    posted: str = ""

    expiry_date: str = ""

    # ------------------------------------------------------
    # URLs
    # ------------------------------------------------------

    apply_url: str = ""

    company_url: str = ""

    # ------------------------------------------------------
    # Matching
    # ------------------------------------------------------

    role_match: float = 0.0

    skill_match: float = 0.0

    experience_match: float = 0.0

    location_match: float = 0.0

    salary_match: float = 0.0

    semantic_match: float = 0.0

    match_score: float = 0.0

    matching_skills: List[str] = field(default_factory=list)

    missing_skills: List[str] = field(default_factory=list)

    # ------------------------------------------------------
    # Status
    # ------------------------------------------------------

    active: bool = True

    # ======================================================
    # Utility Methods
    # ======================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert JobData to dictionary.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Create JobData from dictionary.
        """
        return cls(**data)

    # ------------------------------------------------------

    def has_salary(self) -> bool:
        return (
            self.min_salary is not None
            or
            self.max_salary is not None
        )

    # ------------------------------------------------------

    def is_remote(self) -> bool:
        return self.remote

    # ------------------------------------------------------

    def has_skills(self) -> bool:
        return len(self.skills) > 0

    # ------------------------------------------------------

    def total_skills(self) -> int:
        return len(self.skills)

    # ------------------------------------------------------

    def add_skill(self, skill: str):

        if not skill:

            return

        skill = skill.strip()

        if skill.lower() not in {

            s.lower()

            for s in self.skills

        }:

            self.skills.append(skill)
        
    # ------------------------------------------------------

    def add_matching_skill(self, skill: str):

        if not skill:

            return

        skill = skill.strip()

        if skill.lower() not in {

            s.lower()

            for s in self.matching_skills

        }:

            self.matching_skills.append(skill)

    # ------------------------------------------------------

    def add_missing_skill(self, skill: str):

        if not skill:

            return

        skill = skill.strip()

        if skill.lower() not in {

            s.lower()

            for s in self.missing_skills

        }:

            self.missing_skills.append(skill)

    # ------------------------------------------------------

    def set_match_score(
        self,
        role: float,
        skill: float,
        experience: float,
        location: float,
        salary: float = 0.0,
        semantic: float = 0.0,
        final_score: float | None = None,
    ):
        """
        Update all matching scores.
        """

        self.role_match = role
        self.skill_match = skill
        self.experience_match = experience
        self.location_match = location
        self.salary_match = salary
        self.semantic_match = semantic

        if final_score is not None:

            self.match_score = round(
                final_score,
                2,
            )

        else:

            self.match_score = round(

                role
                + skill
                + experience
                + location
                + salary
                + semantic,

                2

            )

    # ------------------------------------------------------

    def get_match_reason(self) -> str:
        """
        Returns a human-readable explanation of why the job matched.
        """
        matched_str = " | ".join(f"{s} ✔" for s in self.matching_skills) if self.matching_skills else "None"
        missing_str = ", ".join(self.missing_skills) if self.missing_skills else "None"
        return f"Matched Skills: {matched_str} | Missing Skills: {missing_str}"

    def __str__(self):

        return (

            f"JobData("

            f"title='{self.title}', "

            f"company='{self.company}', "

            f"provider='{self.provider}', "

            f"match={self.match_score}%)"

        )