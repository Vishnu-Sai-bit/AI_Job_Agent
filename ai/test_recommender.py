from ai.recommender import JobRecommender

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
        "title": "Machine Learning Engineer",
        "company": "Microsoft",
        "location": "Bangalore",
        "skills": [
            "Python",
            "Machine Learning",
            "Azure",
            "SQL"
        ]
    }

]

recommender = JobRecommender(
    resume_skills,
    jobs
)

print("=" * 60)
print("Recommended Jobs")
print("=" * 60)

for job in recommender.recommend():

    print()

    print(job["title"])

    print(job["company"])

    print(job["location"])

    print("ATS Score:", job["score"], "%")