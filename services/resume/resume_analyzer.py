"""
==========================================================
AI JobAgent - Resume Analyzer
Author : Beere Vishnu Sai

Description:
    Analyze resume using Ollama and convert the
    response into a ResumeData object.

Flow
----
Resume Text
      ↓
Ollama
      ↓
JSON Response
      ↓
ResumeData
      ↓
ATS Score
==========================================================
"""

import json
import time
from typing import Dict, Any

import requests

from config import (
    MAX_RETRIES,
)

from models import ResumeData

from utils import (
    info,
    warning,
    exception,
    call_llm,
)

from exceptions import (
    ResumeAnalyzerError,
    OllamaConnectionError,
    InvalidAIResponseError,
)

from services.resume.resume_enricher import (
    extract_github,
    extract_linkedin,
    extract_portfolio,
    infer_role,
    infer_location,
    infer_experience,
    infer_career_level,
)

# ==========================================================
# AI Prompt
# ==========================================================

PROMPT = """
You are an expert ATS Resume Analyzer.

Your job is to extract information from the resume.

IMPORTANT RULES:

12. Infer preferred_role from the Profile Summary, Career Objective,
or Targeting statement.

Example:

"Targeting Data Analyst roles"
→ preferred_role = "Data Analyst"

13. Infer preferred_location from the resume.
If no preferred location is mentioned,
use the current city.

14. Estimate experience_years using internships,
full-time experience and project duration.

15. Always extract GitHub, LinkedIn and Portfolio URLs if present.

16. If GitHub or LinkedIn is written without https://,
still return the value.

Estimate experience_years.

Examples

Jan 2025 – Jan 2026 = 1

Oct 2025 – Mar 2026 = 0.5

No experience = 0

1. Return ONLY valid JSON.
2. Do NOT use markdown.
3. Do NOT use ```json.
4. Do NOT explain anything.
5. Do NOT write notes.
6. Do NOT create new keys.
7. Use ONLY the keys shown below.
8. Every key MUST exist.
9. If information is unavailable:
   - string -> ""
   - list -> []
   - number -> 0
10. The response MUST begin with { and end with }.
11. The response MUST be directly parsable using Python json.loads().

Return EXACTLY this JSON schema:

{
    "name":"",
    "email":"",
    "phone":"",
    "linkedin":"",
    "github":"",
    "portfolio":"",
    "location":"",
    "career_level":"",
    "experience_years":0,
    "preferred_role":"",
    "preferred_location":"",
    "skills":[],
    "soft_skills":[],
    "education":[],
    "experience":[],
    "projects":[],
    "certifications":[],
    "languages":[],
    "career_summary":""
}

Resume:

"""

# ==========================================================
# Ollama Request
# ==========================================================

def call_ollama(
    resume_text: str
) -> str:
    """
    Send resume to LLM using unified helper.
    """
    info("Sending request to LLM analyzer.")
    try:
        return call_llm(PROMPT + resume_text, json_format=True)
    except Exception as e:
        exception("LLM analyzer request failed.")
        raise ResumeAnalyzerError(str(e))
    
# ==========================================================
# Retry Logic
# ==========================================================

def request_with_retry(
    resume_text: str
) -> str:
    """
    Retry Ollama request.
    """
    last_error = "No attempts made."
    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):
        try:
            info(
                f"Ollama Attempt {attempt}"
            )
            return call_ollama(
                resume_text
            )
        except Exception as e:
            last_error = str(e)
            warning(
                f"Retry {attempt} failed: {e}"
            )
            if attempt < MAX_RETRIES:
                time.sleep(2)

    raise ResumeAnalyzerError(
        f"Maximum retry limit reached. Last error: {last_error}"
    )

# ==========================================================
# JSON Cleaner
# ==========================================================

