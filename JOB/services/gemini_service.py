import os
import json
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from flask import current_app
from utils.logging_config import logger

load_dotenv()

class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        self._explicit_key = api_key

    def get_api_key(self) -> str:
        if self._explicit_key is not None:
            return self._explicit_key
        try:
            if current_app and current_app.config.get("GEMINI_API_KEY"):
                return current_app.config["GEMINI_API_KEY"]
        except Exception:
            pass
        return os.getenv("GEMINI_API_KEY", "")

    def is_available(self) -> bool:
        key = self.get_api_key()
        return bool(key and len(key.strip()) > 5)

    def analyze_resume_deep(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """
        Uses Google Gemini to parse and deeply analyze a resume with professional ATS intelligence.
        Returns parsed profile data and an in-depth AI critique.
        """
        try:
            if current_app and current_app.config.get("TESTING") and not self._explicit_key:
                return None
        except Exception:
            pass

        api_key = self.get_api_key()
        if not api_key:
            logger.info("Gemini API key is not configured. Falling back to local deterministic parsing.")
            return None

        prompt = f"""You are a senior technical recruiter and principal ATS (Applicant Tracking System) intelligence consultant.
Analyze the following resume thoroughly and extract clean, structured data and an in-depth diagnostic critique.

RESUME CONTENT:
\"\"\"
{raw_text[:12000]}
\"\"\"

Output MUST be a single, valid JSON object (and nothing else) adhering exactly to this structure:
{{
  "parsed_data": {{
    "name": "Full candidate name",
    "email": "candidate@example.com",
    "phone": "+1 555-0199",
    "location": "City, State/Country",
    "headline": "Concise professional title (e.g. Senior Full-Stack Engineer)",
    "summary": "2-3 sentence executive summary of experience and core competencies",
    "skills": ["List of all detected technical & domain skills"],
    "skills_by_category": {{
      "languages": ["Python", "JavaScript", "..."],
      "frameworks": ["Flask", "React", "..."],
      "databases": ["PostgreSQL", "Redis", "..."],
      "cloud_devops": ["AWS", "Docker", "Kubernetes", "..."],
      "tools_and_practices": ["Git", "CI/CD", "Agile", "..."]
    }},
    "experience_years": 4.5,
    "experience": [
      {{
        "title": "Job Title",
        "company": "Company Name",
        "duration": "Start - End Date",
        "details": [
          "Action-oriented achievement bullet point 1",
          "Action-oriented achievement bullet point 2"
        ]
      }}
    ],
    "projects": [
      {{
        "title": "Project Title",
        "description": "Clear description of what was built and impact",
        "technologies": ["Tech1", "Tech2"]
      }}
    ],
    "education": [
      {{
        "degree": "Degree and Major",
        "institution": "University / College Name",
        "year": "Graduation Year"
      }}
    ],
    "certifications": ["Cert 1", "Cert 2"]
  }},
  "ai_critique": {{
    "executive_summary": "Comprehensive 3-4 sentence professional evaluation of resume strength, clarity, and ATS readability.",
    "ats_score_estimate": 85,
    "key_strengths": [
      "Specific technical strength or clear competitive advantage",
      "Evidence of ownership and tangible engineering contributions"
    ],
    "critical_weaknesses_and_gaps": [
      "Identified weakness, missing quantification, or ATS blind spot",
      "Vague bullet points or unproven technology claims"
    ],
    "actionable_bullet_rewrites": [
      {{
        "original_or_concept": "Original vague bullet or underdeveloped concept from resume",
        "recommended_rewrite": "High-impact rewrite starting with strong action verb and quantified outcome",
        "rationale": "Why this rewrite dramatically improves ATS ranking and recruiter engagement"
      }}
    ],
    "ats_formatting_advice": [
      "Actionable formatting recommendation for ATS scanners"
    ]
  }}
}}
"""
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            
            # Use modern Gemini 3.8 / 3.5 models
            for model_name in ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-flash-latest"]:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    text_resp = response.text
                    if text_resp:
                        return self._clean_and_parse_json(text_resp)
                except Exception as model_err:
                    logger.warning(f"Gemini model {model_name} invocation error: {model_err}")
                    continue

        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")

        return None

    def _clean_and_parse_json(self, raw_resp: str) -> Optional[Dict[str, Any]]:
        text = raw_resp.strip()
        # Remove markdown code fences if present e.g. ```json ... ```
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s*```$", "", text)
        
        try:
            data = json.loads(text.strip())
            return data
        except json.JSONDecodeError as ex:
            logger.error(f"JSON decode error from Gemini response: {ex}. Raw snippet: {text[:200]}")
            # Try finding the first '{' and last '}'
            m = re.search(r"(\{.*\})", text, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group(1))
                except Exception:
                    pass
        return None
