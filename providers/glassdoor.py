"""
==========================================================
AI JobAgent - Glassdoor Provider (via SerpApi Aggregator)
==========================================================
"""

from typing import List
from models import JobData
from config import SERPAPI_API_KEY
from providers.serpapi import SerpApiProvider

class GlassdoorProvider(SerpApiProvider):
    def __init__(self):
        super().__init__()
        self.name = "Glassdoor"

    def search_jobs(self, role: str = "") -> List[JobData]:
        if not SERPAPI_API_KEY:
            return []

        # Target Glassdoor jobs specifically
        query = f"{role} site:glassdoor.com" if role else "Data Analyst site:glassdoor.com"
        jobs = super().search_jobs(role=query)
        
        # Override provider name
        for j in jobs:
            j.provider = "Glassdoor"
        return jobs

def search_glassdoor_jobs(role: str = "") -> List[JobData]:
    provider = GlassdoorProvider()
    return provider.search_jobs(role)
