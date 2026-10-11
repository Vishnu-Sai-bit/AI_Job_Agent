"""
==========================================================
AI JobAgent - Database Package
Author: Beere Vishnu Sai
Description:
    Exports relational (PostgreSQL/SQLite) and document (MongoDB)
    managers and unified connection gateway.
==========================================================
"""

from database.postgres_manager import postgres_manager
from database.mongo_manager import db_manager
from database.connection import db_gateway

__all__ = [
    "postgres_manager",
    "db_manager",
    "db_gateway",
]
