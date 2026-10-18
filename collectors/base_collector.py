"""
==========================================================
AI JobAgent - Base Collector Interface
Author : Antigravity / Beere Vishnu Sai
Defines the common collector interface for all hiring platforms.
==========================================================
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseCollector(ABC):
    """Abstract base class for all job source connectors."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def fetch_jobs(
        self,
        query: str = "",
        location: str = "",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Fetch vacancies from the underlying hiring platform or ATS API.
        Must return standardized job dictionaries preserving exact requisition IDs and URLs.
        """
        pass
