"""
==========================================================
AI JobAgent - Interview Simulator Service
Author : Antigravity
==========================================================
"""

import json
from typing import Dict, Any, List

from utils import info, exception, call_llm
from exceptions import ResumeAnalyzerError, OllamaConnectionError

PROMPT = """
You are a {interviewer_role} at a major technology MNC.
Your job is to generate a list of mock interview questions tailored for a candidate applying for a target role.

Generate the questions following this JSON schema exactly:
{{
    "questions": [
        {{
            "type": "Technical / Behavioral / Scenario",
            "question": "The interview question text...",
            "answer_tips": "Key talking points, technical keywords to include, or what the interviewer is looking for...",
            "sample_answer": "A model response showing how to answer this question professionally..."
        }}
    ]
}}

Generate exactly {question_count} questions (mix of technical, behavioral, and scenario-based questions matching the tone of a {interviewer_role}).

Target Role: {role}
Skills: {skills}
Candidate Resume Context (if available): {resume_context}

CRITICAL: If the Candidate Resume Context is provided, tailor at least 50% of the questions specifically to the candidate's actual projects, work experience description, achievements, or education mentioned in their resume context. Act and evaluate exactly like a seasoned {interviewer_role}.

IMPORTANT: Return ONLY the raw JSON structure. Do NOT explain anything else.
"""

def generate_interview_questions(
    role: str,
    skills: List[str],
    resume_context: str = "",
    question_count: int = 5,
    interviewer_role: str = "Senior Technical Recruiter"
) -> Dict[str, Any]:
    """
    Generate mock interview questions and answers using the LLM helper.
    """
    skills_str = ", ".join(skills) if skills else "Data Analysis, Python, SQL"
    formatted_prompt = PROMPT.format(
        role=role or "Data Analyst",
        skills=skills_str,
        resume_context=resume_context or "Not Provided",
        question_count=question_count,
        interviewer_role=interviewer_role
    )

    info(f"Generating mock interview questions for: {role}")

    try:
        content = call_llm(formatted_prompt, json_format=True)
        return json.loads(content)
    except Exception as e:
        exception("Mock interview question generation failed.")
        # Fallback list of questions
        return {
            "questions": [
                {
                    "type": "Technical",
                    "question": f"Can you explain your experience using {skills[0] if skills else 'SQL'} in your projects?",
                    "answer_tips": "Explain the project goal, data size, and query complexity.",
                    "sample_answer": "In my recent project, I used it to retrieve and clean transactional data, resulting in faster dashboard processing."
                },
                {
                    "type": "Behavioral",
                    "question": "Tell me about a time you had to deal with ambiguous requirements.",
                    "answer_tips": "Use the STAR method: Situation, Task, Action, Result.",
                    "sample_answer": "I worked closely with product stakeholders to clarify business definitions before modeling the datasets."
                }
            ]
        }
