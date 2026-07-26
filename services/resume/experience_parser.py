"""
==========================================================
AI JobAgent - Experience Parser
Author : Beere Vishnu Sai

Description:
    Parse and normalize experience information from
    resumes and job descriptions.
==========================================================
"""

import re
from typing import Dict

from utils import info, exception
from exceptions import ExperienceParserError


# ==========================================================
# Experience Keywords
# ==========================================================

KEYWORDS = {

    "fresher": 0.0,
    "entry level": 0.0,
    "entry-level": 0.0,
    "graduate": 0.0,
    "intern": 0.0,
    "internship": 0.0,

    "junior": 1.0,
    "associate": 2.0,

    "mid": 3.0,

    "senior": 5.0,

    "lead": 7.0,

    "manager": 8.0,

    "principal": 10.0

}


# ==========================================================
# Parse Experience
# ==========================================================

def parse_experience(text: str) -> float:
    """
    Convert experience text into years.
    """

    if not text:
        return 0.0

    try:

        text = text.lower().strip()

        # 2-4 Years
        match = re.search(

            r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)",

            text

        )

        if match:

            start = float(match.group(1))
            end = float(match.group(2))

            return round(

                (start + end) / 2,

                1

            )

        # 3+ Years
        match = re.search(

            r"(\d+(?:\.\d+)?)\s*\+",

            text

        )

        if match:

            return float(match.group(1))

        # 5 Years or 5 yrs
        match = re.search(

            r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?|yr)",

            text

        )

        if match:

            return float(match.group(1))

        # Check if text is a single standalone number under 50 (e.g. "3" or "2.5")
        clean_val = text.strip()
        if clean_val.replace(".", "", 1).isdigit():
            val = float(clean_val)
            if val < 50:
                return val

        # Keyword Match
        for keyword, years in KEYWORDS.items():

            if keyword in text:

                return years

        return 0.0

    except Exception as e:

        exception("Experience parsing failed.")

        raise ExperienceParserError(str(e))


# ==========================================================
# Normalize Experience
# ==========================================================

def normalize_experience(text: str) -> Dict:
    """
    Normalize experience text.
    """

    years = parse_experience(text)

    return {

        "text": text,

        "years": years

    }


# ==========================================================
# Match Experience
# ==========================================================

def match_experience(

    resume_years: float,

    required_years: float

) -> float:
    """
    Calculate experience match percentage.
    """

    if required_years <= 0:

        return 100.0

    if resume_years >= required_years:

        return 100.0

    score = (

        resume_years

        /

        required_years

    ) * 100

    return round(

        max(score, 0),

        2

    )


# ==========================================================
# Experience Category
# ==========================================================

def experience_level(years: float) -> str:
    """
    Convert years into experience level.
    """

    if years <= 0:

        return "Fresher"

    if years <= 2:

        return "Junior"

    if years <= 5:

        return "Mid"

    if years <= 8:

        return "Senior"

    return "Lead"


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    samples = [

        "Fresher",

        "Entry Level",

        "2 Years",

        "2-4 Years",

        "3+ Years",

        "Senior Engineer",

        "Lead Developer",

        "Manager"

    ]

    for sample in samples:

        result = normalize_experience(sample)

        print(result)

    print()

    print(

        match_experience(

            2,

            4

        )

    )

    print(

        experience_level(6)

    )