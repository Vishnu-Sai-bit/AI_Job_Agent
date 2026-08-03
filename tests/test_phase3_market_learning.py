"""
==========================================================
AI JobAgent - Phase 3 Market Gaps & Learning Tests
==========================================================
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from models.job import JobData
from services.analytics.market_skill_aggregator import aggregate_market_skill_gaps
from services.learning.learning_engine import generate_learning_roadmap
from services.company.company_intelligence import generate_company_insights

def test_market_skill_aggregation():
    print("--- 1. Testing Market Skill Gap Aggregator ---")
    candidate_skills = ["Python", "SQL", "Tableau", "Power BI"]
    sample_jobs = [
        JobData(title="Data Analyst", skills=["SQL", "Power BI", "DAX", "Azure"]),
        JobData(title="BI Developer", skills=["Power BI", "DAX", "SQL", "Snowflake"]),
        JobData(title="Analytics Engineer", skills=["SQL", "Python", "dbt", "Snowflake"]),
        JobData(title="Junior Data Analyst", skills=["SQL", "Excel", "Tableau"])
    ]

    result = aggregate_market_skill_gaps(candidate_skills, sample_jobs)
    assert result["total_jobs_analyzed"] == 4
    assert "candidate_market_readiness" in result
    assert len(result["top_market_skills"]) > 0
    print(f"Total Jobs Analyzed: {result['total_jobs_analyzed']}")
    print(f"Market Readiness: {result['candidate_market_readiness']}%")
    print(f"High Priority Gaps: {[g['skill'] for g in result['high_priority_gaps']]}")
    print(f"Medium Priority Gaps: {[g['skill'] for g in result['medium_priority_gaps']]}")
    print("Result: Market Skill Gap Aggregator Passed [PASSED]")

def test_learning_roadmap_weekly():
    print("\n--- 2. Testing Week-by-Week Learning Roadmap & Capstone Blueprints ---")
    roadmap = generate_learning_roadmap("Data Analyst", ["Python", "SQL"])
    assert "roadmaps" in roadmap
    assert len(roadmap["roadmaps"]) > 0
    
    first_path = roadmap["roadmaps"][0]
    assert "skill" in first_path
    assert "weekly_plan" in first_path or "learning_path" in first_path
    print(f"Roadmap Skill: {first_path['skill']}")
    if "weekly_plan" in first_path:
        print(f"Weekly Modules Count: {len(first_path['weekly_plan'])}")
    if "portfolio_project_blueprint" in first_path:
        print(f"Capstone Project: {first_path['portfolio_project_blueprint']['title']}")
    print("Result: Learning Roadmap & Blueprints Passed [PASSED]")

def test_company_intelligence():
    print("\n--- 3. Testing Company Intelligence Agent ---")
    insights = generate_company_insights(
        company="Microsoft",
        role="Data Analyst",
        job_description="Seeking a Data Analyst to build enterprise Power BI dashboards and optimize SQL queries.",
        candidate_skills=["Python", "SQL", "Power BI", "Tableau"]
    )
    assert "industry_domain" in insights
    assert "detected_tech_stack" in insights
    assert len(insights["detected_tech_stack"]) > 0
    assert "recruiter_pitch_angle" in insights
    print(f"Company: {insights['company_name']}")
    print(f"Domain: {insights['industry_domain']}")
    print(f"Tech Stack: {insights['detected_tech_stack']}")
    print(f"Recruiter Hook: {insights['recruiter_pitch_angle'][:100]}...")
    print("Result: Company Intelligence Agent Passed [PASSED]")

if __name__ == "__main__":
    test_market_skill_aggregation()
    test_learning_roadmap_weekly()
    test_company_intelligence()
    print("\nALL PHASE 3 MARKET & LEARNING TESTS PASSED!")
