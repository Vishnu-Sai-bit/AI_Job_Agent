"""
==========================================================
AI Engine Career Intelligence - Learning Recommender
==========================================================
"""

from typing import List, Dict, Any
from services.learning.learning_engine import generate_learning_roadmap

def recommend_learning_path(role: str, skills: List[str]) -> Dict[str, Any]:
    return generate_learning_roadmap(role, skills)
