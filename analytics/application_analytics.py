"""
==========================================================
Analytics - Application Pipeline Analytics
==========================================================
"""

from typing import List, Dict, Any

def calculate_pipeline_metrics(applications: List[Dict[str, Any]]) -> Dict[str, Any]:
    stages = ["saved", "applied", "interview", "offer", "rejected"]
    counts = {s: sum(1 for a in applications if a.get("stage") == s) for s in stages}
    total = len(applications)
    conversion = round((counts["interview"] / counts["applied"] * 100), 1) if counts["applied"] > 0 else 0.0
    return {
        "total": total,
        "counts": counts,
        "interview_conversion_rate": conversion
    }
