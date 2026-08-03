"""
==========================================================
AI JobAgent - Application CRM Service
Author : Antigravity
==========================================================
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from utils import info, exception

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
CRM_FILE = os.path.join(DATA_DIR, "applications.json")

# In-memory storage with file backing
_applications_cache: Dict[str, Dict[str, Any]] = {}

from services.db.mongo_manager import db_manager

def _init_crm():
    global _applications_cache
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    
    # Try reading from db_manager (MongoDB or local JSON)
    try:
        apps = db_manager.get_applications()
        _applications_cache = {a["id"]: a for a in apps if "id" in a}
    except Exception as e:
        exception(f"Failed to load applications from db_manager: {e}")
        _applications_cache = {}

_init_crm()

def _save_crm(app_record: Optional[Dict[str, Any]] = None, deleted_id: Optional[str] = None):
    try:
        if app_record:
            db_manager.save_application(app_record)
        if deleted_id:
            db_manager.delete_application(deleted_id)
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR, exist_ok=True)
        with open(CRM_FILE, "w", encoding="utf-8") as f:
            json.dump(_applications_cache, f, indent=2)
    except Exception as e:
        exception(f"Failed to save applications: {e}")

def get_all_applications() -> List[Dict[str, Any]]:
    """
    Retrieve all tracked applications ordered by date updated.
    """
    apps = list(_applications_cache.values())
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Calculate follow-up due flags
    for app in apps:
        if app.get("status") == "applied" and app.get("followup_date"):
            app["is_followup_due"] = app["followup_date"] <= today
        else:
            app["is_followup_due"] = False

    apps.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return apps

def add_or_update_application(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add a new job application or update an existing one.
    """
    app_id = data.get("id") or f"app_{uuid.uuid4().hex[:8]}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today_str = datetime.now().strftime("%Y-%m-%d")

    status = data.get("status", "saved").lower()
    date_applied = data.get("date_applied")
    
    # If transitioning to applied, set default follow-up in 4 days
    if status == "applied" and not date_applied:
        date_applied = today_str
    
    followup_date = data.get("followup_date")
    if date_applied and not followup_date:
        try:
            d_obj = datetime.strptime(date_applied, "%Y-%m-%d")
            followup_date = (d_obj + timedelta(days=4)).strftime("%Y-%m-%d")
        except Exception:
            followup_date = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")

    app_record = {
        "id": app_id,
        "company": data.get("company", "Company"),
        "role": data.get("role", "Role"),
        "location": data.get("location", "N/A"),
        "salary": data.get("salary", "Not Mentioned"),
        "apply_url": data.get("apply_url", "#"),
        "status": status,
        "date_applied": date_applied or "",
        "followup_date": followup_date or "",
        "notes": data.get("notes", ""),
        "interview_date": data.get("interview_date", ""),
        "created_at": _applications_cache.get(app_id, {}).get("created_at", now_str),
        "updated_at": now_str
    }

    _applications_cache[app_id] = app_record
    _save_crm(app_record=app_record)
    info(f"CRM Application updated: {app_record['role']} at {app_record['company']} ({status})")
    return app_record

def delete_application(app_id: str) -> bool:
    """
    Remove an application from tracking.
    """
    if app_id in _applications_cache:
        del _applications_cache[app_id]
        _save_crm(deleted_id=app_id)
        info(f"CRM Application deleted: {app_id}")
        return True
    return False

def generate_followup_message(app_id: str, candidate_name: str = "Candidate") -> Dict[str, Any]:
    """
    Generate a tailored follow-up message for an application.
    """
    app = _applications_cache.get(app_id)
    if not app:
        raise ValueError(f"Application {app_id} not found in CRM.")

    company = app.get("company", "Hiring Team")
    role = app.get("role", "the role")
    applied_date = app.get("date_applied", "recently")

    subject = f"Following up on {role} application – {candidate_name}"
    body = (
        f"Hi {company} Hiring Team,\n\n"
        f"I hope you are having a great week!\n\n"
        f"I am writing to briefly follow up on my application for the {role} position submitted on {applied_date}. "
        f"I remain extremely enthusiastic about the opportunity to contribute to {company}'s team.\n\n"
        f"Given my hands-on background building end-to-end data pipelines and KPI dashboards, I am confident I can hit the ground running. "
        f"Please let me know if you need any further information, sample projects, or references.\n\n"
        f"Thank you for your time and consideration.\n\n"
        f"Best regards,\n"
        f"{candidate_name}"
    )

    return {
        "subject": subject,
        "body": body,
        "app_id": app_id,
        "company": company,
        "role": role
    }
