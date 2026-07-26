"""
==========================================================
AI JobAgent - Job Matcher
Author : Beere Vishnu Sai

Description:
    Match ResumeData with JobData.

Responsibilities
----------------
• Role Matching
• Skill Matching
• Experience Matching
• Location Matching
• Salary Matching
• Weighted Score Calculation

Used By
-------
- search_jobs.py
- app.py
- Streamlit UI
==========================================================
"""

from typing import List

from config import MATCH_WEIGHTS
from models import ResumeData, JobData
from utils.vector_store import calculate_semantic_similarity

from utils import (
    info,
    exception,
)

from exceptions import (
    JobMatcherError,
)

from services.resume.skill_extractor import (
    match_skills,
)

from services.resume.experience_parser import (
    match_experience,
)

from services.resume.location_parser import (
    match_location,
)

from services.resume.salary_parser import (
    match_salary,
)

from config import MIN_MATCH_SCORE

# ==========================================================
# Role Aliases
# ==========================================================

ROLE_ALIASES = {
    "data analyst": [
        "business analyst",
        "bi analyst",
        "reporting analyst",
        "analytics engineer",
        "data analytics",
        "data specialist",
        "decision analyst",
    ],

    "data engineer": [
        "etl developer",
        "etl engineer",
        "big data engineer",
        "data warehouse engineer",
    ],

    "business analyst": [
        "functional analyst",
        "process analyst",
        "product analyst",
        "business systems analyst",
    ],
}

# ==========================================================
# Role Match
# ==========================================================

def role_match(
    resume: ResumeData,
    job: JobData,
) -> float:
    """
    Compare preferred role and skills with job title.
    We score both preferred role matches and skill-based matches highly so they both appear at the top.
    """
    job_title = (job.title or "").lower().strip()
    
    # ------------------------------------------------------
    # 1. Preferred Role Match (Base: 100.0)
    # ------------------------------------------------------
    if resume.preferred_role:
        resume_role = resume.preferred_role.lower().strip()
        
        if resume_role == job_title:
            return 100.0
            
        if resume_role in ROLE_ALIASES:
            if any(alias in job_title for alias in ROLE_ALIASES[resume_role]):
                return 98.0
                
        resume_words = set(resume_role.split())
        job_words = set(job_title.split())
        
        if all(word in job_words for word in resume_words):
            return 95.0
            
        overlap = len(resume_words.intersection(job_words))
        if overlap > 0:
            percentage = (overlap / max(len(job_words), 1)) * 90.0
            return round(percentage, 2)
            
    # ------------------------------------------------------
    # 2. Skills-based Job Title Match (Base: 100.0)
    # ------------------------------------------------------
    if resume.skills:
        job_title_lower = f" {job_title} "
        for skill in resume.skills:
            s_lower = skill.lower().strip()
            if len(s_lower) > 2 and (f" {s_lower} " in job_title_lower or job_title.startswith(s_lower) or job_title.endswith(s_lower)):
                return 100.0
                
    return 0.0


# ==========================================================
# Skills Match
# ==========================================================

def skills_match(
    resume: ResumeData,
    job: JobData,
):
    """
    Compare resume skills with job skills.
    """

    return match_skills(

        resume.skills,

        job.skills,

    )


# ==========================================================
# Experience Match
# ==========================================================

def experience_match(
    resume: ResumeData,
    job: JobData,
) -> float:
    """
    Compare experience.
    """

    return match_experience(

        resume.experience_years,

        job.experience_years,

    )


# ==========================================================
# Location Match
# ==========================================================

def location_match_score(
    resume: ResumeData,
    job: JobData,
) -> float:
    """
    Compare preferred location with job location.
    """

    return match_location(

        resume.preferred_location,

        job.location,

    )

# ==========================================================
# Salary Match
# ==========================================================

def salary_match_score(
    resume: ResumeData,
    job: JobData,
) -> float:
    """
    Compare expected salary with job salary.
    """

    if resume.expected_salary is None:
        return 100.0

    return match_salary(

        resume.expected_salary,

        job.min_salary,

    )

# ==========================================================
# Calculate Weighted Score
# ==========================================================

