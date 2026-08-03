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
    r"https?://(?:[a-zA-Z0-9-]+\.)?linkedin\.com/[^\s,]+"
)

GITHUB_PATTERN = (
    r"https?://(?:www\.)?github\.com/[^\s,]+"
)

def extract_email(text: str) -> str:
    match = re.search(EMAIL_PATTERN, text)
    return match.group(0).strip().rstrip(".,;") if match else ""

def extract_phone(text: str) -> str:
    match = re.search(PHONE_PATTERN, text)
    return match.group(0).strip() if match else ""

def extract_linkedin(text: str) -> str:
    match = re.search(LINKEDIN_PATTERN, text, re.IGNORECASE)
    if match:
        url = match.group(0).strip().rstrip(".,;)")
        return url if url.startswith("http") else f"https://{url}"
    # Fallback to plain linkedin.com/in/...
    alt_match = re.search(r"(?:www\.)?linkedin\.com/(?:in/)?[A-Za-z0-9_-]+", text, re.IGNORECASE)
    if alt_match:
        url = alt_match.group(0).strip().rstrip(".,;)")
        return f"https://{url}"
    return ""

def extract_github(text: str) -> str:
    match = re.search(GITHUB_PATTERN, text, re.IGNORECASE)
    if match:
        url = match.group(0).strip().rstrip(".,;)")
        return url if url.startswith("http") else f"https://{url}"
    # Fallback to plain github.com/...
    alt_match = re.search(r"(?:www\.)?github\.com/[A-Za-z0-9_.-]+", text, re.IGNORECASE)
    if alt_match:
        url = alt_match.group(0).strip().rstrip(".,;)")
        return f"https://{url}"
    return ""

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