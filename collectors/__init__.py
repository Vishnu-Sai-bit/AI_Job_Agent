"""
==========================================================
AI JobAgent - Multi-Source Job Collectors
Exports connectors for Workday, Greenhouse, Lever,
direct Company Careers, Remotive, RemoteOK, and ArbeitNow.
==========================================================
"""

from collectors.workday import WorkdayCollector, fetch_workday_jobs
from collectors.greenhouse import GreenhouseCollector, fetch_greenhouse_jobs
from collectors.lever import LeverCollector, fetch_lever_jobs
from collectors.company_careers import CompanyCareersCollector, fetch_company_careers_jobs
from collectors.remotive import RemotiveCollector, fetch_remotive_jobs
from collectors.remoteok import RemoteOKCollector, fetch_remoteok_jobs
from collectors.arbeitnow import ArbeitNowCollector, fetch_arbeitnow_jobs

ALL_COLLECTORS = [
    WorkdayCollector,
    GreenhouseCollector,
    LeverCollector,
    CompanyCareersCollector,
    RemotiveCollector,
    RemoteOKCollector,
    ArbeitNowCollector,
]

__all__ = [
    "WorkdayCollector",
    "fetch_workday_jobs",
    "GreenhouseCollector",
    "fetch_greenhouse_jobs",
    "LeverCollector",
    "fetch_lever_jobs",
    "CompanyCareersCollector",
    "fetch_company_careers_jobs",
    "RemotiveCollector",
    "fetch_remotive_jobs",
    "RemoteOKCollector",
    "fetch_remoteok_jobs",
    "ArbeitNowCollector",
    "fetch_arbeitnow_jobs",
    "ALL_COLLECTORS",
]
