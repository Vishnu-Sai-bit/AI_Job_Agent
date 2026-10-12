"""
==========================================================
AI Job Copilot - Application Service
==========================================================
"""

from typing import List, Dict, Any, Optional
from services.crm.application_crm import (
    get_all_applications,
    add_or_update_application,
    delete_application as crm_delete,
    generate_followup_message
)

class ApplicationService:
    @staticmethod
    def get_applications() -> List[Dict[str, Any]]:
        return get_all_applications()

    @staticmethod
    def save_application(app_data: Dict[str, Any]) -> None:
        add_or_update_application(app_data)

    @staticmethod
    def remove_application(app_id: str) -> None:
        crm_delete(app_id)

    @staticmethod
    def create_followup(candidate_name: str, company: str, role: str, date: str) -> str:
        return generate_followup_message(candidate_name, company, role, date)

application_service = ApplicationService()
