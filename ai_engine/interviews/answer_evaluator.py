"""
==========================================================
AI Engine Interviews - Answer Evaluator
==========================================================
"""

from typing import List, Dict, Any
from services.interview.mock_evaluator import evaluate_mock_answer

def evaluate_candidate_answer(question: str, answer: str, role: str, skills: List[str]) -> Dict[str, Any]:
    return evaluate_mock_answer(question=question, candidate_answer=answer, role=role, resume_context=", ".join(skills))
