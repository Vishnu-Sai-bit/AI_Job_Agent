"""
==========================================================
AI JobAgent - Admin Package
Author: Beere Vishnu Sai
Description:
    Exports AdminService and Admin Dashboard views.
==========================================================
"""

from admin.admin_service import admin_service
from admin.admin_view import render_admin_dashboard

__all__ = [
    "admin_service",
    "render_admin_dashboard",
]
