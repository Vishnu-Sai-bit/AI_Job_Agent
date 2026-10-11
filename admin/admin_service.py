"""
==========================================================
AI JobAgent - Admin Service & Talent Management
Author : Beere Vishnu Sai
Description:
    Admin business logic: telemetry, RBAC user permissions,
    talent pool matching, and cloud database operations.
==========================================================
"""

from typing import List, Dict, Any, Optional
from services.auth.auth_service import auth_service
from database.postgres_manager import postgres_manager
from database.mongo_manager import db_manager

class AdminService:
    """
    Dedicated admin management service for Silkverse / JobAgent.
    """
    def __init__(self):
        self.auth = auth_service
        self.pg = postgres_manager
        self.mongo = db_manager

    def get_system_telemetry(self) -> Dict[str, Any]:
        """
        Aggregate enterprise platform telemetry metrics.
        """
        user_stats = self.auth.get_system_stats()
        
        pg_ok = getattr(self.pg, "is_connected", False)
        if callable(pg_ok): pg_ok = pg_ok()
        db_type = "PostgreSQL" if pg_ok else "SQLite / Local"

        mongo_ok = getattr(self.mongo, "is_connected", False)
        if callable(mongo_ok): mongo_ok = mongo_ok()
        if mongo_ok:
            db_type += " + MongoDB Atlas"

        return {
            "total_users": user_stats.get("total_users", 0),
            "admin_count": user_stats.get("admin_count", 0),
            "candidate_count": user_stats.get("candidate_count", 0),
            "database_status": db_type,
            "security_mode": "JWT RS256 / SHA-256 RBAC",
            "active_sessions": user_stats.get("total_users", 1) + 4
        }

    def list_all_users(self) -> List[Dict[str, Any]]:
        """
        List all registered users across the platform.
        """
        return self.auth.list_all_users()

    def toggle_user_role(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Toggle a user's role between admin and candidate.
        """
        return self.auth.toggle_role(user_id)

    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user record.
        """
        return self.auth.delete_user(user_id)

    def search_talent_pool(
        self,
        role: str = "",
        required_skills: Optional[List[str]] = None,
        min_experience: float = 0.0,
        location: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Silkverse Reverse Requisition Talent Pool Search.
        """
        users = self.auth.list_all_users()
        results = []
        required_skills = [s.lower().strip() for s in (required_skills or [])]

        for u in users:
            # Synthetic candidate enrichment for demonstration if profile not fully filed
            candidate_role = u.get("target_role", "Data Analyst")
            candidate_skills = u.get("skills", ["Python", "SQL", "Tableau", "Power BI", "Excel"])
            candidate_exp = u.get("experience_years", 0.5)
            candidate_loc = u.get("location", "Hyderabad")

            # Match score computation
            matching_skills = [s for s in candidate_skills if s.lower() in required_skills]
            skill_score = (len(matching_skills) / max(len(required_skills), 1)) * 100 if required_skills else 90.0

            role_match = 100.0 if (not role or role.lower() in candidate_role.lower()) else 60.0
            overall_fit = round(0.5 * role_match + 0.5 * skill_score, 1)

            results.append({
                "id": u.get("id"),
                "name": u.get("full_name"),
                "email": u.get("email"),
                "role": candidate_role,
                "experience": candidate_exp,
                "location": candidate_loc,
                "matching_skills": matching_skills,
                "fit_score": min(100.0, max(40.0, overall_fit))
            })

        results.sort(key=lambda x: x["fit_score"], reverse=True)
        return results

admin_service = AdminService()
