from dataclasses import dataclass


@dataclass
class Job:
    title: str
    company: str
    location: str
    source: str
    url: str
    skills: str = ""
    salary: str = ""
    posted_date: str = ""