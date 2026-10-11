"""
==========================================================
Automation - Scheduled Job Search Tasks
==========================================================
"""

from typing import List, Dict, Any

def run_scheduled_job_search(role: str = "Data Analyst", location: str = "Hyderabad") -> List[Dict[str, Any]]:
    from app.services.job_service import job_service
    return job_service.filter_jobs(role_query=role, location_query=location)
