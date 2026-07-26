"""
==========================================================
AI JobAgent - Learning Engine Service
Author : Antigravity
==========================================================
"""

import json
from typing import Dict, Any, List

from utils import info, exception, call_llm
from exceptions import ResumeAnalyzerError, OllamaConnectionError

PROMPT = """
You are an expert career advisor and technical educator.
Your task is to identify skill gaps between a candidate's current skills and their target career role, and recommend a structured roadmap.

Generate the roadmap following this JSON schema exactly:
{{
    "skill_gaps": ["skill1", "skill2"],
    "roadmaps": [
        {{
            "skill": "Skill Name",
            "learning_path": "Step-by-step roadmap to master this skill...",
            "courses": ["Course Title 1 (Coursera/Udemy/Pluralsight)", "Course Title 2"],
            "recommended_certifications": ["Certification Name 1", "Certification Name 2"],
            "suggested_project": "A practical project description to build and add to resume to prove capability..."
        }}
    ]
}}

Target Role: {role}
Current Skills: {skills}

IMPORTANT: Return ONLY the raw JSON structure. Do NOT explain anything else.
"""

def generate_learning_roadmap(role: str, skills: List[str]) -> Dict[str, Any]:
    """
    Identify skill gaps and generate a learning roadmap using the LLM helper.
    """
    skills_str = ", ".join(skills) if skills else "None"
    formatted_prompt = PROMPT.format(
        role=role or "Data Analyst",
        skills=skills_str
    )

    info(f"Generating learning roadmap for target role: {role}")

    try:
        content = call_llm(formatted_prompt, json_format=True)
        return json.loads(content)
    except Exception as e:
        exception("Learning roadmap generation failed.")
        # Fallback recommendations
        return {
            "skill_gaps": ["dbt", "Snowflake"],
            "roadmaps": [
                {
                    "skill": "dbt",
                    "learning_path": "Learn modeling, SQL transformations, and documentation testing.",
                    "courses": ["dbt Fundamentals (Free on dbt Learn)"],
                    "recommended_certifications": ["dbt Certified Developer"],
                    "suggested_project": "Build a data pipeline orchestrating transformations using dbt Core and BigQuery."
                }
            ]
        }
