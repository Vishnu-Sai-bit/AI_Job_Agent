"""
==========================================================
Unit Tests - Resume Parser & ATS Engine
==========================================================
"""

from services.resume.skill_extractor import extract_skills as extract_skills_from_text

def test_extract_skills_from_text():
    sample = "Experienced Data Analyst with strong Python, SQL, and Tableau capabilities."
    skills = extract_skills_from_text(sample)
    assert "Python" in skills
    assert "Sql" in skills or "SQL" in skills
    assert "Tableau" in skills
