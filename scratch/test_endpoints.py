"""
==========================================================
AI JobAgent - Test FastAPI Endpoints Script
Author : Antigravity
==========================================================
"""

import requests

BASE_URL = "http://127.0.0.1:8000"

def test_endpoints():
    print("--- 1. Testing /generate-cover-letter ---")
    res1 = requests.post(f"{BASE_URL}/generate-cover-letter", json={
        "name": "Beere Vishnu Sai",
        "skills": ["Python", "SQL", "Power BI"],
        "job_title": "Data Analyst",
        "company": "Google",
        "job_desc": "Looking for a Data Analyst proficient in SQL and visualization."
    })
    print("Status Code:", res1.status_code)
    if res1.status_code == 200:
        print("Success: Salutation =", res1.json().get("salutation"))
    
    print("\n--- 2. Testing /generate-interview-questions ---")
    res2 = requests.post(f"{BASE_URL}/generate-interview-questions", json={
        "role": "Data Analyst",
        "skills": ["Python", "SQL"]
    })
    print("Status Code:", res2.status_code)
    if res2.status_code == 200:
        print("Success: First Question =", res2.json().get("questions", [{}])[0].get("question"))
        
    print("\n--- 3. Testing /generate-learning-roadmap ---")
    res3 = requests.post(f"{BASE_URL}/generate-learning-roadmap", json={
        "role": "Data Analyst",
        "skills": ["Python"]
    })
    print("Status Code:", res3.status_code)
    if res3.status_code == 200:
        print("Success: Skill gaps =", res3.json().get("skill_gaps"))

    print("\n--- 4. Testing /predict-salary ---")
    res4 = requests.post(f"{BASE_URL}/predict-salary", json={
        "role": "Data Analyst",
        "experience_years": 2.0,
        "skills": ["Python", "SQL"],
        "location": "Hyderabad"
    })
    print("Status Code:", res4.status_code)
    if res4.status_code == 200:
        print("Success: Median salary =", res4.json().get("median"))

    print("\n--- 5. Testing /optimize-linkedin ---")
    res5 = requests.post(f"{BASE_URL}/optimize-linkedin", json={
        "name": "Beere Vishnu Sai",
        "role": "Data Analyst",
        "skills": ["Python", "SQL"],
        "experience_text": "Worked as a Data Analyst Intern."
    })
    print("Status Code:", res5.status_code)
    if res5.status_code == 200:
        print("Success: Suggested Headlines =", res5.json().get("suggested_headlines", [])[0])

    print("\n--- 6. Testing /generate-emails ---")
    res6 = requests.post(f"{BASE_URL}/generate-emails", json={
        "name": "Beere Vishnu Sai",
        "skills": ["Python", "SQL"],
        "role": "Data Analyst",
        "company": "Amazon"
    })
    print("Status Code:", res6.status_code)
    if res6.status_code == 200:
        print("Success: Cold Outreach Subject =", res6.json().get("cold_outreach", {}).get("subject"))

if __name__ == "__main__":
    try:
        test_endpoints()
    except Exception as e:
        print("Connection error to FastAPI:", e)
