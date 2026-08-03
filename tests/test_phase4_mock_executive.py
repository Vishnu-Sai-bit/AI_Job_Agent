"""
==========================================================
AI JobAgent - Phase 4 Mock Interview & Executive Tests
==========================================================
"""

import sys
from pathlib import Path

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from models.resume import ResumeData
from models.job import JobData
from services.interview.mock_evaluator import evaluate_mock_answer
from services.analytics.career_intelligence import generate_career_overview
from app import (
    api_evaluate_mock_answer,
    api_career_overview,
    EvaluateAnswerRequest,
    CareerOverviewRequest
)

def test_mock_interview_evaluator_live():
    print("--- 1. Testing Interactive Mock Interview Evaluator ---")
    question = "How do you handle missing values and outliers in a customer churn dataset using Python and SQL?"
    candidate_answer = (
        "In my customer churn project with 30,000 records, I used SQL queries with IS NULL and COALESCE to identify missing fields. "
        "For outliers, I calculated the IQR using Python Pandas and replaced extreme anomalies with median values. "
        "This improved my XGBoost model accuracy to 82%."
    )

    result = evaluate_mock_answer(
        question=question,
        candidate_answer=candidate_answer,
        role="Data Analyst",
        interviewer_role="Senior Technical Recruiter",
        resume_context="Data analytics background with SQL, Python, Tableau, Power BI"
    )

    assert "overall_score" in result
    assert "dimension_scores" in result
    assert "technical_correctness" in result["dimension_scores"]
    assert "structure_star" in result["dimension_scores"]
    assert "relevance" in result["dimension_scores"]
    assert "clarity" in result["dimension_scores"]
    assert "strengths" in result
    assert len(result["strengths"]) > 0
    assert "refined_model_answer" in result

    print(f"Overall Score: {result['overall_score']}/10")
    print(f"Dimension Scores: {result['dimension_scores']}")
    print(f"Strengths: {result['strengths']}")
    print(f"Refined Answer: {result['refined_model_answer'][:100]}...")
    print("Result: Mock Interview Evaluator Passed [PASSED]")

def test_mock_interview_evaluator_brief_fallback():
    print("\n--- 2. Testing Short/Empty Answer Rubric Handling ---")
    result = evaluate_mock_answer(
        question="Explain SQL indexing.",
        candidate_answer="no",
        role="Data Analyst"
    )
    assert result["overall_score"] <= 4.0
    assert len(result["improvement_areas"]) > 0
    print(f"Short Answer Score: {result['overall_score']}")
    print(f"Feedback: {result['improvement_areas']}")
    print("Result: Short Answer Handling Passed [PASSED]")

def test_career_intelligence_overview():
    print("\n--- 3. Testing Executive Career Intelligence & Pipeline Funnel ---")
    resume = ResumeData(
        name="Beere Vishnu Sai",
        email="vishnu@example.com",
        skills=["Python", "SQL", "Power BI", "Tableau", "Excel", "Data Modeling", "EDA"],
        preferred_role="Data Analyst",
        certifications=["Oracle Cloud Infrastructure 2025 Certified AI Foundations Associate"],
        projects=[
            {"title": "EV Charging Station Analysis", "description": "Tableau dashboard for 30k records"},
            {"title": "Customer Churn Prediction", "description": "Machine learning with 82% accuracy"}
        ]
    )

    jobs = [
        JobData(title="Data Analyst", skills=["SQL", "Power BI", "Python"]),
        JobData(title="BI Developer", skills=["Power BI", "DAX", "SQL"])
    ]

    overview = generate_career_overview(resume, jobs)

    assert "pipeline_funnel" in overview
    assert "role_track_readiness" in overview
    assert "Data Analyst" in overview["role_track_readiness"]
    assert "BI Analyst" in overview["role_track_readiness"]
    assert "top_verified_strengths" in overview
    assert len(overview["top_verified_strengths"]) > 0
    assert "market_standing_summary" in overview

    print(f"Candidate: {overview['candidate_name']}")
    print(f"Funnel Discovered: {overview['pipeline_funnel']['jobs_discovered']}")
    print(f"Verified Opportunities: {overview['pipeline_funnel']['verified_opportunities']}")
    print(f"Role Track Readiness: {overview['role_track_readiness']}")
    print(f"Top Strengths: {overview['top_verified_strengths']}")
    print(f"Summary: {overview['market_standing_summary'][:100]}...")
    print("Result: Executive Career Intelligence Passed [PASSED]")

def test_fastapi_endpoints_phase4():
    print("\n--- 4. Testing Phase 4 FastAPI Endpoints & Schema Validation ---")
    
    # 1. /interview/evaluate-answer
    req_eval = EvaluateAnswerRequest(
        question="What is the difference between WHERE and HAVING in SQL?",
        candidate_answer="WHERE filters rows before grouping, whereas HAVING filters aggregated groups after GROUP BY.",
        role="Data Analyst",
        interviewer_role="Senior Technical Recruiter"
    )
    eval_json = api_evaluate_mock_answer(req_eval)
    assert "overall_score" in eval_json
    print(f"api_evaluate_mock_answer executed: Score {eval_json['overall_score']}/10")

    # 2. /analytics/career-overview
    req_overview = CareerOverviewRequest(
        resume_data={
            "name": "Beere Vishnu Sai",
            "skills": ["Python", "SQL", "Tableau", "Power BI"],
            "preferred_role": "Data Analyst"
        },
        jobs=[]
    )
    overview_json = api_career_overview(req_overview)
    assert "role_track_readiness" in overview_json
    print(f"api_career_overview executed: Tracks: {list(overview_json['role_track_readiness'].keys())}")
    print("Result: Phase 4 Endpoints Passed [PASSED]")

if __name__ == "__main__":
    test_mock_interview_evaluator_live()
    test_mock_interview_evaluator_brief_fallback()
    test_career_intelligence_overview()
    test_fastapi_endpoints_phase4()
    print("\nALL PHASE 4 MOCK EVALUATION & EXECUTIVE INTELLIGENCE TESTS PASSED!")