def clean_json(ai_response: str) -> str:
    """
    Clean JSON returned by Ollama.

    Removes markdown code blocks and extra spaces.
    """

    if not ai_response:

        raise InvalidAIResponseError(
            "Empty response received from AI."
        )

    info("Cleaning AI response.")

    cleaned = ai_response.strip()

    # Remove markdown code blocks
    cleaned = cleaned.replace("```json", "")
    cleaned = cleaned.replace("```JSON", "")
    cleaned = cleaned.replace("```", "")

    cleaned = cleaned.strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1:
        raise InvalidAIResponseError(
            "No JSON object found in AI response."
        )

    cleaned = cleaned[start:end + 1]

    return cleaned


# ==========================================================
# JSON Parser
# ==========================================================

def parse_json(ai_response: str) -> Dict[str, Any]:
    """
    Convert AI response into Python dictionary.
    """

    try:

        cleaned = clean_json(ai_response)

        data = json.loads(cleaned)

        if not isinstance(data, dict):

            raise InvalidAIResponseError(
                "AI response is not a JSON object."
            )

        info("AI JSON parsed successfully.")

        return data

    except json.JSONDecodeError as e:

        exception("Invalid JSON returned by AI.")

        print("\n========== AI RESPONSE ==========")
        print(cleaned)
        print("=================================\n")

        raise InvalidAIResponseError(str(e))

    except Exception as e:

        exception("Unable to parse AI response.")

        raise InvalidAIResponseError(str(e))


# ==========================================================
# Safe Getter
# ==========================================================

def safe_get(
    data: Dict[str, Any],
    key: str,
    default=None
):
    """
    Safely retrieve a value from a dictionary.
    """

    value = data.get(key, default)

    if value is None:

        return default

    return value


# ==========================================================
# Ensure List
# ==========================================================

def ensure_list(value) -> list:
    """
    Ensure the value is always a list.
    """

    if value is None:

        return []

    if isinstance(value, list):

        return value

    if isinstance(value, str):

        return [

            item.strip()

            for item in value.split(",")

            if item.strip()

        ]

    return []


# ==========================================================
# Ensure Float
# ==========================================================

def ensure_float(value) -> float:
    """
    Convert value to float safely.
    """

    try:

        return float(value)

    except Exception:

        return 0.0


# ==========================================================
# Ensure String
# ==========================================================

def ensure_string(value) -> str:
    """
    Convert value to string safely.
    """

    if value is None:

        return ""

    return str(value).strip()


# ==========================================================
# Validate AI Schema
# ==========================================================

REQUIRED_FIELDS = [
    "name",
    "email",
    "phone",
    "linkedin",
    "github",
    "portfolio",
    "location",
    "career_level",
    "experience_years",
    "preferred_role",
    "preferred_location",
    "skills",
    "soft_skills",
    "education",
    "experience",
    "projects",
    "certifications",
    "languages",
    "career_summary",
]


