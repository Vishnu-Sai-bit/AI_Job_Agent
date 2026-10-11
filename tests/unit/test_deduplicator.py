"""
==========================================================
Unit Tests - Deduplicator
==========================================================
"""

from job_sources.deduplicator import deduplicate_jobs

def test_deduplicate_jobs():
    raw_list = [
        {"title": "Data Analyst", "company": "Google"},
        {"title": "Data Analyst", "company": "Google"},
        {"title": "Data Analyst", "company": "Microsoft"}
    ]
    unique = deduplicate_jobs(raw_list)
    assert len(unique) == 2
