"""
==========================================================
AI JobAgent - Company Intelligence Service
Author : Antigravity
==========================================================
"""

import json
from typing import Dict, Any, List
from utils import info, exception, call_llm

PROMPT = """
You are a Principal Talent Acquisition Partner and Corporate Intelligence Analyst.
Analyze the provided employer and role to generate comprehensive company intelligence, expected tech stack, hiring patterns, and a tailored recruiter pitch angle.

Generate output following this JSON schema exactly:
{{
    "company_name": "{company}",
    "industry_domain": "e.g. Enterprise Cloud Analytics / FinTech / Healthcare IT",
    "detected_tech_stack": ["Tool 1", "Tool 2", "Tool 3", "Database", "BI Platform"],
    "engineering_culture_and_hiring_focus": "2-3 sentences explaining the team's data culture, analytics maturity, and what they evaluate in candidates...",
    "interview_focus_areas": [
        "Live Technical Evaluation (e.g. Complex SQL Joins & Window Functions)",
        "Portfolio & KPI Defense (e.g. Dashboard layout & business metric definitions)",
        "Cross-functional Stakeholder Communication"
    ],
    "recruiter_pitch_angle": "A customized 2-3 sentence elevator pitch the candidate can use when messaging recruiters at this specific company..."
}}

Company: {company}
Target Role: {role}
Job Description Context: {job_description}
Candidate Background Skills: {candidate_skills}

Return ONLY valid JSON.
"""

def generate_company_insights(
    company: str,
    role: str,
    job_description: str = "",
    candidate_skills: List[str] = None
) -> Dict[str, Any]:
    """
    Generate corporate intelligence, tech stack profile, and recruiter pitch hook.
    """
    candidate_skills_str = ", ".join(candidate_skills) if candidate_skills else "Python, SQL, Power BI, Tableau"
    formatted_prompt = PROMPT.format(
        company=company or "Target Enterprise",
        role=role or "Data Analyst",
        job_description=(job_description or "General opening")[:1500],
        candidate_skills=candidate_skills_str
    )

    info(f"Generating company intelligence for: {company} ({role})")

    try:
        content = call_llm(formatted_prompt, json_format=True)
        cleaned = content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return json.loads(cleaned.strip())
    except Exception as e:
        exception(f"Company intelligence generation failed: {e}")
        # Dynamic fallback
        return {
            "company_name": company or "Target Employer",
            "industry_domain": "Technology & Enterprise Data Solutions",
            "detected_tech_stack": ["SQL", "Power BI", "Tableau", "Python (Pandas)", "Cloud Data Warehouses"],
            "engineering_culture_and_hiring_focus": f"{company} values data integrity, actionable KPI reporting, and clear cross-functional stakeholder communication. Hiring managers prioritize candidates with verified portfolio dashboards and solid data modeling foundations.",
            "interview_focus_areas": [
                "Advanced SQL querying (Aggregations, Window Functions, Joins)",
                "Executive BI Dashboard Design & KPI Strategy",
                "STAR method behavioral questions on handling ambiguous business requirements"
            ],
            "recruiter_pitch_angle": f"I noticed {company}'s focus on data-driven decision making. Having built end-to-end analytics pipelines on 30,000+ records and delivered Oracle-certified BI dashboards, I am excited about contributing to your team's analytics goals."
        }
