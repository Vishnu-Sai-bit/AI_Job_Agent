"""
==========================================================
AI Engine Job Matching - Scoring
==========================================================
"""

def compute_weighted_score(role_fit: float, skill_fit: float, exp_fit: float = 80.0) -> float:
    score = (0.40 * role_fit) + (0.45 * skill_fit) + (0.15 * exp_fit)
    return round(min(100.0, max(30.0, score)), 1)
