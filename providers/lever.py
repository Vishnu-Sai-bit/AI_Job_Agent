"""
==========================================================
AI JobAgent - Lever Provider (via SerpApi Aggregator)
==========================================================
"""

from typing import List
from models import JobData
from config import SERPAPI_API_KEY
from providers.serpapi import SerpApiProvider

class LeverProvider(SerpApiProvider):
    def __init__(self):
        super().__init__()
        self.name = "Lever"

    def search_jobs(self, role: str = "") -> List[JobData]:
        if not SERPAPI_API_KEY:
            return []

        # Target Lever boards specifically
        query = f"{role} site:jobs.lever.co" if role else "Data Analyst site:jobs.lever.co"
        jobs = super().search_jobs(role=query)
        
        # Override provider name
        for j in jobs:
            j.provider = "Lever"
        return jobs

def search_lever_jobs(role: str = "") -> List[JobData]:
    provider = LeverProvider()
    return provider.search_jobs(role)
