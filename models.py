"""
==========================================================
AI Job Agent - Database Models (models.py)
Stores real job listings, original source requisition IDs,
official URLs, application URLs, and verification metadata.
==========================================================
"""

from models.sql_models import db, Job, utc_now

__all__ = ["db", "Job", "utc_now"]
