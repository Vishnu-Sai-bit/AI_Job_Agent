"""
==========================================================
Analytics - Dashboard Metrics Aggregator
==========================================================
"""

from typing import Dict, Any

def get_dashboard_summary(total_jobs: int, total_apps: int, ats_score: float) -> Dict[str, Any]:
    return {
        "verified_jobs_count": total_jobs,
        "tracked_applications_count": total_apps,
        "ats_compatibility_score": ats_score,
        "health_status": "Optimal"
    }
