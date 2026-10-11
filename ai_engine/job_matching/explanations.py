"""
==========================================================
AI Engine Job Matching - Explanations
==========================================================
"""

from typing import List

def generate_match_explanation(role: str, matching_skills: List[str], missing_skills: List[str], score: float) -> str:
    explanation = f"Matched {score}% with {role}. "
    if matching_skills:
        explanation += f"Strengths in {', '.join(matching_skills[:3])}. "
    if missing_skills:
        explanation += f"Recommended keyword improvements: {', '.join(missing_skills[:3])}."
    return explanation
