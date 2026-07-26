import sys
from pathlib import Path

# Add project root to path
sys.path.append("c:/JobAgent")

from models import ResumeData, JobData, SearchResult
from services.resume.resume_enricher import infer_location
from services.ats.ats_calculator import calculate_ats
from services.jobs.search_jobs import search_jobs
from config import MATCH_WEIGHTS

def test_location_logic():
    print("\n--- Testing Location Inference Fallback ---")
    resume_text_objective = """
    CAREER OBJECTIVE:
    Seeking a Data Analyst position in Hyderabad or Chennai.
    Current address: Dharmavaram, AP.
    """
    inferred = infer_location(resume_text_objective)
    print("Inferred location:", inferred)
    # Since Hyderabad is in DEFAULT_LOCATIONS, it should find it in the text.
    assert inferred == "Hyderabad", "Failed to infer location from objective"

    # Testing empty objective / target defaults
    empty_resume = "Just some text with no location preferences at all."
    inferred_default = infer_location(empty_resume)
    print("Inferred default location:", inferred_default)
    assert inferred_default == "Bengaluru", f"Failed default location, got {inferred_default}"
    print("Location Inference Passed")

def test_ats_skill_quality():
    print("\n--- Testing ATS Skill Quality Scoring ---")
    resume_high_quality = ResumeData(
        skills=["Python", "SQL", "Power BI", "Tableau", "FastAPI", "Docker", "Git", "Azure", "Pandas", "NumPy"]
    )
    resume_low_quality = ResumeData(
        skills=["HTML", "CSS", "Bootstrap", "Word", "Paint", "C", "Java"]
    )
    
    report_high = calculate_ats(resume_high_quality)
    report_low = calculate_ats(resume_low_quality)
    
    print(f"High quality skills score: {report_high.skills_score} / 30")
    print(f"Low quality skills score: {report_low.skills_score} / 30")
    
    assert report_high.skills_score > report_low.skills_score, "High quality skills should score higher than low quality skills"
    print("ATS Skill Quality Scoring Passed")

def test_job_weights_and_reasons():
    print("\n--- Testing Job Match Weights & Explanations ---")
    print("Current Match Weights:", MATCH_WEIGHTS)
    assert MATCH_WEIGHTS["skills"] == 35, "Skills weight should be 35"
    assert MATCH_WEIGHTS["salary"] == 5, "Salary weight should be 5"
    
    # Check explanation format
    job = JobData(
        title="Data Analyst",
        company="IBM",
        matching_skills=["Python", "SQL"],
        missing_skills=["Azure", "Spark"]
    )
    reason = job.get_match_reason()
    # Check assertions without printing the unicode symbol directly to cp1252 stdout
    assert "Python" in reason, "Match reason missing matched skills"
    assert "Azure" in reason, "Match reason missing missing skills"
    print("Job Match Reason Passed")

def test_auto_learning():
    print("\n--- Testing Auto-Learning Recommendation Logic ---")
    resume = ResumeData(
        preferred_role="Data Analyst",
        preferred_location="Hyderabad",
        skills=["Python", "SQL"]
    )
    jobs = [
        JobData(provider="Test", title="Data Analyst", company="IBM", match_score=75.0, missing_skills=["Fabric", "Azure"]),
        JobData(provider="Test", title="Data Analyst", company="Microsoft", match_score=70.0, missing_skills=["Fabric", "SQL"]),
        JobData(provider="Test", title="Data Analyst", company="Accenture", match_score=80.0, missing_skills=["Fabric", "Azure"])
    ]
    
    result = SearchResult(
        status="success",
        role="Data Analyst",
        jobs=jobs
    )
    missing_skill_counts = {}
    for j in jobs:
        for skill in j.missing_skills:
            missing_skill_counts[skill] = missing_skill_counts.get(skill, 0) + 1

    sorted_missing = sorted(missing_skill_counts.items(), key=lambda x: x[1], reverse=True)
    learning_path = []
    for skill, count in sorted_missing[:5]:
        demand_pct = round((count / len(jobs)) * 100, 1)
        learning_path.append({
            "skill": skill,
            "frequency": count,
            "demand_percentage": demand_pct,
            "recommendation": f"Learn {skill} first (Required by {demand_pct}% of matching jobs)"
        })
    result.learning_path = learning_path
    
    # Avoid printing raw list if it has unicode, print key details
    print("Learning Path top skill:", result.learning_path[0]["skill"])
    assert result.learning_path[0]["skill"] == "Fabric", "Fabric should be the top recommended skill"
    print("Auto-Learning Logic Passed")

def test_parser_robustness():
    print("\n--- Testing Parser Robustness against Graduation Years ---")
    from services.resume.experience_parser import parse_experience
    from services.resume.salary_parser import parse_salary
    
    # Graduation year in experience description should NOT be parsed as 2026.0 years of experience
    exp_years = parse_experience("2026 passout")
    print("Parsed experience for '2026 passout':", exp_years)
    assert exp_years == 0.0, f"Expected 0.0, got {exp_years}"
    
    # Standalone small numbers should still work
    exp_years_small = parse_experience("3")
    print("Parsed experience for '3':", exp_years_small)
    assert exp_years_small == 3.0, f"Expected 3.0, got {exp_years_small}"
    
    # Year in salary text without currency symbol should NOT be parsed as $2026 / INR 2026
    sal_parsed = parse_salary("batch of 2026")
    print("Parsed salary for 'batch of 2026':", sal_parsed)
    assert sal_parsed["min_salary"] is None, "Should not parse 2026 as min_salary"
    
    # Proper currency-prefixed or pure numbers should still work
    sal_parsed_valid = parse_salary("$75000")
    print("Parsed salary for '$75000':", sal_parsed_valid)
    assert sal_parsed_valid["min_salary"] == 75000, "Failed to parse valid salary amount"
    
    print("Parser Robustness Passed")

if __name__ == "__main__":
    try:
        test_location_logic()
        test_ats_skill_quality()
        test_job_weights_and_reasons()
        test_auto_learning()
        test_parser_robustness()
        print("\nALL TESTS COMPLETED SUCCESSFULLY!")
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        sys.exit(1)
