"""
==========================================================
AI Job Copilot - Interview Service
==========================================================
"""

from typing import List, Dict, Any, Optional
from services.interview.interview_generator import generate_interview_questions
from services.interview.mock_evaluator import evaluate_mock_answer

class InterviewService:
    @staticmethod
    def get_questions(role: str, skills: List[str], company: str = "Target MNC", count: int = 4) -> List[Dict[str, Any]]:
        res = generate_interview_questions(role=role, skills=skills, company=company, question_count=count)
        if isinstance(res, dict) and "questions" in res:
            return res["questions"]
        return res if isinstance(res, list) else []

    @staticmethod
    def evaluate_response(question: str, answer: str, role: str, skills: List[str]) -> Dict[str, Any]:
        return evaluate_mock_answer(question=question, candidate_answer=answer, role=role, resume_context=", ".join(skills))

interview_service = InterviewService()
