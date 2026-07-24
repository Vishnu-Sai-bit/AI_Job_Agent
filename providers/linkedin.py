"""
==========================================================
AI JobAgent - LinkedIn Provider (via SerpApi Aggregator)
==========================================================
"""

from typing import List
from models import JobData
from config import SERPAPI_API_KEY
from providers.serpapi import SerpApiProvider

class LinkedInProvider(SerpApiProvider):
    def __init__(self):
        super().__init__()
        self.name = "LinkedIn"

    def search_jobs(self, role: str = "") -> List[JobData]:
        if not SERPAPI_API_KEY:
            return []

        # Target LinkedIn jobs specifically using Google Jobs syntax
        query = f"{role} site:linkedin.com/jobs" if role else "Data Analyst site:linkedin.com/jobs"
        jobs = super().search_jobs(role=query)
        
        # Override provider name
        for j in jobs:
            j.provider = "LinkedIn"
        return jobs

def search_linkedin_jobs(role: str = "") -> List[JobData]:
    provider = LinkedInProvider()
    return provider.search_jobs(role)
