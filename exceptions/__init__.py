"""
AI JobAgent Exception Package
"""

from .custom_exceptions import *

__all__ = [

    "JobAgentError",

    "ResumeParserError",
    "ResumeAnalyzerError",

    "SkillExtractionError",

    "ExperienceParserError",

    "SalaryParserError",

    "LocationParserError",

    "ATSCalculationError",

    "JobMatcherError",

    "JobSearchError",

    "ProviderError",

    "OllamaConnectionError",

    "InvalidAIResponseError"

]