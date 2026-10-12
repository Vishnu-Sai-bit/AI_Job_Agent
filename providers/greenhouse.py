"""
==========================================================
AI JobAgent - Greenhouse Provider (via SerpApi Aggregator)
==========================================================
"""

from typing import List
from models import JobData
from config import SERPAPI_API_KEY
from providers.serpapi import SerpApiProvider

class GreenhouseProvider(SerpApiProvider):
    def __init__(self):
        super().__init__()
        self.name = "Greenhouse"

    def search_jobs(self, role: str = "") -> List[JobData]:
        if not SERPAPI_API_KEY:
            return []

        # Target Greenhouse boards specifically
        query = f"{role} site:boards.greenhouse.io" if role else "Data Analyst site:boards.greenhouse.io"
        jobs = super().search_jobs(role=query)
        
        # Override provider name
        for j in jobs:
            j.provider = "Greenhouse"
        return jobs

def search_greenhouse_jobs(role: str = "") -> List[JobData]:
    provider = GreenhouseProvider()
    return provider.search_jobs(role)
