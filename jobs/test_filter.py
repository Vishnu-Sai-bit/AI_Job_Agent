from jobs.india_jobs import Job, filter_jobs

jobs = [
    Job(
        title="Data Analyst",
        company="Infosys",
        location="Bangalore",
        source="LinkedIn",
        url=""
    ),

    Job(
        title="Data Scientist",
        company="Google",
        location="California",
        source="LinkedIn",
        url=""
    ),

    Job(
        title="Business Analyst",
        company="Accenture",
        location="Hyderabad",
        source="Naukri",
        url=""
    )
]

print("Total Jobs:", len(jobs))

filtered = filter_jobs(jobs)

print("Filtered Jobs:", len(filtered))

for job in filtered:
    print(job)