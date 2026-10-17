"""
==========================================================
AI JobAgent - Multi-Source ATS Job Connector Engine
Modular framework for querying public/guest ATS endpoints
(Greenhouse, Lever, Ashby, SmartRecruiters, Workable, etc.)
==========================================================
"""

from services.job_sources.connectors import (
    CONNECTORS,
    normalize_job,
    fetch_greenhouse,
    fetch_lever,
    fetch_ashby,
    fetch_smartrecruiters,
    fetch_workable,
)
from services.job_sources.sync_jobs import sync_all_companies
from services.job_sources.url_verifier import (
    verify_destination_url,
    verify_job_destination,
)

__all__ = [
    "CONNECTORS",
    "normalize_job",
    "fetch_greenhouse",
    "fetch_lever",
    "fetch_ashby",
    "fetch_smartrecruiters",
    "fetch_workable",
    "sync_all_companies",
    "verify_destination_url",
    "verify_job_destination",
]
