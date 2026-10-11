"""
==========================================================
AI Engine Agent - Job Discovery Agent
==========================================================
"""

from typing import List, Dict, Any

class JobDiscoveryAgent:
    """Discovers, retrieves, and ingests job postings across supported portals."""

    def discover_opportunities(self, role: str, location: str) -> List[Dict[str, Any]]:
        from app.services.job_service import job_service
        return job_service.filter_jobs(role_query=role, location_query=location)

job_discovery_agent = JobDiscoveryAgent()