def calculate_weighted_score(
    resume: ResumeData,
    job: JobData,
) -> JobData:
    """
    Calculate weighted job match score.
    """

    info(f"Matching job: {job.title}")

    try:

        # --------------------------------------------------
        # Role Match
        # --------------------------------------------------

        role_score = role_match(
            resume,
            job,
        )

        # --------------------------------------------------
        # Skills Match
        # --------------------------------------------------

        skill_result = skills_match(
            resume,
            job,
        )

        skill_score = skill_result[
            "match_percentage"
        ]

        # --------------------------------------------------
        # Experience Match
        # --------------------------------------------------

        experience_score = experience_match(
            resume,
            job,
        )

        # --------------------------------------------------
        # Location Match
        # --------------------------------------------------

        location_score = location_match_score(
            resume,
            job,
        )

        # --------------------------------------------------
        # Salary Match
        # --------------------------------------------------

        salary_score = salary_match_score(
            resume,
            job,
        )

        # --------------------------------------------------
        # Semantic Match
        # --------------------------------------------------
        semantic_score = calculate_semantic_similarity(resume, job)

        # --------------------------------------------------
        # Weighted Score
        # --------------------------------------------------

        TOTAL_WEIGHT = sum(MATCH_WEIGHTS.values())

        final_score = (
            role_score * MATCH_WEIGHTS["role"] +
            skill_score * MATCH_WEIGHTS["skills"] +
            experience_score * MATCH_WEIGHTS["experience"] +
            location_score * MATCH_WEIGHTS["location"] +
            salary_score * MATCH_WEIGHTS["salary"] +
            semantic_score * MATCH_WEIGHTS.get("semantic", 0.0)
        ) / TOTAL_WEIGHT

        final_score = round(
            final_score,
            2,
        )

        # --------------------------------------------------
        # Update Job Object
        # --------------------------------------------------

        job.role_match = round(
            role_score,
            2,
        )

        job.skill_match = round(
            skill_score,
            2,
        )

        job.experience_match = round(
            experience_score,
            2,
        )

        job.location_match = round(
            location_score,
            2,
        )

        job.salary_match = round(
            salary_score,
            2,
        )

        job.semantic_match = round(
            semantic_score,
            2,
        )

        job.match_score = final_score

        job.matching_skills = skill_result[
            "matching_skills"
        ]

        job.missing_skills = skill_result[
            "missing_skills"
        ]

        info(
            f"{job.title} Match = {final_score}%"
        )

        return job

    except Exception as e:

        exception(
            "Job matching failed."
        )

        raise JobMatcherError(
            str(e)
        )


# ==========================================================
# Match All Jobs
# ==========================================================

def match_jobs(
    resume: ResumeData,
    jobs: List[JobData],
) -> List[JobData]:
    """
    Match resume against all jobs.
    """

    info(
        f"Matching {len(jobs)} jobs."
    )

    matched_jobs = []

    for job in jobs:

        try:

            matched_jobs.append(

                calculate_weighted_score(
                    resume,
                    job,
                )

            )

        except Exception as e:

            exception(f"Skipping job '{job.title}': {e}")

    matched_jobs = [
    
        job

        for job in matched_jobs

        if job is not None

    ]

    matched_jobs.sort(

        key=lambda job: job.match_score,

        reverse=True,

    )

    info(
        "Job ranking completed."
    )

    if matched_jobs:
        info(
            f"Top Match: "
            f"{matched_jobs[0].title} "
            f"({matched_jobs[0].match_score}%)"
        )

    return matched_jobs

# ==========================================================
# Filter Best Matches
# ==========================================================

def filter_best_matches(
    jobs: List[JobData],
    minimum_score: float = MIN_MATCH_SCORE,
) -> List[JobData]:
    """
    Filter jobs above the minimum match score.
    """

    return [

        job

        for job in jobs

        if job.match_score >= minimum_score

    ]


# ==========================================================
# Top Matches
# ==========================================================

def top_matches(
    jobs: List[JobData],
    limit: int = 10,
) -> List[JobData]:
    """
    Return top matching jobs.
    """

    return sorted(

        jobs,

        key=lambda job: job.match_score,

        reverse=True,

    )[:limit]


# ==========================================================
# Match Summary
# ==========================================================

def match_summary(
    jobs: List[JobData],
) -> dict:
    """
    Return matching statistics.
    """

    if not jobs:

        return {

            "total_jobs": 0,

            "average_score": 0,

            "highest_score": 0,

            "lowest_score": 0,

        }

    scores = [

        job.match_score

        for job in jobs

    ]

    return {

        "total_jobs": len(jobs),

        "average_score": round(

            sum(scores) / len(scores),

            2,

        ),

        "highest_score": max(scores),

        "lowest_score": min(scores),

    }


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    resume = ResumeData(

        name="Beere Vishnu Sai",

        preferred_role="Data Analyst",

        preferred_location="Hyderabad",

        experience_years=2,

        skills=[

            "Python",

            "SQL",

            "Power BI",

            "Excel",

            "Tableau",

            "Pandas",

            "NumPy",

        ],

        expected_salary=600000,

    )

    jobs = [

        JobData(

            title="Data Analyst",

            company="IBM",

            location="Hyderabad",

            experience_years=2,

            min_salary=700000,

            skills=[

                "Python",

                "SQL",

                "Power BI",

                "Excel",

            ],

        ),

        JobData(

            title="Business Analyst",

            company="Accenture",

            location="Bengaluru",

            experience_years=1,

            min_salary=550000,

            skills=[

                "SQL",

                "Excel",

                "Tableau",

            ],

        ),

    ]

    matched = match_jobs(

        resume,

        jobs,

    )

    print("\n" + "=" * 60)

    print(" AI JobAgent - Job Matcher ")

    print("=" * 60)

    for job in matched:

        print(f"\nCompany : {job.company}")

        print(f"Role    : {job.title}")

        print(f"Score   : {job.match_score}%")

        print(f"Matched : {job.matching_skills}")

        print(f"Missing : {job.missing_skills}")

    print("\nSummary")

    print(match_summary(matched))