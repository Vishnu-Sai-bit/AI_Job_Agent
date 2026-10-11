"""
==========================================================
Job Sources - Direct Company Careers
==========================================================
"""

from typing import List, Dict, Any
from job_sources.base import BaseJobSource

class CompanyCareersSource(BaseJobSource):
    @property
    def source_name(self) -> str:
        return "CompanyCareers"

    def fetch_jobs(self, role: str, location: str) -> List[Dict[str, Any]]:
        # Structured corporate board direct ingestion
        return []
