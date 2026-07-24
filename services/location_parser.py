"""
==========================================================
AI JobAgent - Location Parser
Author : Beere Vishnu Sai

Description:
    Parse, normalize and compare locations.
==========================================================
"""

from typing import Dict

from utils import info, exception
from exceptions import LocationParserError


# ==========================================================
# City Aliases
# ==========================================================

CITY_ALIASES = {

    "bangalore": "bengaluru",

    "bombay": "mumbai",

    "madras": "chennai",

    "calcutta": "kolkata",

    "new delhi": "delhi",

    "gurgaon": "gurugram",

}


# ==========================================================
# Normalize Location
# ==========================================================

def normalize_location(location: str) -> str:
    """
    Normalize location.
    """

    if not location:

        return ""

    location = location.lower().strip()

    location = CITY_ALIASES.get(location, location)

    return location.title()


# ==========================================================
# Parse Location
# ==========================================================

def parse_location(location: str) -> Dict[str, str]:
    """
    Parse city/state/country.
    """

    info("Parsing location.")

    try:

        if not location:

            return {

                "city": "",

                "state": "",

                "country": ""

            }

        location = normalize_location(location)

        parts = [

            item.strip()

            for item in location.split(",")

        ]

        if len(parts) == 1:

            return {

                "city": parts[0],

                "state": "",

                "country": ""

            }

        if len(parts) == 2:

            return {

                "city": parts[0],

                "state": parts[1],

                "country": ""

            }

        return {

            "city": parts[0],

            "state": parts[1],

            "country": parts[2]

        }

    except Exception as e:

        exception("Location parsing failed.")

        raise LocationParserError(str(e))


# ==========================================================
# Remote Detection
# ==========================================================

def is_remote(location: str) -> bool:
    """
    Detect remote jobs.
    """

    if not location:

        return False

    location = location.lower()

    remote_keywords = [

        "remote",

        "work from home",

        "wfh",

        "anywhere",

        "hybrid"

    ]

    return any(

        keyword in location

        for keyword in remote_keywords

    )


# ==========================================================
# Match Location
# ==========================================================

def match_location(

    resume_location: str,

    job_location: str

) -> float:
    """
    Calculate location match.
    """

    if is_remote(job_location):

        return 100.0

    if not resume_location:

        return 0.0

    resume = normalize_location(

        resume_location

    ).lower()

    job = normalize_location(

        job_location

    ).lower()

    if resume == job:

        return 100.0

    if resume in job:

        return 90.0

    if job in resume:

        return 90.0

    return 0.0


# ==========================================================
# Display Location
# ==========================================================

def display_location(location: Dict[str, str]) -> str:
    """
    Convert parsed location into string.
    """

    values = [

        location.get("city"),

        location.get("state"),

        location.get("country")

    ]

    values = [

        value

        for value in values

        if value

    ]

    return ", ".join(values)


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    samples = [

        "Bangalore",

        "Bangalore, Karnataka",

        "Hyderabad, Telangana, India",

        "Remote",

        "Work From Home"

    ]

    for sample in samples:

        parsed = parse_location(sample)

        print(parsed)

        print(display_location(parsed))

        print(is_remote(sample))

        print("-" * 50)

    print(

        match_location(

            "Bangalore",

            "Bengaluru"

        )

    )

    print(

        match_location(

            "Hyderabad",

            "Remote"

        )

    )