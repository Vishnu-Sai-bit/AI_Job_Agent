"""
==========================================================
AI JobAgent - Resume Tailoring Agent
Author : Antigravity
==========================================================
"""

import json
from typing import Dict, Any, List
from utils import info, exception, call_llm
from models.resume import ResumeData

PROMPT = """
You are an expert Executive Career Strategist and ATS Specialist.
Your task is to tailor a candidate's resume specifically for a target job opening WITHOUT inventing, fabricating, or adding false skills or experience.

Strict Rules:
1. Work ONLY with the candidate's real skills, projects, certifications, and experience provided below.
2. Formulate a compelling, tailored Professional Summary (3-4 sentences) highlighting the exact intersection between the candidate's actual background and the target role requirements.
3. Prioritize candidate's actual skills into "core_matching_skills" (directly required by the JD) and "supporting_skills".
4. Reframe 2-3 of the candidate's real project bullet points using strong action verbs, quantifiable metrics, and relevance to this specific company.
5. Provide actionable ATS optimization keywords to emphasize.

Output Schema (Return valid JSON only):
{{
    "tailored_summary": "Tailored 3-4 sentence professional summary...",
    "core_matching_skills": ["Skill 1", "Skill 2"],
    "supporting_skills": ["Skill 3", "Skill 4"],
    "tailored_projects": [
        {{
            "project_title": "Project Name",
            "tailored_bullet_points": [
                "Tailored bullet point 1 with metrics...",
                "Tailored bullet point 2..."
            ]
        }}
    ],
    "ats_keywords_to_emphasize": ["Keyword 1", "Keyword 2", "Keyword 3"],
    "strategic_advice": "1-2 sentences on how to stand out for this specific company..."
}}

Target Job:
- Title: {role}
- Company: {company}
- Key Required Skills: {required_skills}
- Job Description Context: {job_description}

Candidate Profile:
- Current Summary: {candidate_summary}
- Actual Skills: {candidate_skills}
- Projects & Experience: {candidate_context}
- Certifications: {candidate_certs}

Return ONLY raw JSON.
"""

def tailor_resume_for_job(
    resume_context: Dict[str, Any],
    job_title: str,
    job_company: str,
    job_description: str = "",
    required_skills: List[str] = None
) -> Dict[str, Any]:
    """
    Generate tailored resume components for a specific job posting.
    """
    required_skills_str = ", ".join(required_skills) if required_skills else "Not Specified"
    candidate_skills_str = ", ".join(resume_context.get("skills", []))
    candidate_certs_str = ", ".join(resume_context.get("certifications", []))
    
    projects_context = []
    for p in resume_context.get("projects", []):
        t = p.get("title") or p.get("name") or ""
        d = p.get("description") or ""
        projects_context.append(f"• Project: {t}. Details: {d}")
    for e in resume_context.get("experience", []):
        r = e.get("designation") or e.get("role") or ""
        c = e.get("company") or ""
        d = e.get("description") or ""
        projects_context.append(f"• Experience: {r} at {c}. Details: {d}")

    formatted_prompt = PROMPT.format(
        role=job_title or "Target Role",
        company=job_company or "Target Employer",
        required_skills=required_skills_str,
        job_description=(job_description or "General opening")[:1500],
        candidate_summary=resume_context.get("career_summary") or resume_context.get("summary") or "Motivated and dedicated professional",
        candidate_skills=candidate_skills_str or "Technical problem-solving and domain skills",
        candidate_context="\n".join(projects_context) if projects_context else "Hands-on technical deliverables and project experience",
        candidate_certs=candidate_certs_str or "Relevant technical certifications and credentials"
    )

    info(f"Generating tailored resume for: {job_title} at {job_company}")

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
        exception(f"Resume tailoring generation failed: {e}")
        # Dynamic fallback
        skills = resume_context.get("skills", ["Problem Solving", "Technical Execution"])
        matching = [s for s in skills if s.lower() in [r.lower() for r in (required_skills or [])]]
        if not matching:
            matching = skills[:3]
        supporting = [s for s in skills if s not in matching]

        raw_projects = resume_context.get("projects", [])
        project_title = "Core Technical Deliverable & Architecture"
        if raw_projects:
            first_p = raw_projects[0]
            if isinstance(first_p, dict):
                project_title = first_p.get("title") or first_p.get("name") or first_p.get("project_name") or project_title
            elif isinstance(first_p, str):
                project_title = first_p

        top_skill = matching[0] if matching else (skills[0] if skills else "technical architecture")
        return {
            "tailored_summary": f"Analytical and results-driven professional specializing in {', '.join(matching[:3]) if matching else 'software and technical deliverables'}. Proven ability in engineering robust solutions, optimizing workflows, and driving measurable impact aligned with {job_company}'s goals for the {job_title} role.",
            "core_matching_skills": matching,
            "supporting_skills": supporting,
            "tailored_projects": [
                {
                    "project_title": project_title,
                    "tailored_bullet_points": [
                        f"Architected and deployed technical solution leveraging {top_skill}, improving system performance and reliability.",
                        f"Collaborated cross-functionally to integrate robust components, achieving measurable operational efficiency."
                    ]
                }
            ],
            "ats_keywords_to_emphasize": matching + ["System Optimization", "Best Practices", "Scalability"],
            "strategic_advice": f"Emphasize your hands-on experience in {top_skill} and specific measurable project outcomes when interviewing at {job_company}."
        }
