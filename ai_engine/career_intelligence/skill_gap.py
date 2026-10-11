"""
==========================================================
AI Engine Career Intelligence - Skill Gap
==========================================================
"""

from typing import List, Dict, Any
from services.analytics.market_skill_aggregator import aggregate_market_skill_gaps

def analyze_skill_gaps(candidate_skills: List[str], jobs: List[Any]) -> Dict[str, Any]:
    return aggregate_market_skill_gaps(candidate_skills, jobs)
