"""
==========================================================
AI JobAgent - Base Provider Interface
==========================================================
"""

from abc import ABC, abstractmethod
from typing import List
import requests

from config import (
    USER_AGENT,
    HTTP_TIMEOUT,
)

from models import JobData

from utils import (
    info,
    warning,
    exception,
)

from exceptions import (
    ProviderError,
)

class BaseProvider(ABC):
    def __init__(self, name: str, api_url: str):
        self.name = name
        self.api_url = api_url

    def get_headers(self) -> dict:
        return {
            "User-Agent": USER_AGENT,
        }

    def fetch_raw_data(self, params: dict = None, headers: dict = None) -> list | dict:
        """
        Perform the HTTP GET request to retrieve raw jobs.
        """
        info(f"Fetching data from {self.name} API...")
        req_headers = self.get_headers()
        if headers:
            req_headers.update(headers)
        try:
            response = requests.get(
                self.api_url,
                headers=req_headers,
                params=params,
                timeout=HTTP_TIMEOUT,
            )
            if response.status_code != 200:
                warning(f"{self.name} API returned status {response.status_code}. Response: {response.text}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            exception(f"HTTP request failed for {self.name} API: {e}")
            raise ProviderError(f"{self.name} provider failed: {e}")

    @abstractmethod
    def search_jobs(self, role: str = "") -> List[JobData]:
        pass

    @abstractmethod
    def build_job(self, item: dict, keywords: List[str]) -> JobData | None:
        pass
