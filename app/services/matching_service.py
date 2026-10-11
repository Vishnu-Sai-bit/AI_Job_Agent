"""
==========================================================
AI Job Copilot - Matching Service
==========================================================
"""

from typing import List, Dict, Any

class MatchingService:
    @staticmethod
    def calculate_match(job: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
        candidate_skills = {s.lower().strip() for s in candidate.get("skills", [])}
        job_skills = job.get("skills") or []

        matching = [s for s in job_skills if s and s.lower().strip() in candidate_skills]
        missing = [s for s in job_skills if s and s.lower().strip() not in candidate_skills]

        skill_pct = (len(matching) / len(job_skills) * 100.0) if job_skills else 85.0
        role_pct = 95.0 if candidate.get("preferred_role", "").lower() in job.get("title", "").lower() else 75.0

        score = round(0.40 * role_pct + 0.45 * skill_pct + 15.0, 1)
        score = min(100.0, max(35.0, score))

        return {
            "score": score,
            "matching_skills": matching,
            "missing_skills": missing,
            "role_fit": role_pct,
            "skill_fit": skill_pct
        }

matching_service = MatchingService()
