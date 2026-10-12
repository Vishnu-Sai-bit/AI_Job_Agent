"""
==========================================================
AI JobAgent - Wellfound Provider (via SerpApi Aggregator)
==========================================================
"""

from typing import List
from models import JobData
from config import SERPAPI_API_KEY
from providers.serpapi import SerpApiProvider

class WellfoundProvider(SerpApiProvider):
    def __init__(self):
        super().__init__()
        self.name = "Wellfound"

    def search_jobs(self, role: str = "") -> List[JobData]:
        if not SERPAPI_API_KEY:
            return []

        # Target Wellfound jobs specifically
        query = f"{role} site:wellfound.com/jobs" if role else "Data Analyst site:wellfound.com/jobs"
        jobs = super().search_jobs(role=query)
        
        # Override provider name
        for j in jobs:
            j.provider = "Wellfound"
        return jobs

def search_wellfound_jobs(role: str = "") -> List[JobData]:
    provider = WellfoundProvider()
    return provider.search_jobs(role)
