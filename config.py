"""
==========================================================
AI JobAgent - Configuration
Author : Beere Vishnu Sai

Description:
    Central configuration for the entire AI JobAgent.
==========================================================
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


# ==========================================================
# Project Information
# ==========================================================

APP_NAME = "AI JobAgent"

AUTHOR = "Beere Vishnu Sai"

VERSION = "2.0.0"

DEBUG = True


# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

RESUME_FOLDER = BASE_DIR / "resumes"

REPORT_FOLDER = BASE_DIR / "reports"

LOG_FOLDER = BASE_DIR / "logs"

TEMP_FOLDER = BASE_DIR / "temp"

# Automatically create folders
for folder in (
    RESUME_FOLDER,
    REPORT_FOLDER,
    LOG_FOLDER,
    TEMP_FOLDER,
):
    folder.mkdir(parents=True, exist_ok=True)


# ==========================================================
# Resume Settings
# ==========================================================

SUPPORTED_RESUME_FORMATS = {
    ".pdf",
    ".docx",
    ".doc",
    ".txt",
    ".rtf",
    ".odt",
}

MAX_RESUME_SIZE_MB = 10

MAX_RESUME_TEXT_LENGTH = 12000


# ==========================================================
# Ollama Configuration
# ==========================================================

OLLAMA_URL = "http://localhost:11434/api/chat"

OLLAMA_MODEL = "llama3.2:latest"

OLLAMA_TIMEOUT = 180

# Number of retry attempts
OLLAMA_MAX_RETRIES = 3

# Compatibility alias
MAX_RETRIES = OLLAMA_MAX_RETRIES

OLLAMA_OPTIONS = {
    "temperature": 0,
    "num_predict": 4096,
}


# ==========================================================
# ATS Score Weights
# ==========================================================

ATS_WEIGHTS = {

    "contact": 10,

    "skills": 30,

    "education": 15,

    "experience": 20,

    "projects": 15,

    "certifications": 10,

}


# ==========================================================
# Job Match Weights
# ==========================================================

MATCH_WEIGHTS = {
    "role": 30,
    "skills": 30,
    "experience": 15,
    "location": 10,
    "salary": 5,
    "semantic": 10,
}

# ==========================================================
# Job Matching
# ==========================================================

MIN_MATCH_SCORE = 50


# ==========================================================
# Job Search Defaults
# ==========================================================

DEFAULT_POSTED_DAYS = 30

DEFAULT_LIMIT = 10

MAX_LIMIT = 100

# ==========================================================
# Preferred Roles
# ==========================================================

DEFAULT_ROLES = [

    "Data Analyst",

    "Business Analyst",

    "BI Analyst",

    "Reporting Analyst",

    "Data Engineer",

    "Data Scientist",

]


# ==========================================================
# Preferred Locations
# ==========================================================

DEFAULT_LOCATIONS = [

    "Bengaluru",

    "Hyderabad",

    "Chennai",

    "Pune",

    "Mumbai",

    "Noida",

    "Gurugram",

    "Delhi",

]


# ==========================================================
# Logging
# ==========================================================

LOG_LEVEL = "INFO"

LOG_FILE = LOG_FOLDER / "jobagent.log"


# ==========================================================
# API Configuration
# ==========================================================

API_TITLE = APP_NAME

API_VERSION = VERSION

API_DESCRIPTION = "AI Powered Resume Analyzer & Job Search System"


# ==========================================================
# CORS
# ==========================================================

ALLOWED_ORIGINS = [

    "http://localhost:8000",

    "http://127.0.0.1:8000",

    "http://localhost:8501",

    "http://127.0.0.1:8501",

]


# ==========================================================
# HTTP Requests
# ==========================================================

USER_AGENT = (
    "AIJobAgent/2.0 "
    "(Python Requests)"
)

# Maximum time (seconds) to wait for an API response
HTTP_TIMEOUT = 10

# Delay (seconds) between consecutive API requests
REQUEST_DELAY = 1


# ==========================================================
# Job Providers
# ==========================================================

ENABLE_REMOTIVE = True

ENABLE_REMOTEOK = True

ENABLE_ARBEITNOW = True

ENABLE_LINKEDIN = True

ENABLE_NAUKRI = True

ENABLE_FOUNDIT = True

ENABLE_INDEED = True

ENABLE_GLASSDOOR = True

ENABLE_WELLFOUND = True

ENABLE_GREENHOUSE = False

ENABLE_LEVER = False

ENABLE_JSEARCH = False

ENABLE_THEMUSE = True

ENABLE_ADZUNA = True
 
ENABLE_JOOBLE = True

ENABLE_SERPAPI = True
 
# API Keys and Hosts
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "jsearch.p.rapidapi.com")
 
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")
 
JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY", "")

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")


# ==========================================================
# Future Database
# ==========================================================

DATABASE_URL = ""

DATABASE_NAME = "jobagent"


# ==========================================================
# Future Cache
# ==========================================================

CACHE_ENABLED = False

CACHE_TIMEOUT = 3600