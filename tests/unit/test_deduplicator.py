"""
==========================================================
Unit Tests - Deduplicator
==========================================================
"""

from models.job import JobData
from services.job.job_deduplicator import deduplicate_jobs

def test_deduplicate_jobs():
    raw_list = [
        JobData(title="Data Analyst", company="Google", location="Bangalore", apply_url="https://google.com/1"),
        JobData(title="Data Analyst", company="Google Inc", location="Bangalore", apply_url="https://google.com/2"),
        JobData(title="Data Analyst", company="Microsoft", location="Hyderabad", apply_url="https://microsoft.com/1")
    ]
    unique = deduplicate_jobs(raw_list)
    assert len(unique) == 2
