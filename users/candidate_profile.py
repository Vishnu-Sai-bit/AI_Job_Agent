"""
==========================================================
AI JobAgent - Candidate Profile Manager
Author : Beere Vishnu Sai
Description:
    User candidate profile model, preference manager,
    and profile serialization for multi-user support.
==========================================================
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json

@dataclass
class CandidateProfile:
    """
    Candidate user profile holding resume metrics and career targets.
    """
    user_id: str = "default_user"
    full_name: str = "BEERE VISHNU SAI"
    email: str = "beerevishnusai776600@gmail.com"
    phone: str = "+91 9182679641"
    linkedin: str = "https://www.linkedin.com/in/beerevishnusai/"
    github: str = "https://github.com/Vishnu-Sai-bit"
    portfolio: str = "https://beere-vishnu-sai-portfolio.netlify.app/"
    target_role: str = "Data Analyst"
    preferred_location: str = "Hyderabad"
    experience_years: float = 0.5
    expected_salary: Optional[int] = 1200000
    skills: List[str] = field(default_factory=list)
    education: List[Dict[str, Any]] = field(default_factory=list)
    projects: List[Dict[str, Any]] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    ats_score: float = 79.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CandidateProfile":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def save_to_file(self, file_path: Path):
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, file_path: Path) -> "CandidateProfile":
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return cls.from_dict(json.load(f))
        return cls()
