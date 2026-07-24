"""
==========================================================
AI JobAgent - Foundit Provider (via SerpApi Aggregator)
==========================================================
"""

from typing import List
from models import JobData
from config import SERPAPI_API_KEY
from providers.serpapi import SerpApiProvider

class FounditProvider(SerpApiProvider):
    def __init__(self):
        super().__init__()
        self.name = "Foundit"

    def search_jobs(self, role: str = "") -> List[JobData]:
        if not SERPAPI_API_KEY:
            return []

        # Target Foundit jobs specifically
        query = f"{role} site:foundit.in" if role else "Data Analyst site:foundit.in"
        jobs = super().search_jobs(role=query)
        
        # Override provider name
        for j in jobs:
            j.provider = "Foundit"
        return jobs

def search_foundit_jobs(role: str = "") -> List[JobData]:
    provider = FounditProvider()
    return provider.search_jobs(role)
