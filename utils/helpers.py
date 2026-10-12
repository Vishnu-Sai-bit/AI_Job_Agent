"""
==========================================================
AI JobAgent - Helper Functions
Author : Beere Vishnu Sai

Description:
    Common utility/helper functions used across the project.
==========================================================
"""

from typing import List

from models import JobData


# ==========================================================
# Remove Duplicate Jobs
# ==========================================================

def remove_duplicates(
    jobs: List[JobData],
) -> List[JobData]:
    """
    Remove duplicate jobs using
    Company + Title + Location.

    Returns:
        List[JobData]
    """

    unique_jobs: List[JobData] = []

    seen = set()

    for job in jobs:

        key = (

            (job.company or "").strip().lower(),

            (job.title or "").strip().lower(),

            (job.location or "").strip().lower(),

        )

        if key not in seen:

            seen.add(key)

            unique_jobs.append(job)

    return unique_jobs