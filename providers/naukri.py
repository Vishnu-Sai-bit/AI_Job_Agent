"""
==========================================================
AI JobAgent - Naukri Provider (via SerpApi Aggregator)
==========================================================
"""

from typing import List
from models import JobData
from config import SERPAPI_API_KEY
from providers.serpapi import SerpApiProvider

class NaukriProvider(SerpApiProvider):
    def __init__(self):
        super().__init__()
        self.name = "Naukri"

    def search_jobs(self, role: str = "") -> List[JobData]:
        if not SERPAPI_API_KEY:
            return []

        # Target Naukri jobs specifically
        query = f"{role} site:naukri.com" if role else "Data Analyst site:naukri.com"
        jobs = super().search_jobs(role=query)
        
        # Override provider name
        for j in jobs:
            j.provider = "Naukri"
        return jobs

def search_naukri_jobs(role: str = "") -> List[JobData]:
    provider = NaukriProvider()
    return provider.search_jobs(role)
