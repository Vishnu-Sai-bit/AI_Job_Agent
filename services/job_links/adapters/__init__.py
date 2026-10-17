"""
==========================================================
ATS Provider Adapters package
Tier 1: Workday, Greenhouse, Lever, Ashby, SmartRecruiters, Workable, Teamtailor, Recruitee, Personio
Tier 2: Oracle Taleo, SAP SuccessFactors, iCIMS
==========================================================
"""

from .greenhouse import GreenhouseAdapter
from .lever import LeverAdapter
from .ashby import AshbyAdapter
from .workday import WorkdayAdapter
from .smartrecruiters import SmartRecruitersAdapter
from .workable import WorkableAdapter
from .teamtailor import TeamtailorAdapter
from .recruitee import RecruiteeAdapter
from .personio import PersonioAdapter
from .taleo import TaleoAdapter
from .successfactors import SuccessFactorsAdapter
from .icims import ICIMSAdapter

__all__ = [
    "GreenhouseAdapter",
    "LeverAdapter",
    "AshbyAdapter",
    "WorkdayAdapter",
    "SmartRecruitersAdapter",
    "WorkableAdapter",
    "TeamtailorAdapter",
    "RecruiteeAdapter",
    "PersonioAdapter",
    "TaleoAdapter",
    "SuccessFactorsAdapter",
    "ICIMSAdapter"
]
