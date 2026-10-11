"""
==========================================================
Job Sources - Deduplicator
==========================================================
"""

from typing import List, Dict, Any

def deduplicate_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen_keys = set()
    unique_jobs = []
    for j in jobs:
        title = (j.get("title") or "").lower().strip()
        company = (j.get("company") or "").lower().strip()
        key = f"{title}::{company}"
        if key not in seen_keys and title:
            seen_keys.add(key)
            unique_jobs.append(j)
    return unique_jobs
