"""
==========================================================
AI JobAgent - Frontend Views Package
Author: Beere Vishnu Sai
Description:
    Pure Python Streamlit UI component views.
==========================================================
"""

from frontend.views.ats_view import render_ats_view
from admin.admin_view import render_admin_dashboard
from users.user_view import render_user_auth_modal

__all__ = [
    "render_ats_view",
    "render_admin_dashboard",
    "render_user_auth_modal",
]
