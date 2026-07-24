"""
==========================================================
AI JobAgent - Custom Exceptions
Author : Beere Vishnu Sai

Description:
    Custom exception classes used throughout the project.
==========================================================
"""


# ==========================================================
# Base Exception
# ==========================================================

class JobAgentError(Exception):
    """
    Base exception for all AI JobAgent errors.
    """

    def __init__(self, message: str = "AI JobAgent Error"):
        self.message = message
        super().__init__(self.message)


# ==========================================================
# Resume Exceptions
# ==========================================================

class ResumeParserError(JobAgentError):
    """Raised when resume parsing fails."""
    pass


class ResumeAnalyzerError(JobAgentError):
    """Raised when AI resume analysis fails."""
    pass


# ==========================================================
# Skill Exceptions
# ==========================================================

class SkillExtractionError(JobAgentError):
    """Raised when skill extraction fails."""
    pass


# ==========================================================
# Experience Exceptions
# ==========================================================

class ExperienceParserError(JobAgentError):
    """Raised when experience parsing fails."""
    pass


# ==========================================================
# Salary Exceptions
# ==========================================================

class SalaryParserError(JobAgentError):
    """Raised when salary parsing fails."""
    pass


# ==========================================================
# Location Exceptions
# ==========================================================

class LocationParserError(JobAgentError):
    """Raised when location parsing fails."""
    pass


# ==========================================================
# ATS Exceptions
# ==========================================================

class ATSCalculationError(JobAgentError):
    """Raised when ATS calculation fails."""
    pass


# ==========================================================
# Job Matching
# ==========================================================

class JobMatcherError(JobAgentError):
    """Raised when job matching fails."""
    pass


# ==========================================================
# Job Search
# ==========================================================

class JobSearchError(JobAgentError):
    """Raised when job search fails."""
    pass


# ==========================================================
# Provider Exceptions
# ==========================================================

class ProviderError(JobAgentError):
    """Raised when a job provider fails."""
    pass


# ==========================================================
# Ollama Exceptions
# ==========================================================

class OllamaConnectionError(JobAgentError):
    """Raised when Ollama cannot be reached."""
    pass


class InvalidAIResponseError(JobAgentError):
    """Raised when AI returns invalid JSON."""
    pass