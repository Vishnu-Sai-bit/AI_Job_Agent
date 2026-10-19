import pytest
from services.ats_scorer import ATSScorer
from services.resume_parser import ResumeParser
from tests.test_resume_parser import SAMPLE_RESUME

def test_ats_scorer_complete_resume():
    parser = ResumeParser()
    data = parser.parse(SAMPLE_RESUME)
    
    scorer = ATSScorer()
    report = scorer.score_resume(SAMPLE_RESUME, data)
    
    assert report["overall_score"] >= 70.0
    assert report["tier"] in ["Strong", "Excellent"]
    assert "breakdown" in report
    assert report["breakdown"]["readability"] > 0
    assert report["breakdown"]["completeness"] >= 80

def test_ats_scorer_empty_resume():
    scorer = ATSScorer()
    report = scorer.score_resume("", {})
    
    assert report["overall_score"] < 50.0
    assert report["tier"] == "Needs Improvement"
    assert len(report["missing_sections"]) > 0
