"""
==========================================================
AI Job Copilot - Application Custom Exceptions
==========================================================
"""

class JobCopilotError(Exception):
    """Base exception for AI Job Copilot."""
    pass

class ResumeParsingError(JobCopilotError):
    """Raised when parsing or extracting text from a resume fails."""
    pass

class JobMatchingError(JobCopilotError):
    """Raised when job matching score calculation fails."""
    pass

class IntegrationError(JobCopilotError):
    """Raised when external job portal API calls fail."""
    pass
