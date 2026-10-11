"""
==========================================================
Job Sources - Base Class
==========================================================
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseJobSource(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str:
        pass

    @abstractmethod
    def fetch_jobs(self, role: str, location: str) -> List[Dict[str, Any]]:
        pass
