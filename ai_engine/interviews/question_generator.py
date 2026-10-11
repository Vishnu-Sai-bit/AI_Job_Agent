"""
==========================================================
AI Engine Interviews - Question Generator
==========================================================
"""

from typing import List, Dict, Any
from services.interview.interview_generator import generate_interview_questions

def generate_questions(role: str, skills: List[str], company: str = "Target MNC", count: int = 4) -> Dict[str, Any]:
    return generate_interview_questions(role=role, skills=skills, company=company, question_count=count)
