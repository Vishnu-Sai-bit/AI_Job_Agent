"""
==========================================================
AI JobAgent - Salary Predictor Service
Author : Antigravity
==========================================================
"""

import json
from typing import Dict, Any, List

from utils import info, exception, call_llm
from exceptions import ResumeAnalyzerError, OllamaConnectionError

PROMPT = """
You are a compensation analyst and recruitment partner specializing in tech careers.
Your job is to predict the target salary range for a candidate based on their role, experience, skills, and preferred location.

Generate the prediction following this JSON schema exactly:
{
    "currency": "INR / USD",
    "low": 500000,
    "median": 800000,
    "high": 1200000,
    "market_trend": "Description of market demand, hiring velocity, and trends for this role...",
    "justification": "Why this range is recommended based on candidate profile (skills match, experience, location)..."
}

Provide estimations for both India market (INR) and Remote international market (USD).

Candidate Profile:
- Role: {role}
- Experience: {experience_years} years
- Skills: {skills}
- Location: {location}

IMPORTANT: Return ONLY the raw JSON structure. Do NOT explain anything else.
"""

def predict_salary(role: str, experience_years: float, skills: List[str], location: str) -> Dict[str, Any]:
    """
    Predict market salary range based on candidate profile using LLM helper.
    """
    skills_str = ", ".join(skills) if skills else "None"
    formatted_prompt = PROMPT.format(
        role=role or "Data Analyst",
        experience_years=experience_years or 0.0,
        skills=skills_str,
        location=location or "India"
    )

    info(f"Predicting salary range for: {role} ({experience_years} YOE)")

    try:
        content = call_llm(formatted_prompt, json_format=True)
        return json.loads(content)
    except Exception as e:
        exception("Salary prediction failed.")
        # Fallback predictions based on experience
        inr_val = 500000 + int(experience_years * 150000)
        return {
            "currency": "INR",
            "low": inr_val - 100000,
            "median": inr_val,
            "high": inr_val + 200000,
            "market_trend": "High demand for data practitioners with SQL and visualization capabilities.",
            "justification": f"Estimated based on {experience_years} years of experience in technical analysis."
        }
