"""
==========================================================
Analytics - Resume Analytics
==========================================================
"""

from typing import Dict, Any

def summarize_ats_performance(candidate: Dict[str, Any]) -> Dict[str, Any]:
    score = candidate.get("ats_score", 79.0)
    return {
        "score": score,
        "percentile": "Top 15%",
        "status": "Competitive" if score >= 75 else "Needs Improvement"
    }
