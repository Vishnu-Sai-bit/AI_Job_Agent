"""
==========================================================
AI JobAgent - Cover Letter Generator Service
Author : Antigravity
==========================================================
"""

import json
from typing import Dict, Any

from utils import info, exception, call_llm
from exceptions import ResumeAnalyzerError, OllamaConnectionError

PROMPT = """
You are an expert AI Resume Writer and Recruiter.
Your task is to generate a professional, high-impact cover letter tailored for a specific candidate and job role.

Generate the letter following this JSON schema exactly:
{
    "subject": "Job Application: [Job Title] - [Candidate Name]",
    "salutation": "Dear [Hiring Manager Name/Hiring Team],",
    "introduction": "Introductory paragraph expressing interest in the role...",
    "body_paragraphs": [
        "First body paragraph detailing matching skills and value proposition...",
        "Second body paragraph highlighting specific achievements..."
    ],
    "conclusion": "Concluding paragraph with call-to-action...",
    "sign_off": "Sincerely,\\n[Candidate Name]"
}

Candidate Name: {name}
Skills: {skills}
Target Job Title: {job_title}
Company: {company}
Job Description: {job_desc}

IMPORTANT: Return ONLY the raw JSON structure. Do NOT explain anything else.
"""

def generate_cover_letter(
    name: str,
    skills: list,
    job_title: str,
    company: str,
    job_desc: str = ""
) -> Dict[str, Any]:
    """
    Generate a cover letter using the LLM helper.
    """
    skills_str = ", ".join(skills) if skills else "Data Analysis, Python, SQL"
    formatted_prompt = PROMPT.format(
        name=name or "Candidate",
        skills=skills_str,
        job_title=job_title or "Data Analyst",
        company=company or "Company",
        job_desc=job_desc or "N/A"
    )

    info(f"Generating cover letter for {job_title} at {company}")

    try:
        content = call_llm(formatted_prompt, json_format=True)
        return json.loads(content)
    except Exception as e:
        exception("Cover letter generation failed.")
        # Fallback dictionary structure
        return {
            "subject": f"Application for {job_title} - {name}",
            "salutation": "Dear Hiring Team,",
            "introduction": f"I am writing to express my strong interest in the {job_title} position at {company}.",
            "body_paragraphs": [
                f"With my expertise in {skills_str}, I am confident in my ability to add value to your team.",
                "I look forward to discussing how my experience aligns with your team's needs."
            ],
            "conclusion": "Thank you for your time and consideration.",
            "sign_off": f"Sincerely,\n{name}"
        }
