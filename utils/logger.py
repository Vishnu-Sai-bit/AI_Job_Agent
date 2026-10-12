"""
==========================================================
AI JobAgent - Logger
Author : Beere Vishnu Sai

Description:
    Central logging utility for AI JobAgent.
==========================================================
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ==========================================================
# Log Directory
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "jobagent.log"

# ==========================================================
# Logger Configuration
# ==========================================================

logger = logging.getLogger("AIJobAgent")

if not logger.handlers:

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(filename)s | %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    # Console Output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # File Output
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,   # 5 MB
        backupCount=5,
        encoding="utf-8"
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.propagate = False


# ==========================================================
# Helper Functions
# ==========================================================

def debug(message: str):
    logger.debug(message)


def info(message: str):
    logger.info(message)


def warning(message: str):
    logger.warning(message)


def error(message: str):
    logger.error(message)


def exception(message: str):
    logger.exception(message)