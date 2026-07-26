"""
==========================================================
AI JobAgent - ATS Calculator
Author : Beere Vishnu Sai

Description:
    Calculate ATS Score for resumes.

Scoring:
---------
Contact Information : 10%
Skills              : 30%
Education           : 15%
Experience          : 20%
Projects            : 15%
Certifications      : 10%
==========================================================
"""

from typing import List

from models import (
    ResumeData,
    ATSReport,
)

from utils import (
    info,
    exception,
)

from exceptions import ATSCalculationError


# ==========================================================
# Contact Score (10)
# ==========================================================

def contact_score(resume: ResumeData) -> float:
    """
    Calculate contact information score.
    """

    score = 0.0

    if resume.name:
        score += 2

    if resume.email:
        score += 3

    if resume.phone:
        score += 3

    if resume.linkedin:
        score += 1

    if resume.github or resume.portfolio:
        score += 1

    return round(score, 2)


# ==========================================================
# Skills Score (30)
# ==========================================================

def skills_score(resume: ResumeData) -> float:
    """
    Calculate skills score rewarding quality.
    """
    if not resume.skills:
        return 0.0

    high_value_skills = {
        "python", "sql", "power bi", "tableau", "excel", "pandas", "numpy", "git", "fastapi", "azure", 
        "aws", "gcp", "docker", "spark", "pyspark", "databricks", "machine learning", "deep learning", 
        "tensorflow", "pytorch", "etl", "data warehouse", "microsoft fabric", "azure data factory",
        "postgresql", "mongodb", "flask", "django"
    }

    total_count = len(resume.skills)
    high_value_count = sum(1 for skill in resume.skills if skill.lower() in high_value_skills)

    # Base score based on count (max 20 points)
    if total_count >= 12:
        base_score = 20.0
    elif total_count >= 8:
        base_score = 16.0
    elif total_count >= 5:
        base_score = 12.0
    elif total_count >= 3:
        base_score = 8.0
    elif total_count >= 1:
        base_score = 4.0
    else:
        base_score = 0.0

    # Quality bonus (max 10 points) based on high value skills
    if high_value_count >= 8:
        quality_bonus = 10.0
    elif high_value_count >= 5:
        quality_bonus = 8.0
    elif high_value_count >= 3:
        quality_bonus = 6.0
    elif high_value_count >= 1:
        quality_bonus = 3.0
    else:
        quality_bonus = 0.0

    return base_score + quality_bonus


# ==========================================================
# Education Score (15)
# ==========================================================

def education_score(resume: ResumeData) -> float:
    """
    Calculate education score.
    """

    education = len(resume.education)

    if education >= 2:
        return 15.0

    if education == 1:
        return 10.0

    return 0.0


# ==========================================================
# Helper
# ==========================================================

def initialize_report() -> ATSReport:
    """
    Create an empty ATS report.
    """

    return ATSReport()

# ==========================================================
# Experience Score (20)
# ==========================================================

def experience_score(resume: ResumeData) -> float:
    """
    Calculate experience score.
    """

    years = resume.experience_years

    if years >= 8:
        return 20.0

    if years >= 5:
        return 18.0

    if years >= 3:
        return 15.0

    if years >= 2:
        return 12.0

    if years >= 1:
        return 8.0

    if years > 0:
        return 5.0

    return 2.0


# ==========================================================
# Projects Score (15)
# ==========================================================

def projects_score(resume: ResumeData) -> float:
    """
    Calculate project score.
    """

    count = len(resume.projects)

    if count >= 5:
        return 15.0

    if count >= 4:
        return 13.0

    if count >= 3:
        return 11.0

    if count >= 2:
        return 8.0

    if count >= 1:
        return 5.0

    return 0.0


# ==========================================================
# Certification Score (10)
# ==========================================================

def certifications_score(resume: ResumeData) -> float:
    """
    Calculate certification score.
    """

    count = len(resume.certifications)

    if count >= 5:
        return 10.0

    if count >= 3:
        return 8.0

    if count >= 2:
        return 6.0

    if count >= 1:
        return 4.0

    return 0.0


# ==========================================================
# Strengths
# ==========================================================

def build_strengths(resume: ResumeData) -> List[str]:
    """
    Build resume strengths.
    """

    strengths: List[str] = []

    if len(resume.skills) >= 10:
        strengths.append(
            "Strong technical skill set."
        )

    if len(resume.projects) >= 3:
        strengths.append(
            "Good project portfolio."
        )

    if resume.experience_years >= 2:
        strengths.append(
            "Relevant work experience."
        )

    if len(resume.certifications) >= 2:
        strengths.append(
            "Multiple certifications."
        )

    if resume.linkedin:
        strengths.append(
            "LinkedIn profile available."
        )

    if resume.github:
        strengths.append(
            "GitHub profile available."
        )

    return strengths


