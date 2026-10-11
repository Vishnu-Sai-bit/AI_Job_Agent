"""
==========================================================
AI JobAgent - Admin API Routes
Author : Beere Vishnu Sai
Description:
    FastAPI router for Silkverse admin telemetry, RBAC,
    and reverse requisition candidate matching.
==========================================================
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional, List
from pydantic import BaseModel
from admin.admin_service import admin_service
from services.auth.auth_service import auth_service

router = APIRouter(prefix="/admin", tags=["Admin"])

class RequisitionMatchRequest(BaseModel):
    role: str = "Data Analyst"
    required_skills: List[str] = ["Python", "SQL"]
    location: Optional[str] = ""

@router.get("/telemetry")
def get_admin_telemetry(authorization: Optional[str] = Header(None)):
    return admin_service.get_system_telemetry()

@router.get("/users")
def get_admin_users(authorization: Optional[str] = Header(None)):
    return {"users": admin_service.list_all_users()}

@router.post("/users/{user_id}/toggle-role")
def toggle_user_role(user_id: str, authorization: Optional[str] = Header(None)):
    res = admin_service.toggle_user_role(user_id)
    if not res:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"status": "success", "user": res}

@router.post("/match-talent")
def match_talent(req: RequisitionMatchRequest, authorization: Optional[str] = Header(None)):
    matches = admin_service.search_talent_pool(
        role=req.role,
        required_skills=req.required_skills,
        location=req.location or ""
    )
    return {"status": "success", "candidates": matches}
