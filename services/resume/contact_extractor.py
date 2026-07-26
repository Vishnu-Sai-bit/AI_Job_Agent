"""
==========================================================
AI JobAgent - Contact Extractor
Author : Beere Vishnu Sai

Description:
    Rule-based extraction of contact information.
==========================================================
"""

import re


EMAIL_PATTERN = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

PHONE_PATTERN = (
    r"(?:\+91[\s-]?)?"
    r"[6-9]\d{9}"
)

LINKEDIN_PATTERN = (
    r"https?://(?:www\.)?linkedin\.com/[^\s]+"
)

GITHUB_PATTERN = (
    r"https?://(?:www\.)?github\.com/[^\s]+"
)

def extract_email(text: str) -> str:
    match = re.search(EMAIL_PATTERN, text)
    return match.group(0) if match else ""

def extract_phone(text: str) -> str:
    match = re.search(PHONE_PATTERN, text)
    return match.group(0) if match else ""

def extract_linkedin(text: str) -> str:
    match = re.search(LINKEDIN_PATTERN, text)
    return match.group(0) if match else ""

def extract_github(text: str) -> str:
    match = re.search(GITHUB_PATTERN, text)
    return match.group(0) if match else ""

def extract_name(text: str) -> str:
    """
    First non-empty uppercase line.
    """

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if len(line) < 3:
            continue

        if "@" in line:
            continue

        if "http" in line.lower():
            continue

        words = line.split()

        if 2 <= len(words) <= 5:

            return line.title()

    return ""