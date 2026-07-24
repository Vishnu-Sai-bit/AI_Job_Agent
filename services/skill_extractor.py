"""
==========================================================
AI JobAgent - Skill Extractor
Author : Beere Vishnu Sai

Description:
    Extract, normalize and compare technical skills.

Used By
-------
- resume_analyzer.py
- job_matcher.py
- ats_calculator.py
- search_jobs.py
==========================================================
"""

import re
from typing import List, Set

from utils import info, exception
from exceptions import SkillExtractionError


# ==========================================================
# Master Skills
# ==========================================================

MASTER_SKILLS: Set[str] = {

    # Programming
    "python", "java", "c", "c++", "c#", "javascript",
    "typescript", "r",

    # Databases
    "sql", "mysql", "postgresql", "oracle",
    "mongodb", "sqlite", "sql server",

    # Analytics
    "excel", "power bi", "tableau",
    "power query", "dax",
    "business intelligence",
    "dashboard",
    "dashboard development",
    "kpi",
    "data analysis",
    "data analytics",
    "data visualization",
    "reporting",

    # ETL
    "etl",
    "etl pipeline",
    "data cleaning",
    "data preprocessing",
    "data warehouse",
    "data warehousing",

    # Python Libraries
    "numpy",
    "pandas",
    "matplotlib",
    "seaborn",
    "plotly",
    "scikit-learn",

    # AI / ML
    "machine learning",
    "deep learning",
    "tensorflow",
    "keras",
    "pytorch",

    # Big Data
    "spark",
    "pyspark",
    "hadoop",
    "databricks",

    # Cloud
    "aws",
    "azure",
    "gcp",
    "microsoft fabric",
    "azure data factory",
    "azure synapse",
    "synapse",

    # Backend
    "fastapi",
    "flask",
    "django",

    # DevOps
    "docker",
    "git",
    "github",

    # Data Engineering
    "data engineer",
    "data analyst",
    "business analyst",
    "bi analyst",
    "reporting analyst",

    # Soft Skills
    "communication",
    "leadership",
    "teamwork",
    "problem solving",
    "critical thinking",
    "time management",
    "analytical thinking"

}


# ==========================================================
# Normalize Text
# ==========================================================

def normalize_text(text: str) -> str:
    """
    Normalize text for skill extraction.
    """

    if not text:
        return ""

    text = text.lower()

    text = re.sub(r"[(){}\[\]]", " ", text)

    text = text.replace("/", " ")

    text = text.replace(",", " ")

    text = text.replace("|", " ")

    text = text.replace("•", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==========================================================
# Extract Skills
# ==========================================================

def extract_skills(text: str) -> List[str]:
    """
    Extract known skills from text.
    """

    info("Extracting skills...")

    try:

        normalized = normalize_text(text)

        skills = []

        for skill in sorted(

            MASTER_SKILLS,

            key=len,

            reverse=True

        ):

            pattern = r"\b" + re.escape(skill) + r"\b"

            if re.search(pattern, normalized):

                skills.append(skill.title())

        skills = sorted(list(set(skills)))

        info(f"{len(skills)} skills extracted.")

        return skills

    except Exception as e:

        exception("Skill extraction failed.")

        raise SkillExtractionError(str(e))


# ==========================================================
# Merge Skills
# ==========================================================

def merge_skills(*skill_lists: List[str]) -> List[str]:
    """
    Merge multiple skill lists.
    """

    merged = set()

    for skill_list in skill_lists:

        for skill in skill_list:

            if skill:

                merged.add(skill.title())

    return sorted(merged)


# ==========================================================
# Skill Matching
# ==========================================================

def match_skills(

    resume_skills: List[str],

    job_skills: List[str]

):
    """
    Compare resume skills with job skills.
    """

    resume = {

        normalize_text(skill)

        for skill in resume_skills

    }

    job = {

        normalize_text(skill)

        for skill in job_skills

    }

    matching = sorted(resume & job)

    missing = sorted(job - resume)

    union = resume | job

    percentage = round(

        (

            len(matching)

            /

            max(len(union), 1)

        )

        * 100,

        2

    )

    return {

        "matching_skills": [

            skill.title()

            for skill in matching

        ],

        "missing_skills": [

            skill.title()

            for skill in missing

        ],

        "match_percentage": percentage

    }


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    sample = """

    Python
    SQL
    Power BI
    Excel
    Tableau
    Pandas
    NumPy
    Docker
    FastAPI
    Git

    """

    skills = extract_skills(sample)

    print(skills)

    result = match_skills(

        skills,

        [

            "Python",

            "SQL",

            "Docker",

            "AWS",

            "Power BI"

        ]

    )

    print(result)