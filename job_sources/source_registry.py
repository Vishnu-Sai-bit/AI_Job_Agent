"""
==========================================================
Job Sources - Source Registry
==========================================================
"""

from typing import Dict, Type
from job_sources.base import BaseJobSource
from job_sources.remotive import RemotiveSource
from job_sources.arbeitnow import ArbeitnowSource
from job_sources.remoteok import RemoteOKSource
from job_sources.company_careers import CompanyCareersSource

class SourceRegistry:
    def __init__(self):
        self._sources: Dict[str, BaseJobSource] = {
            "remotive": RemotiveSource(),
            "arbeitnow": ArbeitnowSource(),
            "remoteok": RemoteOKSource(),
            "company": CompanyCareersSource()
        }

    def get_source(self, name: str) -> BaseJobSource:
        return self._sources.get(name.lower())

    def list_sources(self):
        return list(self._sources.keys())

source_registry = SourceRegistry()
