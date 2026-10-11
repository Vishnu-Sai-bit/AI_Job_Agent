"""
==========================================================
Analytics - Job Market Analytics
==========================================================
"""

from typing import List, Dict, Any
from collections import Counter

def analyze_market_density(jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    locations = Counter([j.get("location", "Unknown") for j in jobs])
    return {
        "top_locations": dict(locations.most_common(5)),
        "total_jobs": len(jobs)
    }
