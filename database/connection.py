"""
==========================================================
AI JobAgent - Unified Database Gateway
Author : Beere Vishnu Sai
Description:
    Unified connection gateway orchestrating PostgreSQL
    and MongoDB Atlas connections with automated health checks.
==========================================================
"""

from typing import Dict, Any, Optional
from services.db.postgres_manager import postgres_manager
from services.db.mongo_manager import db_manager

class DatabaseGateway:
    """
    Central database gateway unifying relational and document stores.
    """
    def __init__(self):
        self.pg = postgres_manager
        self.mongo = db_manager

    def get_status(self) -> Dict[str, Any]:
        """
        Return the live health status of all database engines.
        """
        pg_conn_val = getattr(self.pg, "is_connected", False)
        pg_connected = pg_conn_val() if callable(pg_conn_val) else bool(pg_conn_val)

        mongo_conn_val = getattr(self.mongo, "is_connected", False)
        mongo_connected = mongo_conn_val() if callable(mongo_conn_val) else bool(mongo_conn_val)

        active_engine = "PostgreSQL" if pg_connected else ("MongoDB Atlas" if mongo_connected else "Local SQLite")

        return {
            "active_engine": active_engine,
            "postgresql": {
                "connected": pg_connected,
                "engine": getattr(self.pg, "db_engine", "sqlite") if self.pg else "none"
            },
            "mongodb": {
                "connected": mongo_connected,
                "database": getattr(self.mongo, "db_name", "ai_job_agent") if self.mongo else "none"
            }
        }

    def is_healthy(self) -> bool:
        """
        Check if at least one database engine is healthy.
        """
        status = self.get_status()
        return status["postgresql"]["connected"] or status["mongodb"]["connected"]

db_gateway = DatabaseGateway()
