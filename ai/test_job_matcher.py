from ai.job_matcher import JobMatcher

resume_skills = [
    "Python",
    "SQL",
    "Power BI",
    "Tableau",
    "Excel"
]

jobs = [

    {
        "title": "Data Analyst",
        "company": "Infosys",
        "location": "Bangalore",
        "skills": [
            "Python",
            "SQL",
            "Power BI",
            "Tableau"
        ]
    },

    {
        "title": "Business Analyst",
        "company": "Accenture",
        "location": "Hyderabad",
        "skills": [
            "Excel",
            "SQL",
            "Communication"
        ]
    },

    {
        "title": "Python Developer",
        "company": "Google",
        "location": "California",
        "skills": [
            "Python",
            "Django",
            "AWS"
        ]
    }

]

results = JobMatcher.rank_jobs(
    resume_skills,
    jobs
)

for job in results:

    print("=" * 40)

    print(job["title"])

    print(job["company"])

    print(job["location"])

    print("Score:", job["score"], "%")

    print("Matched:", job["matched"])

    print("Missing:", job["missing"])