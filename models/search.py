"""
==========================================================
AI JobAgent - Search Result Model
Author : Beere Vishnu Sai

Description:
    Search result model used across the application.
==========================================================
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any

from .job import JobData


# ==========================================================
# Search Result Model
# ==========================================================

@dataclass
class SearchResult:
    """
    Represents the complete output of a job search.
    """

    # ------------------------------------------------------
    # Search Status
    # ------------------------------------------------------

    status: str = "success"

    message: str = ""

    # ------------------------------------------------------
    # Search Information
    # ------------------------------------------------------

    role: str = ""

    location: str = ""

    work_type: str = ""

    experience: str = ""

    posted_days: int = 30

    limit: int = 10

    # ------------------------------------------------------
    # Search Statistics
    # ------------------------------------------------------

    total_jobs_found: int = 0

    total_jobs_returned: int = 0

    providers_used: List[str] = field(default_factory=list)

    failed_providers: List[str] = field(default_factory=list)

    search_time: float = 0.0

    # ------------------------------------------------------
    # Results
    # ------------------------------------------------------

    jobs: List[JobData] = field(default_factory=list)

    grouped_jobs: Dict[str, Any] = field(default_factory=dict)

    learning_path: List[Dict[str, Any]] = field(default_factory=list)

    # ------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert SearchResult object to dictionary.
        """

        return {

            "status": self.status,

            "message": self.message,

            "role": self.role,

            "location": self.location,

            "work_type": self.work_type,

            "experience": self.experience,

            "posted_days": self.posted_days,

            "limit": self.limit,

            "total_jobs_found": self.total_jobs_found,

            "total_jobs_returned": self.total_jobs_returned,

            "providers_used": self.providers_used,

            "failed_providers": self.failed_providers,

            "search_time": self.search_time,

            "jobs": [

                job.to_dict()

                if hasattr(job, "to_dict")

                else job

                for job in self.jobs

            ],

            "grouped_jobs": self.grouped_jobs,

            "learning_path": self.learning_path

        }

    # ------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ):

        jobs = [

            JobData.from_dict(job)

            if isinstance(job, dict)

            else job

            for job in data.get("jobs", [])

        ]

        data["jobs"] = jobs

        return cls(**data)

    # ------------------------------------------------------

    def add_job(
        self,
        job: JobData,
    ):

        if not isinstance(job, JobData):

            return

        for existing in self.jobs:

            if (

                (existing.title or "").lower() == (job.title or "").lower()

                and

                (existing.company or "").lower() == (job.company or "").lower()

            ):

                return

        self.jobs.append(job)

        self.total_jobs_returned = len(self.jobs)

    # ------------------------------------------------------

    def add_provider(
        self,
        provider: str,
    ):

        if not provider:

            return

        provider = provider.strip()

        if provider.lower() not in {

            p.lower()

            for p in self.providers_used

        }:

            self.providers_used.append(provider)

    # ------------------------------------------------------

    def total_providers(self) -> int:
        """
        Number of providers used.
        """

        return len(self.providers_used)

    # ------------------------------------------------------

    def clear_jobs(self):

        self.jobs.clear()

        self.grouped_jobs.clear()

        self.total_jobs_returned = 0

    # ------------------------------------------------------

    def has_jobs(self) -> bool:

        return len(self.jobs) > 0

    # ------------------------------------------------------

    def top_match(self) -> JobData | None:

        if not self.jobs:

            return None

        return max(

            self.jobs,

            key=lambda job: job.match_score

        )

    # ------------------------------------------------------

    def average_match_score(self) -> float:

        if not self.jobs:

            return 0.0

        total = sum(

            job.match_score

            for job in self.jobs

        )

        return round(

            total / len(self.jobs),

            2

        )

    # ------------------------------------------------------

    def __len__(self):

        return len(self.jobs)

    # ------------------------------------------------------

    def __str__(self):

        return (

            f"SearchResult("

            f"jobs={len(self.jobs)}, "

            f"providers={len(self.providers_used)}, "

            f"time={self.search_time}s)"

        )