"""
==========================================================
AI Job Copilot - Profile Service
==========================================================
"""

import json
from pathlib import Path
from typing import Dict, Any

class ProfileService:
    @staticmethod
    def get_candidate_context() -> Dict[str, Any]:
        cache_path = Path("data/default_parsed_resume.json")
        if cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "candidate_name": "BEERE VISHNU SAI",
            "email": "beerevishnusai776600@gmail.com",
            "phone": "+91 9182679641",
            "preferred_role": "Data Analyst",
            "preferred_location": "Hyderabad",
            "skills": ["Python", "SQL", "Tableau", "Power BI", "Excel", "Pandas"],
            "experience_years": 0.5,
            "ats_score": 79.0,
            "ats_breakdown": {
                "contact_score": 10.0,
                "skills_score": 30.0,
                "experience_score": 5.0,
                "education_score": 15.0,
                "projects_score": 11.0,
                "certifications_score": 8.0
            }
        }

    @staticmethod
    def save_candidate_profile(data: Dict[str, Any]) -> bool:
        cache_path = Path("data/default_parsed_resume.json")
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False

profile_service = ProfileService()
