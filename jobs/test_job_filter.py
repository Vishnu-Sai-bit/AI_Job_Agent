from jobs.india_jobs import Job
from jobs.job_filter import filter_recommended_jobs

jobs = [

    Job(
        "Data Analyst",
        "Infosys",
        "Bangalore",
        "LinkedIn",
        ""
    ),

    Job(
        "Java Developer",
        "TCS",
        "Bangalore",
        "LinkedIn",
        ""
    ),

    Job(
        "Business Analyst",
        "Accenture",
        "Hyderabad",
        "Naukri",
        ""
    ),

    Job(
        "Python Developer",
        "Google",
        "California",
        "LinkedIn",
        ""
    )

]

recommended = filter_recommended_jobs(jobs)

for job in recommended:
    print(job)