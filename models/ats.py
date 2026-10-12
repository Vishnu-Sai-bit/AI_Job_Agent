"""
==========================================================
AI JobAgent - ATS Report Model
Author : Beere Vishnu Sai

Description:
    ATS score model used across the application.
==========================================================
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any


# ==========================================================
# ATS Report Model
# ==========================================================

@dataclass
class ATSReport:
    """
    Represents the complete ATS evaluation of a resume.
    """

    # ------------------------------------------------------
    # Overall Score
    # ------------------------------------------------------

    score: float = 0.0

    # ------------------------------------------------------
    # Individual Scores
    # ------------------------------------------------------

    contact_score: float = 0.0

    skills_score: float = 0.0

    education_score: float = 0.0

    experience_score: float = 0.0

    projects_score: float = 0.0

    certifications_score: float = 0.0

    formatting_score: float = 0.0

    keyword_score: float = 0.0

    # ------------------------------------------------------
    # Resume Analysis
    # ------------------------------------------------------

    strengths: List[str] = field(default_factory=list)

    weaknesses: List[str] = field(default_factory=list)

    suggestions: List[str] = field(default_factory=list)

    missing_skills: List[str] = field(default_factory=list)

    recommended_courses: List[str] = field(default_factory=list)

    recommended_certifications: List[str] = field(default_factory=list)

    # ------------------------------------------------------
    # Statistics
    # ------------------------------------------------------

    total_skills: int = 0

    total_projects: int = 0

    total_certifications: int = 0

    total_education: int = 0

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
        Convert ATSReport object to dictionary.
        """
        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "ATSReport":

        return cls(**data)

    # ------------------------------------------------------

    def add_strength(self, value: str) -> None:

        if not value:

            return

        value = value.strip()

        if value.lower() not in {

            item.lower()

            for item in self.strengths

        }:

            self.strengths.append(value)

    # ------------------------------------------------------

    def add_weakness(self, value: str) -> None:

        if not value:
    
            return

        value = value.strip()

        if value.lower() not in {

            item.lower()

            for item in self.weaknesses

        }:

            self.weaknesses.append(value)

    # ------------------------------------------------------

    def add_suggestion(self, value: str) -> None:

        if not value:

            return

        value = value.strip()

        if value.lower() not in {

            item.lower()

            for item in self.suggestions

        }:

            self.suggestions.append(value)

    # ------------------------------------------------------

    def add_missing_skill(self, value: str) -> None:

        if not value:

            return

        value = value.strip()

        if value.lower() not in {

            item.lower()

            for item in self.missing_skills

        }:

            self.missing_skills.append(value)

    # ------------------------------------------------------

    def add_course(self, value: str) -> None:

        if not value:

            return

        value = value.strip()

        if value.lower() not in {

            item.lower()

            for item in self.recommended_courses

        }:

            self.recommended_courses.append(value)

    # ------------------------------------------------------

    def add_certification(self, value: str) -> None:

        if not value:

            return

        value = value.strip()

        if value.lower() not in {

            item.lower()

            for item in self.recommended_certifications

        }:

            self.recommended_certifications.append(value)

    # ------------------------------------------------------

    def is_excellent(self) -> bool:

        return self.score >= 90

    # ------------------------------------------------------

    def is_good(self) -> bool:

        return 75 <= self.score < 90

    # ------------------------------------------------------

    def needs_improvement(self) -> bool:

        return self.score < 75

    # ------------------------------------------------------

    def total_suggestions(self) -> int:
        """
        Total suggestions.
        """

        return len(self.suggestions)

    # ------------------------------------------------------

    def has_missing_skills(self) -> bool:
        """
        Check whether missing skills exist.
        """

        return bool(self.missing_skills)
    
    # ------------------------------------------------------

    def __str__(self) -> str:

        return (

            f"ATSReport("

            f"score={self.score}, "

            f"skills={self.skills_score}, "

            f"experience={self.experience_score})"

        )