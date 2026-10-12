"""
==========================================================
AI JobAgent - Indeed Provider (via SerpApi Aggregator)
==========================================================
"""

from typing import List
from models import JobData
from config import SERPAPI_API_KEY
from providers.serpapi import SerpApiProvider

class IndeedProvider(SerpApiProvider):
    def __init__(self):
        super().__init__()
        self.name = "Indeed"

    def search_jobs(self, role: str = "") -> List[JobData]:
        if not SERPAPI_API_KEY:
            return []

        # Target Indeed jobs specifically
        query = f"{role} site:indeed.com" if role else "Data Analyst site:indeed.com"
        jobs = super().search_jobs(role=query)
        
        # Override provider name
        for j in jobs:
            j.provider = "Indeed"
        return jobs

def search_indeed_jobs(role: str = "") -> List[JobData]:
    provider = IndeedProvider()
    return provider.search_jobs(role)
