"""
==========================================================
AI JobAgent - LinkedIn Optimizer Service
Author : Antigravity
==========================================================
"""

import json
from typing import Dict, Any, List

from utils import info, exception, call_llm
from exceptions import ResumeAnalyzerError, OllamaConnectionError

PROMPT = """
You are an expert LinkedIn branding specialist and career optimizer.
Your task is to analyze the candidate's details and generate optimized suggestions to maximize recruiter views on LinkedIn.

Generate the suggestions following this JSON schema exactly:
{
    "suggested_headlines": [
        "Headline Option 1: Action-oriented (e.g. Data Analyst | Python, SQL & Power BI | Helping businesses derive insights...)",
        "Headline Option 2: Skills-focused",
        "Headline Option 3: Achievement-focused"
    ],
    "about_summary": "A highly compelling, search-optimized 'About' section summary (first-person narrative, listing skills, values, and call-to-action)...",
    "experience_bullet_enhancements": [
        "Suggestion 1: Quantify impact...",
        "Suggestion 2: Highlight key technologies..."
    ],
    "seo_keywords_to_add": ["keyword1", "keyword2", "keyword3"]
}

Candidate Name: {name}
Target Role: {role}
Current Skills: {skills}
Experience Text: {experience_text}

IMPORTANT: Return ONLY the raw JSON structure. Do NOT explain anything else.
"""

def optimize_linkedin_profile(
    name: str,
    role: str,
    skills: List[str],
    experience_text: str = ""
) -> Dict[str, Any]:
    """
    Generate optimized LinkedIn headlines and summaries using LLM helper.
    """
    skills_str = ", ".join(skills) if skills else "None"
    formatted_prompt = PROMPT.format(
        name=name or "Candidate",
        role=role or "Data Analyst",
        skills=skills_str,
        experience_text=experience_text or "N/A"
    )

    info(f"Generating LinkedIn optimization profile for {name}")

    try:
        content = call_llm(formatted_prompt, json_format=True)
        return json.loads(content)
    except Exception as e:
        exception("LinkedIn optimization failed.")
        # Fallback suggestions
        return {
            "suggested_headlines": [
                f"{role} | Specializing in {skills_str} | Open to Opportunities",
                f"Data Analyst passionate about turning raw datasets into actionable insights using Python & SQL"
            ],
            "about_summary": f"Hi! I am a results-oriented {role} skilled in {skills_str}. I love solving complex data problems.",
            "experience_bullet_enhancements": [
                "Quantify bullet points: add percentage increases in efficiency or query speeds."
            ],
            "seo_keywords_to_add": ["Data Analysis", "Python", "SQL", "Dashboard Reporting"]
        }
