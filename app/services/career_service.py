"""
==========================================================
AI Job Copilot - Career Service
==========================================================
"""

from typing import List, Dict, Any
from services.analytics.market_skill_aggregator import aggregate_market_skill_gaps
from services.learning.learning_engine import generate_learning_roadmap

class CareerService:
    @staticmethod
    def get_market_analysis(candidate_skills: List[str], jobs: List[Any]) -> Dict[str, Any]:
        return aggregate_market_skill_gaps(candidate_skills=candidate_skills, jobs=jobs)

    @staticmethod
    def get_roadmap(role: str, skills: List[str]) -> Dict[str, Any]:
        return generate_learning_roadmap(role=role, skills=skills)

career_service = CareerService()
