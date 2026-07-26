"""
==========================================================
AI JobAgent - Email Generator Service
Author : Antigravity
==========================================================
"""

import json
from typing import Dict, Any, List

from utils import info, exception, call_llm
from exceptions import ResumeAnalyzerError, OllamaConnectionError

PROMPT = """
You are an expert recruitment coordinator and job search strategist.
Your task is to write high-conversion, professional emails for job applications and outreach.

Generate the emails following this JSON schema exactly:
{{
    "cold_outreach": {{
        "subject": "Subject for cold outreach to Hiring Manager...",
        "body": "Body of outreach email. Keep it concise, professional, highlighting 2 core skills and value proposition..."
    }},
    "job_application": {{
        "subject": "Subject for direct job application...",
        "body": "Body of application email attaching resume..."
    }},
    "interview_follow_up": {{
        "subject": "Subject for follow-up 48 hours after interview...",
        "body": "Body of thank-you and follow-up email..."
    }}
}}

Candidate Name: {name}
Skills: {skills}
Target Role: {role}
Company: {company}

IMPORTANT: Return ONLY the raw JSON structure. Do NOT explain anything else.
"""

def generate_job_emails(
    name: str,
    skills: List[str],
    role: str,
    company: str
) -> Dict[str, Any]:
    """
    Generate cold outreach, application, and follow-up email templates using LLM helper.
    """
    skills_str = ", ".join(skills) if skills else "None"
    formatted_prompt = PROMPT.format(
        name=name or "Candidate",
        skills=skills_str,
        role=role or "Data Analyst",
        company=company or "Company"
    )

    info(f"Generating email templates for: {role} at {company}")

    try:
        content = call_llm(formatted_prompt, json_format=True)
        return json.loads(content)
    except Exception as e:
        exception("Email template generation failed.")
        # Fallback templates
        return {
            "cold_outreach": {
                "subject": f"Inquiry: {role} opportunities at {company} - {name}",
                "body": f"Dear Hiring Team,\n\nI am writing to express my interest in joining your team as a {role}..."
            },
            "job_application": {
                "subject": f"Application for {role} - {name}",
                "body": f"Dear Hiring Manager,\n\nPlease find attached my resume for the {role} position..."
            },
            "interview_follow_up": {
                "subject": f"Thank you for the interview - {role} - {name}",
                "body": f"Dear Team,\n\nThank you for taking the time to speak with me about the {role} role..."
            }
        }
