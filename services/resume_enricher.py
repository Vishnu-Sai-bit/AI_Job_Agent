"""
==========================================================
AI JobAgent - Resume Enricher
==========================================================
"""

from datetime import datetime
import re
from config import DEFAULT_LOCATIONS


def extract_github(text: str) -> str:
    """
    Extract GitHub profile or repository.
    """

    patterns = [

        r"https?://(?:www\.)?github\.com/[A-Za-z0-9_.-]+",

        r"github\.com/[A-Za-z0-9_.-]+",

    ]

    for pattern in patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            url = match.group(0)

            if not url.startswith("http"):

                url = "https://" + url

            return url

    return ""


def extract_linkedin(text: str) -> str:
    """
    Extract LinkedIn profile.
    """

    patterns = [

        r"https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+",

        r"linkedin\.com/in/[A-Za-z0-9_-]+",

    ]

    for pattern in patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            url = match.group(0)

            if not url.startswith("http"):

                url = "https://" + url

            return url

    return ""

def extract_portfolio(text: str) -> str:
    """
    Extract portfolio/personal website.
    """

    patterns = [

        r"https?://(?:www\.)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/[^\s]*)?",

        r"(?:www\.)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/[^\s]*)?",

    ]

    ignore = (
        "linkedin.com",
        "github.com",
    )

    for pattern in patterns:

        matches = re.findall(pattern, text, re.IGNORECASE)

        for url in matches:

            if any(site in url.lower() for site in ignore):
                continue

            if not url.startswith("http"):

                url = "https://" + url

            return url

    return ""

def extract_kaggle(text: str) -> str:
    """
    Extract Kaggle profile.
    """
    patterns = [
        r"https?://(?:www\.)?kaggle\.com/[A-Za-z0-9_-]+",
        r"kaggle\.com/[A-Za-z0-9_-]+",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            url = match.group(0)
            if not url.startswith("http"):
                url = "https://" + url
            return url
    return ""

def extract_leetcode(text: str) -> str:
    """
    Extract LeetCode profile.
    """
    patterns = [
        r"https?://(?:www\.)?leetcode\.com/[A-Za-z0-9_-]+",
        r"leetcode\.com/[A-Za-z0-9_-]+",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            url = match.group(0)
            if not url.startswith("http"):
                url = "https://" + url
            return url
    return ""

def extract_hackerrank(text: str) -> str:
    """
    Extract HackerRank profile.
    """
    patterns = [
        r"https?://(?:www\.)?hackerrank\.com/[A-Za-z0-9_-]+",
        r"hackerrank\.com/[A-Za-z0-9_-]+",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            url = match.group(0)
            if not url.startswith("http"):
                url = "https://" + url
            return url
    return ""

ROLE_ALIASES = {

    "Data Analyst": [
        "data analyst",
        "business analyst",
        "bi analyst",
        "reporting analyst",
        "analytics engineer",
    ],

    "Data Engineer": [
        "data engineer",
        "etl developer",
        "big data engineer",
    ],

    "Data Scientist": [
        "data scientist",
        "machine learning engineer",
        "ml engineer",
        "ai engineer",
    ],

    "Software Engineer": [
        "software engineer",
        "python developer",
        "backend developer",
        "full stack developer",
    ],

}

def infer_role(text: str) -> str:
    """
    Infer preferred role from resume.
    """

    text = text.lower()

    for role, aliases in ROLE_ALIASES.items():

        for alias in aliases:

            if alias in text:

                return role

    return "Data Analyst"

COMMON_CITIES = [

    "hyderabad",

    "bangalore",

    "bengaluru",

    "chennai",

    "pune",

    "mumbai",

    "delhi",

    "gurugram",

    "noida",

    "tirupati",

]

def infer_location(text: str) -> str:
    """
    Infer preferred job location.
    """

    text = text.lower()

    # If the resume explicitly mentions a preferred location,
    # return it.

    keywords = [

        "preferred location",

        "location preference",

        "preferred work location",

        "looking for jobs in",

        "relocate to",

    ]

    for keyword in keywords:

        if keyword in text:

            for city in DEFAULT_LOCATIONS:

                if city.lower() in text:

                    return city

    # Otherwise, inspect the first part of the resume for default target cities
    intro_text = text[:2000]
    for city in DEFAULT_LOCATIONS:
        if city.lower() in intro_text:
            return city

    # Fallback to the first default location
    return DEFAULT_LOCATIONS[0] if DEFAULT_LOCATIONS else "Bengaluru"

def infer_experience(text: str) -> float:
    """
    Estimate years of experience.
    """

    text = text.lower()

    if "intern" in text:

        return 0.5

    matches = re.findall(

        r"(\d+)\+?\s*years",

        text,

    )

    if matches:

        return float(matches[0])

    return 0.0

def infer_career_level(experience: float) -> str:

    if experience == 0:

        return "Fresher"

    if experience < 2:

        return "Junior"

    if experience < 5:

        return "Mid"

    return "Senior"
