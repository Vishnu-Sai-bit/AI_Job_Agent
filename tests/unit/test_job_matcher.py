"""
==========================================================
Unit Tests - Job Matcher & Scoring
==========================================================
"""

from app.services.matching_service import matching_service

def test_calculate_match():
    job = {
        "title": "Data Analyst",
        "skills": ["Python", "SQL", "Tableau"]
    }
    candidate = {
        "preferred_role": "Data Analyst",
        "skills": ["Python", "SQL", "Excel"]
    }
    result = matching_service.calculate_match(job, candidate)
    assert result["score"] >= 70.0
    assert "Python" in result["matching_skills"]
