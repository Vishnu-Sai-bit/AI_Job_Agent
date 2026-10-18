"""
==========================================================
AI JobAgent - Canonical Database Models
Defines Job model with the 11 required fields:
job_id, company_name, job_title, description, location,
posted_at, source_platform, original_url, apply_url,
last_verified_at, status.
STRICT REQUIREMENT: Zero salary attributes stored or exposed.
==========================================================
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any


@dataclass
class Job:
    """Canonical 11-field Job data model."""
    job_id: str
    company_name: str
    job_title: str
    description: str
    location: str
    posted_at: str
    source_platform: str
    original_url: str
    apply_url: str
    last_verified_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "active"

    # Optional metadata
    skills: List[str] = field(default_factory=list)
    match_score: float = 0.0
    matching_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    experience_alignment: str = ""
    url_verified: bool = True

    # Backwards compatibility properties for legacy code
    @property
    def title(self) -> str:
        return self.job_title

    @title.setter
    def title(self, value: str):
        self.job_title = value

    @property
    def company(self) -> str:
        return self.company_name

    @company.setter
    def company(self, value: str):
        self.company_name = value

    @property
    def source(self) -> str:
        return self.source_platform

    @source.setter
    def source(self, value: str):
        self.source_platform = value

    @property
    def url(self) -> str:
        return self.apply_url

    @url.setter
    def url(self, value: str):
        self.apply_url = value

    @property
    def posted_date(self) -> str:
        return self.posted_at

    @posted_date.setter
    def posted_date(self, value: str):
        self.posted_at = value

    @property
    def salary(self) -> str:
        return ""

    @salary.setter
    def salary(self, value: str):
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert Job object to dictionary with exact 11 fields."""
        return {
            "job_id": self.job_id,
            "company_name": self.company_name,
            "job_title": self.job_title,
            "description": self.description,
            "location": self.location,
            "posted_at": self.posted_at,
            "source_platform": self.source_platform,
            "original_url": self.original_url,
            "apply_url": self.apply_url,
            "last_verified_at": self.last_verified_at,
            "status": self.status,
            "skills": self.skills,
            "match_score": self.match_score,
            "matching_skills": self.matching_skills,
            "missing_skills": self.missing_skills,
            "experience_alignment": self.experience_alignment,
            "url_verified": self.url_verified,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Job":
        """Instantiate Job model from a dictionary."""
        return cls(
            job_id=str(data.get("job_id") or data.get("external_job_id") or data.get("id") or ""),
            company_name=str(data.get("company_name") or data.get("company") or ""),
            job_title=str(data.get("job_title") or data.get("title") or ""),
            description=str(data.get("description") or ""),
            location=str(data.get("location") or "Remote / Office"),
            posted_at=str(data.get("posted_at") or data.get("posted_date") or ""),
            source_platform=str(data.get("source_platform") or data.get("provider") or data.get("source") or "Company Careers"),
            original_url=str(data.get("original_url") or data.get("url") or ""),
            apply_url=str(data.get("apply_url") or data.get("url") or ""),
            last_verified_at=str(data.get("last_verified_at") or datetime.now(timezone.utc).isoformat()),
            status=str(data.get("status") or "active"),
            skills=data.get("skills") if isinstance(data.get("skills"), list) else [],
            match_score=float(data.get("match_score") or 0.0),
            matching_skills=data.get("matching_skills") if isinstance(data.get("matching_skills"), list) else [],
            missing_skills=data.get("missing_skills") if isinstance(data.get("missing_skills"), list) else [],
            experience_alignment=str(data.get("experience_alignment") or ""),
            url_verified=bool(data.get("url_verified", True)),
        )