import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from models import ResumeData, JobData
from services.jobs.search_jobs import is_india_or_remote_job
from services.matcher.job_matcher import match_jobs, role_match

# -----------------------------------------------------------------------------
# Test Data
# -----------------------------------------------------------------------------
resume = ResumeData(
    name="Beere Vishnu Sai",
    preferred_role="Data Analyst",
    preferred_location="Hyderabad",
    experience_years=2,
    skills=["Python", "SQL", "Tableau", "Power BI"]
)

# A set of test jobs representing different scenarios
test_jobs = [
    # 1. Preferred role match in India
    JobData(title="Data Analyst", company="Scout Inc", location="Hyderabad, India", description="Requirement: Python, SQL", provider="Adzuna"),
    
    # 2. Skill-related job in India (no Data Analyst in title)
    JobData(title="Python Developer", company="CodeTech", location="Hyderabad, India", description="Requirement: Python, Django, SQL", provider="Jooble"),
    
    # 3. Generic "India" location job with city in description
    JobData(title="Junior Data Analyst", company="GlobalCorp", location="India", description="This position is based in our Bangalore office. Requirements: Python, SQL", skills=["Python", "SQL"], provider="JSearch"),
    
    # 4. Foreign job (should be filtered out)
    JobData(title="Data Analyst", company="USCorp", location="Toronto, Canada", description="Based in Canada.", provider="TheMuse"),
    
    # 5. Worldwide remote job (should be filtered out)
    JobData(title="Data Analyst", company="RemoteOK", location="Worldwide", description="Remote worldwide job.", provider="RemoteOK"),
    
    # 6. Irrelevant job (should score below 50% and be filtered out)
    JobData(title="Mechanical Engineer", company="HeavyMech", location="Hyderabad, India", description="HVAC systems.", provider="Adzuna")
]

# -----------------------------------------------------------------------------
# 1. Test India-Only Location Filter
# -----------------------------------------------------------------------------
print("--- 1. Testing India-Only Location Filter ---")
filtered_jobs = [j for j in test_jobs if is_india_or_remote_job(j.location)]
filtered_locations = [j.location for j in filtered_jobs]
print("Filtered Locations remaining:", filtered_locations)
assert "Toronto, Canada" not in filtered_locations, "Foreign jobs should be excluded"
assert "Worldwide" not in filtered_locations, "Worldwide remote jobs should be excluded"
print("Result: India-Only Location Filter Passed [PASSED]")

# -----------------------------------------------------------------------------
# 2. Test Priority Role Matching (Skills vs Preferred Role)
# -----------------------------------------------------------------------------
print("\n--- 2. Testing Priority Role Matching ---")
# Data Analyst match score
da_job = JobData(title="Data Analyst", company="Test")
da_score = role_match(resume, da_job)
print(f"Role match score for 'Data Analyst': {da_score}%")
assert da_score == 100.0, "Preferred role should score 100%"

# Python Developer (skill-based fallback) match score
python_job = JobData(title="Python Developer", company="Test")
py_score = role_match(resume, python_job)
print(f"Role match score for 'Python Developer': {py_score}%")
assert py_score == 100.0, "Skill-based role should score 100%"

# Irrelevant match score
irrelevant_job = JobData(title="Mechanical Engineer", company="Test")
irr_score = role_match(resume, irrelevant_job)
print(f"Role match score for 'Mechanical Engineer': {irr_score}%")
assert irr_score == 0.0, "Irrelevant role should score 0%"
print("Result: Priority Role Matching Passed [PASSED]")

# -----------------------------------------------------------------------------
# 3. Test Full Match and Grouping Engine
# -----------------------------------------------------------------------------
print("\n--- 3. Testing Full Search & Grouping ---")
# Temporarily lower score threshold or run match
matched = match_jobs(resume, filtered_jobs)

# Apply match score filter (>= 50)
from services.jobs.search_jobs import filter_match_score
good_matches = filter_match_score(matched, 50.0)

print("Matched jobs above 50% threshold:")
for j in good_matches:
    print(f" * Title: {j.title} | Company: {j.company} | Location: {j.location} | Match Score: {j.match_score}%")

# Assert mechanical engineer is filtered out
titles = [j.title for j in good_matches]
assert "Mechanical Engineer" not in titles, "Irrelevant jobs scoring < 50% should be filtered out"
assert "Python Developer" in titles, "Skill-based fallback jobs scoring >= 50% should be matched"
print("Result: Score Threshold & Fallback Matching Passed [PASSED]")

# -----------------------------------------------------------------------------
# 4. Test Smart City Grouping (Generic "India" -> specific city)
# -----------------------------------------------------------------------------
print("\n--- 4. Testing Smart City Parser ---")
# Group jobs by city
grouped_jobs = {}
from services.resume.location_parser import is_remote, CITY_ALIASES
from config import DEFAULT_LOCATIONS

for job in good_matches:
    loc_lower = (job.location or "").lower()
    city_found = None
    for city in DEFAULT_LOCATIONS:
        if city.lower() in loc_lower:
            city_found = city
            break
            
    if not city_found:
        search_text = ((job.location or "") + " " + (job.title or "") + " " + (job.description or "")).lower()
        for city in DEFAULT_LOCATIONS:
            city_key = city.lower()
            if city_key in search_text:
                city_found = city
                break
            for alias, canonical in CITY_ALIASES.items():
                if canonical.lower() == city_key and alias in search_text:
                    city_found = city
                    break
                    
    if job.remote or is_remote(job.location or ""):
        group_name = "Remote"
    elif city_found:
        group_name = city_found
    else:
        group_name = "Other India Locations"
        
    if group_name not in grouped_jobs:
        grouped_jobs[group_name] = []
    grouped_jobs[group_name].append(job)

print("Grouped Jobs:")
for city, jobs in grouped_jobs.items():
    print(f" * {city}: {[j.company for j in jobs]}")

# Assert GlobalCorp (location "India", desc "Bangalore office") is grouped under "Bengaluru"
bengaluru_companies = [j.company for j in grouped_jobs.get("Bengaluru", [])]
assert "GlobalCorp" in bengaluru_companies, "Generic 'India' job with 'Bangalore' in description should be grouped under Bengaluru"
print("Result: Smart City Parser Grouping Passed [PASSED]")

print("\nALL 5 POINTS SUCCESSFULLY VERIFIED AND PASSED!")
