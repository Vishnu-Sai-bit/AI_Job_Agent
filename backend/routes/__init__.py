"""
==========================================================
AI JobAgent - Backend Routes Package
Author: Beere Vishnu Sai
==========================================================
"""

from backend.routes.admin_routes import router as admin_router
from backend.routes.user_routes import router as user_router

__all__ = [
    "admin_router",
    "user_router",
]