def validate_schema(
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Ensure all required fields exist.
    """

    info("Validating AI schema.")

    list_fields = {
        "skills",
        "soft_skills",
        "education",
        "experience",
        "projects",
        "certifications",
        "languages",
    }

    for field in REQUIRED_FIELDS:

        if field not in data:

            warning(f"Missing field: {field}")

            if field in list_fields:

                data[field] = []

            elif field == "experience_years":

                data[field] = 0

            else:

                data[field] = ""

    return data
# ==========================================================
# Service Imports
# ==========================================================

from services.resume.skill_extractor import (
    extract_skills,
)

from services.resume.location_parser import (
    normalize_location,
)

from services.ats.ats_calculator import (
    calculate_ats,
)


# ==========================================================
# Build ResumeData
# ==========================================================

def build_resume_data(
    data: Dict[str, Any],
    resume_text: str
) -> ResumeData:
    """
    Convert AI JSON into ResumeData.
    """

    info("Building ResumeData object.")

    resume = ResumeData()

    # ------------------------------------------------------
    # Personal Information
    # ------------------------------------------------------

    resume.name = ensure_string(
        safe_get(data, "name")
    )

    resume.email = ensure_string(safe_get(data, "email")).strip()
    if not resume.email or "@" not in resume.email:
        resume.email = extract_email(resume_text)

    resume.phone = ensure_string(safe_get(data, "phone")).strip()
    if not resume.phone:
        resume.phone = extract_phone(resume_text)

    # LinkedIn
    raw_linkedin = ensure_string(safe_get(data, "linkedin")).strip()
    if not raw_linkedin or raw_linkedin.lower() in ["linkedin", "n/a", "none"]:
        raw_linkedin = extract_linkedin(resume_text)
    if raw_linkedin and not raw_linkedin.startswith("http"):
        raw_linkedin = "https://" + raw_linkedin.lstrip("/")
    resume.linkedin = raw_linkedin

    # GitHub
    raw_github = ensure_string(safe_get(data, "github")).strip()
    if not raw_github or raw_github.lower() in ["github", "n/a", "none"]:
        raw_github = extract_github(resume_text)
    if raw_github and not raw_github.startswith("http"):
        raw_github = "https://" + raw_github.lstrip("/")
    resume.github = raw_github

    # Portfolio
    raw_portfolio = ensure_string(safe_get(data, "portfolio")).strip()
    if not raw_portfolio or "@" in raw_portfolio or "gmail.com" in raw_portfolio.lower() or raw_portfolio.lower() in ["portfolio", "n/a", "none"]:
        raw_portfolio = extract_portfolio(resume_text)
    if raw_portfolio and "@" not in raw_portfolio:
        if not raw_portfolio.startswith("http"):
            raw_portfolio = "https://" + raw_portfolio.lstrip("/")
        resume.portfolio = raw_portfolio
    else:
        resume.portfolio = ""



    resume.location = normalize_location(
        ensure_string(
            safe_get(data, "location")
        )
    )

    resume.career_level = ensure_string(
        safe_get(data, "career_level")
    )

    resume.experience_years = ensure_float(
        safe_get(data, "experience_years")
    )

    resume.preferred_role = ensure_string(
        safe_get(data, "preferred_role")
    )

    resume.preferred_location = ensure_string(
        safe_get(data, "preferred_location")
    )

    

    # ------------------------------------------------------
    # Career
    # ------------------------------------------------------

    if not resume.preferred_role:

        resume.preferred_role = infer_role(
            resume_text
        )

    # Ensure preferred_location is a major job city from config, fallback to infer_location if not
    is_major_city = False
    from config import DEFAULT_LOCATIONS
    for city in DEFAULT_LOCATIONS:
        if city.lower() in resume.preferred_location.lower():
            is_major_city = True
            break

    if not resume.preferred_location or not is_major_city:

        resume.preferred_location = infer_location(
            resume_text
        )

    if resume.experience_years <= 0:

        resume.experience_years = infer_experience(
            resume_text
        )

    if not resume.career_level:

        resume.career_level = infer_career_level(
            resume.experience_years
        )

    # ------------------------------------------------------
    # Skills
    # ------------------------------------------------------

    ai_skills = ensure_list(

        safe_get(

            data,

            "skills"

        )

    )

    extracted_skills = extract_skills(

        resume_text

    )

    resume.skills = sorted({
        skill.strip().title()
        for skill in ai_skills + extracted_skills
        if skill
    })

    resume.soft_skills = ensure_list(

        safe_get(

            data,

            "soft_skills"

        )

    )

    # ------------------------------------------------------
    # Education
    # ------------------------------------------------------

    resume.education = ensure_list(

        safe_get(

            data,

            "education"

        )

    )


    resume.experience = ensure_list(
        safe_get(data, "experience")
    )

    # ------------------------------------------------------
    # Projects
    # ------------------------------------------------------

    resume.projects = ensure_list(

        safe_get(

            data,

            "projects"

        )

    )

    # ------------------------------------------------------
    # Certifications
    # ------------------------------------------------------

    resume.certifications = ensure_list(

        safe_get(

            data,

            "certifications"

        )

    )

    # ------------------------------------------------------
    # Languages
    # ------------------------------------------------------

    resume.languages = ensure_list(

        safe_get(

            data,

            "languages"

        )

    )

    # ------------------------------------------------------
    # Summary
    # ------------------------------------------------------

    resume.career_summary = ensure_string(

        safe_get(

            data,

            "career_summary"

        )

    )

    resume.raw_resume_text = resume_text

    info("ResumeData created successfully.")

    return resume

# ==========================================================
# Enrich Resume
# ==========================================================

def enrich_resume(
    resume: ResumeData
) -> ResumeData:
    """
    Enrich ResumeData using internal services.
    """

    info("Enriching ResumeData.")

    ats_report = calculate_ats(resume)

    # ------------------------------------------------------
    # ATS
    # ------------------------------------------------------

    resume.ats_score = ats_report.score

    resume.missing_skills = ats_report.missing_skills

    resume.recommended_courses = (
        ats_report.recommended_courses
    )

    resume.recommended_certifications = (
        ats_report.recommended_certifications
    )

    return resume


# ==========================================================
# Analyze Resume
# ==========================================================

def analyze_resume(
    resume_text: str
) -> ResumeData:
    """
    Analyze resume using Ollama.

    Parameters
    ----------
    resume_text : str

    Returns
    -------
    ResumeData
    """

    info("Resume analysis started.")

    try:

        # ------------------------------------------
        # Call Ollama
        # ------------------------------------------

        for attempt in range(MAX_RETRIES):

            ai_response = request_with_retry(resume_text)

            try:
                data = parse_json(ai_response)
                break

            except InvalidAIResponseError:

                warning(
                    f"Invalid JSON from AI. Retry {attempt + 1}"
            )

        else:
            raise InvalidAIResponseError(
                "AI returned invalid JSON after all retries."
            )

        data = validate_schema(
            data
        )

        # ------------------------------------------
        # Build ResumeData
        # ------------------------------------------

        resume = build_resume_data(

            data,

            resume_text

        )

        # ------------------------------------------
        # ATS
        # ------------------------------------------

        resume = enrich_resume(
            resume
        )

        resume.status = "success"

        resume.message = (

            "Resume analyzed successfully."

        )

        info("Resume analysis completed.")

        return resume

    except InvalidAIResponseError:

        raise

    except ResumeAnalyzerError:

        raise

    except Exception as e:

        exception(
            "Resume analysis failed."
        )

        raise ResumeAnalyzerError(
            str(e)
        )
    
# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    print("=" * 60)
    print(" AI JobAgent - Resume Analyzer ")
    print("=" * 60)

    from services.resume.resume_parser import extract_resume_text

    resume_path = input(
        "\nEnter Resume Path: "
    ).strip()

    try:

        # ----------------------------------------------
        # Extract Resume
        # ----------------------------------------------

        resume_text = extract_resume_text(
            resume_path
        )

        # ----------------------------------------------
        # Analyze Resume
        # ----------------------------------------------

        resume = analyze_resume(
            resume_text
        )

        print("\nResume Analysis Completed\n")

        print("=" * 60)

        print(f"Name              : {resume.name}")
        print(f"Email             : {resume.email}")
        print(f"Phone             : {resume.phone}")
        print(f"Location          : {resume.location}")
        print(f"Career Level      : {resume.career_level}")
        print(f"Experience        : {resume.experience_years}")
        print(f"Preferred Role    : {resume.preferred_role}")

        print("=" * 60)

        print("\nTechnical Skills")

        for skill in resume.skills:

            print(f"  • {skill}")

        print("\nProjects :", len(resume.projects))
        print("Education :", len(resume.education))
        print("Certificates :", len(resume.certifications))

        print("\nATS Score :", resume.ats_score)

        print("\nRecommended Courses")

        if resume.recommended_courses:

            for course in resume.recommended_courses:

                print(f"  • {course}")

        else:

            print("  None")

        print("\nRecommended Certifications")

        if resume.recommended_certifications:

            for cert in resume.recommended_certifications:

                print(f"  • {cert}")

        else:

            print("  None")

        print("\nResume Summary")

        print(resume.career_summary)

        print("\nAnalysis Completed Successfully.")

    except Exception as e:

        print("\nAnalysis Failed")

        print(e)