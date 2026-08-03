from jobs.india_jobs import filter_jobs


PREFERRED_KEYWORDS = [

    "data analyst",
    "business analyst",
    "data scientist",
    "analytics",
    "python",
    "sql",
    "power bi",
    "tableau",
    "excel"

]


def keyword_match(job):

    text = (
        job.title +
        " " +
        job.company +
        " " +
        job.location +
        " " +
        job.source
    ).lower()

    return any(
        keyword in text
        for keyword in PREFERRED_KEYWORDS
    )


def filter_recommended_jobs(job_list):

    indian_jobs = filter_jobs(job_list)

    return [

        job

        for job in indian_jobs

        if keyword_match(job)

    ]