# ==========================================================
# Weaknesses
# ==========================================================

def build_weaknesses(resume: ResumeData) -> List[str]:
    """
    Build resume weaknesses.
    """

    weaknesses: List[str] = []

    if len(resume.skills) < 5:
        weaknesses.append(
            "Technical skills section is limited."
        )

    if len(resume.projects) == 0:
        weaknesses.append(
            "No projects listed."
        )

    if len(resume.certifications) == 0:
        weaknesses.append(
            "No certifications listed."
        )

    if not resume.linkedin:
        weaknesses.append(
            "LinkedIn profile missing."
        )

    if not resume.github:
        weaknesses.append(
            "GitHub profile missing."
        )

    return weaknesses


# ==========================================================
# Suggestions
# ==========================================================

def build_suggestions(resume: ResumeData) -> List[str]:
    """
    Generate resume improvement suggestions.
    """

    suggestions: List[str] = []

    if resume.total_skills() < 10:
        suggestions.append(
            "Add more technical skills relevant to your target role."
        )

    if resume.total_projects() < 3:
        suggestions.append(
            "Include more real-world projects."
        )

    if resume.total_certifications() < 2:
        suggestions.append(
            "Complete additional industry certifications."
        )

    if not resume.linkedin:
        suggestions.append(
            "Add your LinkedIn profile."
        )

    if not resume.github:
        suggestions.append(
            "Add your GitHub profile."
        )

    return suggestions

# ==========================================================
# Calculate ATS
# ==========================================================

def calculate_ats(resume: ResumeData) -> ATSReport:
    """
    Calculate ATS report for a resume.

    Parameters
    ----------
    resume : ResumeData

    Returns
    -------
    ATSReport
    """

    info("Calculating ATS score...")

    try:

        report = initialize_report()

        # --------------------------------------------------
        # Individual Scores
        # --------------------------------------------------

        report.contact_score = contact_score(resume)

        report.skills_score = skills_score(resume)

        report.education_score = education_score(resume)

        report.experience_score = experience_score(resume)

        report.projects_score = projects_score(resume)

        report.certifications_score = certifications_score(
            resume
        )

        # --------------------------------------------------
        # Overall Score
        # --------------------------------------------------

        report.score = round(

            report.contact_score
            + report.skills_score
            + report.education_score
            + report.experience_score
            + report.projects_score
            + report.certifications_score,

            2

        )

        # Maximum Score = 100
        report.score = min(report.score, 100.0)

        # --------------------------------------------------
        # Statistics
        # --------------------------------------------------

        report.total_skills = resume.total_skills()

        report.total_projects = resume.total_projects()

        report.total_certifications = resume.total_certifications()

        report.total_education = resume.total_education()

        # --------------------------------------------------
        # Analysis
        # --------------------------------------------------

        report.strengths = build_strengths(resume)

        report.weaknesses = build_weaknesses(resume)

        report.suggestions = build_suggestions(resume)

        report.missing_skills = list(
            resume.missing_skills
        )

        report.recommended_courses = list(
            resume.recommended_courses
        )

        report.recommended_certifications = list(
            resume.recommended_certifications
        )

        report.status = "success"

        report.message = (
            "ATS calculation completed successfully."
        )

        info(
            f"ATS Score Calculated: {report.score}"
        )

        info("ATS report generated successfully.")

        return report

    except Exception as e:

        exception("ATS calculation failed.")

        raise ATSCalculationError(str(e))


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    resume = ResumeData()

    resume.name = "Beere Vishnu Sai"

    resume.email = "demo@email.com"

    resume.phone = "9876543210"

    resume.linkedin = (
        "https://linkedin.com/in/demo"
    )

    resume.github = (
        "https://github.com/demo"
    )

    resume.skills = [

        "Python",

        "SQL",

        "Power BI",

        "Excel",

        "Tableau",

        "FastAPI",

        "Docker",

        "Git",

        "Pandas",

        "NumPy"

    ]

    resume.education = [

        {

            "degree": "B.Tech"

        }

    ]

    resume.projects = [

        {},

        {},

        {}

    ]

    resume.certifications = [

        {},

        {}

    ]

    resume.experience_years = 2

    report = calculate_ats(resume)

    print("\nATS REPORT")

    print("=" * 40)

    print(report.to_dict())