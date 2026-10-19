from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field
import requests
from utils.logging_config import logger

class RawJobRecord(BaseModel):
    source_platform: str
    source_company_key: str
    source_job_id: str
    title: str
    company: str
    department: str = ""
    location: str = ""
    country: str = ""
    city: str = ""
    work_mode: str = "on-site"  # remote, hybrid, on-site
    employment_type: str = "full-time"  # full-time, part-time, contract, internship
    experience_level: str = "any"  # entry, mid, senior, lead
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: str = "USD"
    description: str = ""
    raw_description: str = ""
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    original_url: str
    apply_url: str
    canonical_url: Optional[str] = None
    published_at: Optional[datetime] = None
    source_metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseCollector(ABC):
    """
    Abstract Base Class for recruitment platform connectors.
    Ensures provider-specific logic, respectful rate-limits, and error isolation.
    """
    platform_name: str = "unknown"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "AIJobAgent/1.0 (+https://github.com/ai-job-agent; legitimate job matching and verified application links)"
        })

    @abstractmethod
    def fetch_jobs(self, company_key: str, **kwargs) -> List[RawJobRecord]:
        """Fetch raw job records from the specific provider."""
        pass

    def verify_job_live(self, original_url: str, apply_url: str) -> Tuple[bool, int, str]:
        """
        Default HTTP verification for job availability.
        Returns (is_active, http_status, details).
        """
        target = apply_url or original_url
        try:
            resp = self.session.head(target, timeout=self.timeout, allow_redirects=True)
            if resp.status_code == 405:  # HEAD not allowed
                resp = self.session.get(target, timeout=self.timeout, allow_redirects=True, stream=True)
            
            # Check for not found or explicit redirect away
            if resp.status_code == 200:
                return True, resp.status_code, "Verified accessible"
            elif resp.status_code in (404, 410):
                return False, resp.status_code, f"Posting returned {resp.status_code} (Gone/Not Found)"
            else:
                return True, resp.status_code, f"Returned status {resp.status_code}"
        except Exception as e:
            return False, 0, f"Connection error: {str(e)}"
