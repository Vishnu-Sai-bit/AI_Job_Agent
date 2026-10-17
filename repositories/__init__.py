"""
==========================================================
AI JobAgent - Repositories Package
==========================================================
"""

from repositories.job_repository import (
    initialize_jobs_table,
    save_job,
    get_discovered_jobs,
    get_discovered_job_by_id,
    mark_job_verified,
    mark_job_closed,
    get_default_db_path,
)

__all__ = [
    "initialize_jobs_table",
    "save_job",
    "get_discovered_jobs",
    "get_discovered_job_by_id",
    "mark_job_verified",
    "mark_job_closed",
    "get_default_db_path",
]
