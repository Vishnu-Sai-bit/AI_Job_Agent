from dataclasses import dataclass


@dataclass
class Job:

    title: str
    company: str
    location: str
    source: str
    url: str


INDIAN_CITIES = [

    "Bangalore",
    "Bengaluru",
    "Hyderabad",
    "Chennai",
    "Pune",
    "Noida",
    "Gurgaon",
    "Gurugram",
    "Delhi",
    "Mumbai",
    "Kolkata",
    "Ahmedabad",
    "Coimbatore",
    "Kochi",
    "Trivandrum",
    "Visakhapatnam",
    "Remote",
    "India",
    "India (Remote)",
    "Remote - India",
    "Work From Home",
    "WFH"

]


def is_indian_job(location: str):

    if not location or not location.strip():

        return False

    location = location.lower()

    return any(

        city.lower() in location

        for city in INDIAN_CITIES

    )


def filter_jobs(job_list):

    return [

        job

        for job in job_list

        if is_indian_job(job.location)

    ]