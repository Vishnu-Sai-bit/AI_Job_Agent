"""
==========================================================
AI Job Copilot - Job Service
==========================================================
"""

import json
from pathlib import Path
from typing import List, Dict, Any

class JobService:
    @staticmethod
    def get_verified_jobs() -> List[Dict[str, Any]]:
        export_path = Path("data/jobs_export.json")
        if export_path.exists():
            try:
                with open(export_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    @staticmethod
    def filter_jobs(role_query: str = "", location_query: str = "") -> List[Dict[str, Any]]:
        jobs = JobService.get_verified_jobs()
        filtered = []
        for j in jobs:
            title = j.get("title", "")
            loc = j.get("location", "")
            if role_query and role_query.lower() not in title.lower():
                continue
            if location_query and location_query.lower() not in loc.lower():
                continue
            filtered.append(j)
        return filtered

job_service = JobService()
