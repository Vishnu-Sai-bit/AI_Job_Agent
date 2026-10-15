"""
====================================================================
AI Job Agent - User-Friendly Career Intelligence Platform
Author: Beere Vishnu Sai
100% Pure Python Implementation (Streamlit UI)

Sequential 7-Step Career Lifecycle Workflow:
1. Upload
2. Resume
3. Show Job Searches
4. Prepare for Interview
5. Cover Letter Preparation
6. Mail Preparation
7. Application CRM
====================================================================
"""

import os
import sys
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

import streamlit as st

# Ensure repository root is on sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Core Models
from models import ResumeData, JobData, ATSReport

# Core Services
from services.resume.resume_parser import extract_resume_text
from services.resume.resume_analyzer import analyze_resume
from services.ats.ats_calculator import calculate_ats
from services.matcher.job_matcher import match_jobs
from services.resume.resume_tailorer import tailor_resume_for_job
from services.cover_letter.cover_letter_generator import generate_cover_letter
from services.email.email_generator import generate_job_emails
from services.interview.interview_generator import generate_interview_questions
from services.crm.application_crm import (
    get_all_applications,
    add_or_update_application,
    delete_application
)
from services.jobs.live_job_aggregator import (
    fetch_arbeitnow_live,
    fetch_remoteok_live,
    fetch_remotive_live
)

# ------------------------------------------------------------------
# Page Setup & Modern Dark Theme Styling
# ------------------------------------------------------------------
st.set_page_config(
    page_title="AI Job Agent",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .stApp {
        background-color: #0b0f17;
        color: #f1f5f9;
    }
    .hero-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #ffffff;
        margin-bottom: 6px;
    }
    .step-banner {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.12));
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 1rem 1.3rem;
        margin-bottom: 1.25rem;
    }
    .job-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 14px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .job-card:hover {
        border-color: #6366f1;
        transform: translateY(-2px);
    }
    .score-pill-high {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.2));
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 20px;
        padding: 4px 14px;
        font-weight: 700;
        font-size: 0.88rem;
    }
    .score-pill-med {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2));
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.4);
        border-radius: 20px;
        padding: 4px 14px;
        font-weight: 700;
        font-size: 0.88rem;
    }
    .skill-tag {
        display: inline-block;
        background: #1e293b;
        color: #cbd5e1;
        border: 1px solid #334155;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.82rem;
        font-weight: 500;
        margin: 3px 4px 3px 0;
    }
    .skill-match {
        display: inline-block;
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 6px;
        padding: 3px 10px;
        font-size: 0.8rem;
        margin: 2px 4px 2px 0;
    }
    .skill-gap {
        display: inline-block;
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 6px;
        padding: 3px 10px;
        font-size: 0.8rem;
        margin: 2px 4px 2px 0;
    }
    .stat-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 14px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    }
    .letter-paper {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.75rem;
        font-family: 'Inter', sans-serif;
        line-height: 1.8;
    }
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        border: none;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
    }
    .stButton>button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
        box-shadow: 0 6px 18px rgba(99, 102, 241, 0.45);
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# Data Normalization & Helper Functions (Required by Unit Tests)
# ------------------------------------------------------------------
def convert_to_jobdata(item: Dict[str, Any]) -> JobData:
    provider = item.get("source") or item.get("provider") or "Direct"
    return JobData(
        provider=provider,
        provider_id=str(item.get("id") or ""),
        company=item.get("company") or "Tech Enterprise",
        title=item.get("title") or "Data Analyst",
        description=item.get("description") or "",
        location=item.get("location") or "Remote",
        salary=item.get("salary") or "₹6 - ₹12 LPA",
        experience=item.get("experience") or "0-2 yrs",
        skills=item.get("skills") or ["Python", "SQL", "Data Analysis"],
        apply_url=item.get("url") or item.get("apply_url") or "#",
        remote=True if "remote" in (item.get("location") or "").lower() else False
    )

convert_dict_to_jobdata = convert_to_jobdata

def execute_job_collection(role: str = "Data Analyst", location: str = "India", providers: Optional[List[str]] = None) -> List[JobData]:
    """Helper for collecting jobs across verified repository and live multi-portal APIs."""
    collected: List[JobData] = []
    
    # 1. Load from verified jobs catalog
    initial = load_initial_jobs()
    role_lower = (role or "").lower().strip()
    for ij in initial:
        if not role_lower or role_lower in ij.title.lower() or any(w in ij.title.lower() for w in role_lower.split()):
            collected.append(ij)
            
    # 2. Concurrently fetch live opportunities across connected APIs
    try:
        from services.jobs.live_job_aggregator import aggregate_live_jobs
        live_res = aggregate_live_jobs(role=role or "Data Analyst", location=location or "India", max_total=35)
        for lj in live_res.get("jobs", []):
            collected.append(convert_to_jobdata(lj))
    except Exception:
        pass
        
    # Deduplicate by normalized title & company
    seen = set()
    deduped = []
    for j in collected:
        key = f"{j.title.strip().lower()}::{(j.company or '').strip().lower()}"
        if key not in seen:
            seen.add(key)
            deduped.append(j)
            
    return deduped if deduped else initial

def load_initial_jobs() -> List[JobData]:
    """Load default verified jobs pool."""
    verified_file = BASE_DIR / "data" / "verified_jobs.json"
    if not verified_file.exists():
        verified_file = BASE_DIR / "data" / "jobs_export.json"
    jobs = []
    if verified_file.exists():
        try:
            with open(verified_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
                for item in raw:
                    jobs.append(convert_to_jobdata(item))
        except Exception:
            pass
    return jobs

def load_initial_profile() -> ResumeData:
    """Load candidate profile if uploaded, otherwise return clean empty profile."""
    default_file = BASE_DIR / "data" / "default_parsed_resume.json"
    if default_file.exists():
        try:
            with open(default_file, "r", encoding="utf-8") as f:
                d = json.load(f)
                if d and d.get("has_resume"):
                    return ResumeData(
                        name=d.get("candidate_name", "Candidate"),
                        email=d.get("email", ""),
                        phone=d.get("phone", ""),
                        location=d.get("location", ""),
                        preferred_location=d.get("preferred_location", ""),
                        preferred_role=d.get("preferred_role", "Data Analyst"),
                        skills=d.get("skills", []),
                        experience_years=float(d.get("experience_years", 0)),
                        education=d.get("education", []),
                        projects=d.get("projects", []),
                        certifications=d.get("certifications", []),
                        career_summary=d.get("career_summary", ""),
                    )
        except Exception:
            pass
    return ResumeData(
        name="Candidate",
        email="",
        phone="",
        location="",
        preferred_location="",
        preferred_role="Data Analyst",
        skills=[],
        experience_years=0.0,
        career_summary=""
    )


# ------------------------------------------------------------------
# Session State Initialization
# ------------------------------------------------------------------
if "resume_data" not in st.session_state or st.session_state.resume_data is None:
    st.session_state.resume_data = load_initial_profile()

if "ats_report" not in st.session_state or st.session_state.ats_report is None:
    st.session_state.ats_report = calculate_ats(st.session_state.resume_data) if st.session_state.resume_data.skills else None

if "collected_jobs" not in st.session_state or not st.session_state.collected_jobs:
    st.session_state.collected_jobs = load_initial_jobs()

if "matched_jobs" not in st.session_state or not st.session_state.matched_jobs:
    st.session_state.matched_jobs = match_jobs(st.session_state.resume_data, st.session_state.collected_jobs)

if "target_role" not in st.session_state:
    st.session_state.target_role = "Data Analyst"

if "preferred_location" not in st.session_state:
    st.session_state.preferred_location = "Hyderabad"

if "raw_resume_text" not in st.session_state:
    st.session_state.raw_resume_text = ""

# ------------------------------------------------------------------
# Define the Exact 7-Step Workflow Requested by User:
# upload, resume, show job searches, prepare for interview,
# cover letter preparation, mail preparation, application crm
# ------------------------------------------------------------------
WORKFLOW_STEPS = [
    "Upload",
    "Resume",
    "Show Job Searches",
    "Prepare for Interview",
    "Cover Letter Preparation",
    "Mail Preparation",
    "Application CRM"
]

if "current_step_idx" not in st.session_state:
    st.session_state.current_step_idx = 0


# ------------------------------------------------------------------
# Sidebar: Exact 7-Step Flow Navigation & Candidate Status
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 💼 AI JobAgent")
    st.caption("Your AI-Powered Career Assistant")
    st.markdown("---")

    # Candidate Quick Status
    res = st.session_state.resume_data
    ats = st.session_state.ats_report
    has_res = bool(st.session_state.raw_resume_text or res.skills)
    st.markdown(f"**👤 {res.name if has_res else 'Candidate'}**")
    if has_res and res.location:
        st.caption(f"📍 Location: {res.location}")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("ATS Fit", f"{ats.score:.0f}%" if (ats and has_res) else "--")
    with col_s2:
        st.metric("Skills", len(res.skills) if has_res else 0)

    st.markdown("---")
    st.markdown("##### 🧭 Career Workflow Pipeline")

    # Radio selection driven by current step index
    selected_step_str = st.radio(
        "Workflow:",
        WORKFLOW_STEPS,
        index=st.session_state.current_step_idx,
        label_visibility="collapsed"
    )
    
    # Sync if user clicked a radio item
    new_step_idx = WORKFLOW_STEPS.index(selected_step_str)
    if new_step_idx != st.session_state.current_step_idx:
        st.session_state.current_step_idx = new_step_idx
        st.rerun()

    st.markdown("---")
    if st.button("🔄 Reset Workspace", use_container_width=True):
        st.session_state.resume_data = load_initial_profile()
        st.session_state.raw_resume_text = ""
        st.session_state.ats_report = None
        st.session_state.current_step_idx = 0
        st.success("Session reset!")
        st.rerun()

    st.caption("Pure Python Architecture • 7 Core Modules")


# ------------------------------------------------------------------
# Main Workspace: Dedicated Render per Selected Workflow Step
# ------------------------------------------------------------------
cur_idx = st.session_state.current_step_idx
step_name = WORKFLOW_STEPS[cur_idx]

# Top Step Title
st.markdown(f'<div class="hero-title">{step_name}</div>', unsafe_allow_html=True)

# Navigation Helper Function
def render_step_footer(prev_idx: Optional[int], next_idx: Optional[int], next_label: str = "Proceed to Next Step"):
    st.markdown("<hr style='border-color: #1f2937; margin-top: 2rem; margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if prev_idx is not None:
            if st.button(f"⬅ Back: {WORKFLOW_STEPS[prev_idx]}", use_container_width=True):
                st.session_state.current_step_idx = prev_idx
                st.rerun()
    with c3:
        if next_idx is not None:
            if st.button(f"{next_label} ➔", type="primary", use_container_width=True):
                st.session_state.current_step_idx = next_idx
                st.rerun()


# ==================================================================
# STEP 1: UPLOAD
# ==================================================================
if cur_idx == 0:
    st.markdown("""
    <div class="step-banner">
        <strong>Step 1 of 7 — Resume Upload</strong><br>
        Upload your latest resume (.pdf, .docx, or .txt). The AI will ingest and extract text and structural sections.
    </div>
    """, unsafe_allow_html=True)

    col_u1, col_u2 = st.columns([1, 1])
    with col_u1:
        st.subheader("📄 Upload Resume Document")
        uploaded = st.file_uploader("Select Resume File:", type=["pdf", "docx", "txt"])
        
        if uploaded is not None:
            save_path = BASE_DIR / "resumes" / uploaded.name
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(uploaded.getbuffer())
            
            with st.spinner("Extracting text and building candidate profile..."):
                raw_text = extract_resume_text(save_path)
                st.session_state.raw_resume_text = raw_text
                st.session_state.resume_data = analyze_resume(raw_text)
                st.session_state.ats_report = calculate_ats(st.session_state.resume_data)
                st.session_state.matched_jobs = match_jobs(st.session_state.resume_data, st.session_state.collected_jobs)
            st.success(f"'{uploaded.name}' ingested and processed successfully!")

    with col_u2:
        st.subheader("📋 Ingestion Summary & Preview")
        if st.session_state.raw_resume_text:
            res = st.session_state.resume_data
            st.write(f"- **Candidate Name:** {res.name}")
            st.write(f"- **Target Job Title:** {res.preferred_role}")
            st.write(f"- **Extracted Length:** {len(st.session_state.raw_resume_text)} characters")
            st.write(f"- **Identified Skills:** {len(res.skills)} verified skills")

            with st.expander("View Extracted Raw Resume Text", expanded=False):
                st.text_area("Extracted Text", st.session_state.raw_resume_text, height=220, disabled=True)
        else:
            st.info("No resume uploaded yet. Select a PDF or DOCX file on the left to extract your skills and calculate your ATS fit score.")

    render_step_footer(None, 1, "Proceed to 2. Resume")


# ==================================================================
# STEP 2: RESUME
# ==================================================================
elif cur_idx == 1:
    st.markdown("""
    <div class="step-banner">
        <strong>Step 2 of 7 — Resume Analysis & ATS Diagnostic</strong><br>
        View candidate details, verified skills, credentials, and 6-dimension ATS audit score.
    </div>
    """, unsafe_allow_html=True)

    res = st.session_state.resume_data
    ats = st.session_state.ats_report
    has_res = bool(st.session_state.raw_resume_text or (res and res.skills))

    if not has_res:
        st.info("No resume uploaded yet. Please upload your resume in Step 1 to generate your ATS audit and profile analysis.")
        if st.button("⬅ Go to Step 1: Upload", type="primary"):
            st.session_state.current_step_idx = 0
            st.rerun()
        render_step_footer(0, 2, "Proceed to 3. Show Job Searches")
    else:
        col_r1, col_r2 = st.columns([1, 1])

        with col_r1:
            st.subheader("👤 Candidate Profile Coordinates")
            st.markdown(f"""
            <div class="job-card">
                <h4 style="margin: 0; color: #ffffff;">{res.name}</h4>
                <div style="color: #60a5fa; margin-top: 4px; font-weight: 600;">{res.preferred_role} • {res.experience_years} yrs exp</div>
                <hr style="border-color: #1f2937;">
                <p style="margin: 4px 0;"><strong>📧 Email:</strong> {res.email or 'Not provided'}</p>
                <p style="margin: 4px 0;"><strong>📱 Phone:</strong> {res.phone or 'Not provided'}</p>
                <p style="margin: 4px 0;"><strong>📍 Home Location:</strong> {res.location or 'Not provided'}</p>
                <p style="margin: 4px 0;"><strong>🎯 Preferred Work Location:</strong> {res.preferred_location or 'Not provided'}</p>
            </div>
            """, unsafe_allow_html=True)

            st.subheader("🛠 Verified Skills Stack")
            skills_html = "".join([f'<span class="skill-tag">{s}</span>' for s in res.skills])
            st.markdown(skills_html or "<span class='text-muted'>No verified skills</span>", unsafe_allow_html=True)

            if res.career_summary:
                st.markdown("##### Professional Summary")
                st.info(res.career_summary)

        with col_r2:
            st.subheader("📊 6-Dimension ATS Audit")
            score_val = ats.score if ats else 0.0
            offset = 251.2 - (251.2 * score_val / 100)
            
            st.markdown(f"""
            <div class="stat-card" style="padding: 1.5rem; margin-bottom: 1rem; display: flex; flex-direction: column; align-items: center;">
                <span style="color: #94a3b8; text-transform: uppercase; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 8px;">Overall ATS Score</span>
                <div style="position: relative; width: 140px; height: 140px; margin-bottom: 12px;">
                    <svg viewBox="0 0 100 100" style="transform: rotate(-90deg); width: 140px; height: 140px;">
                        <defs>
                            <linearGradient id="stScoreGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#6366f1" />
                                <stop offset="100%" stop-color="#ec4899" />
                            </linearGradient>
                        </defs>
                        <circle cx="50" cy="50" r="40" fill="none" stroke="#1f2937" stroke-width="10" />
                        <circle cx="50" cy="50" r="40" fill="none" stroke="url(#stScoreGrad)" stroke-width="10" stroke-linecap="round" stroke-dasharray="251.2" stroke-dashoffset="{offset}" />
                    </svg>
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                        <div style="font-size: 2rem; font-weight: 800; color: #ffffff; line-height: 1;">{score_val:.0f}</div>
                        <div style="font-size: 0.65rem; color: #94a3b8; text-transform: uppercase; font-weight: 700;">Out of 100</div>
                    </div>
                </div>
                <span class="score-pill-high">★ Calibrated ATS Screening</span>
            </div>
            """, unsafe_allow_html=True)

            if ats:
                st.progress(min(1.0, (ats.contact_score or 0) / 10), text=f"Contact Information: {ats.contact_score or 0}/10")
                st.progress(min(1.0, (ats.skills_score or 0) / 35), text=f"Skills Alignment: {ats.skills_score or 0}/35")
                st.progress(min(1.0, (ats.experience_score or 0) / 20), text=f"Experience Fit: {ats.experience_score or 0}/20")
                st.progress(min(1.0, (ats.education_score or 0) / 15), text=f"Education Verification: {ats.education_score or 0}/15")
                st.progress(min(1.0, (ats.projects_score or 0) / 15), text=f"Projects Demonstrated: {ats.projects_score or 0}/15")
                st.progress(min(1.0, (ats.certifications_score or 0) / 5), text=f"Certifications: {ats.certifications_score or 0}/5")

                st.markdown("##### ✅ Strengths & Actionable Advice")
                for s in (ats.strengths or [])[:2]:
                    st.write(f"• **Strength:** {s}")
                for sug in (ats.suggestions or [])[:2]:
                    st.write(f"• **Suggestion:** {sug}")

        render_step_footer(0, 2, "Proceed to 3. Show Job Searches")


# ==================================================================
# STEP 3: SHOW JOB SEARCHES
# ==================================================================
elif cur_idx == 2:
    st.markdown("""
    <div class="step-banner">
        <strong>Step 3 of 7 — Show Job Searches</strong><br>
        Curated opportunities matched specifically against your resume, verified skills stack, and experience level.
    </div>
    """, unsafe_allow_html=True)

    res_profile = st.session_state.resume_data
    has_res = bool(st.session_state.raw_resume_text or (res_profile and res_profile.skills))
    
    if has_res:
        skills_preview = ', '.join(res_profile.skills[:4]) + ('...' if len(res_profile.skills) > 4 else '')
        st.success(f"🎯 **Personalized Resume Matching Active:** Filtered for **{res_profile.preferred_role or 'Candidate'}** • **{res_profile.experience_years} yrs experience** • **{len(res_profile.skills)} skills** ({skills_preview})")
    else:
        st.info("💡 **Tip:** Upload your resume in Step 1 to automatically calibrate job search results to your exact skills and experience level.")

    # Search & Filter Controls
    sc1, sc2, sc3 = st.columns([2, 1, 1])
    with sc1:
        default_role_val = st.session_state.target_role or (res_profile.preferred_role if has_res else "Data Analyst")
        target_role_input = st.text_input("Role Title Filter:", value=default_role_val)
    with sc2:
        min_fit = st.slider("Min Match Fit %:", min_value=30, max_value=90, value=50, step=5)
    with sc3:
        st.write("&nbsp;")
        if st.button("🔍 Fetch Live APIs", type="primary", use_container_width=True):
            with st.spinner("Fetching live jobs from LinkedIn, Adzuna, Remotive, and connected APIs..."):
                fresh = execute_job_collection(role=target_role_input, location=st.session_state.preferred_location)
                st.session_state.collected_jobs = fresh
                st.session_state.matched_jobs = match_jobs(st.session_state.resume_data, fresh)
            st.success(f"Fetched {len(fresh)} opportunities!")
            st.rerun()

    if has_res:
        filtered_jobs = [j for j in st.session_state.matched_jobs if (j.match_score or 0) >= min_fit]
    else:
        filtered_jobs = list(st.session_state.collected_jobs)
    
    if target_role_input and target_role_input.strip():
        q = target_role_input.lower().strip()
        filtered_jobs = [j for j in filtered_jobs if q in j.title.lower() or any(q in s.lower() for s in (j.skills or [])) or any(w in j.title.lower() for w in q.split() if len(w) > 3)]

    if has_res:
        st.caption(f"Showing **{len(filtered_jobs)} tailored opportunities** matching your candidate criteria:")
    else:
        st.caption(f"Showing **{len(filtered_jobs)} opportunities in Discovery Mode** (Upload resume in Step 1 to evaluate personalized match scores):")

    if not filtered_jobs:
        st.info("No openings match this fit threshold. Lower the slider above or fetch fresh openings.")
    else:
        for job in filtered_jobs:
            if has_res:
                score = job.match_score or 75.0
                pill_class = "score-pill-high" if score >= 65 else "score-pill-med"
                badge_html = f'<span class="{pill_class}">★ {score:.1f}% Match</span>'
            else:
                score = None
                badge_html = '<span style="background: rgba(100, 116, 139, 0.2); color: #94a3b8; border: 1px solid rgba(100, 116, 139, 0.4); border-radius: 20px; padding: 4px 14px; font-weight: 600; font-size: 0.88rem;">👁 Discovery</span>'
            
            with st.container():
                st.markdown(f"""
                <div class="job-card">
                    <div style="display: flex; justify-content: space-between; align-items: start; flex-wrap: wrap; gap: 8px;">
                        <div>
                            <h3 style="margin: 0; color: #ffffff; font-size: 1.25rem;">{job.title}</h3>
                            <div style="color: #60a5fa; font-weight: 600; font-size: 0.92rem; margin-top: 2px;">
                                {job.company} 
                                <span style="color: #94a3b8; font-weight: normal;">• 📍 {job.location} • 💰 {job.salary} • 🌐 {job.provider}</span>
                            </div>
                        </div>
                        {badge_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_details, col_actions = st.columns([3, 1])
                with col_details:
                    if has_res:
                        match_html = "".join([f'<span class="skill-match">✔ {s}</span>' for s in (job.matching_skills or [])])
                        gap_html = "".join([f'<span class="skill-gap">+ {s}</span>' for s in (job.missing_skills or [])])
                        
                        if match_html:
                            st.markdown(f"**Matched Skills:** {match_html}", unsafe_allow_html=True)
                        if gap_html:
                            st.markdown(f"**Missing Skills to Feature:** {gap_html}", unsafe_allow_html=True)
                    else:
                        req_html = "".join([f'<span class="skill-tag">🏷 {s}</span>' for s in (job.skills or [])[:5]])
                        if req_html:
                            st.markdown(f"**Required Skills:** {req_html}", unsafe_allow_html=True)
                    if job.description:
                        st.caption(job.description[:180] + "...")

                with col_actions:
                    if job.apply_url and job.apply_url != "#":
                        st.link_button("🚀 Apply Now", job.apply_url, type="primary", use_container_width=True)
                    else:
                        search_url = f"https://www.linkedin.com/jobs/search/?keywords={job.title}+{job.company}"
                        st.link_button("🚀 Apply on LinkedIn", search_url, type="primary", use_container_width=True)

                    if st.button(f"➕ Save to CRM", key=f"crm_{job.title}_{job.company}", use_container_width=True):
                        add_or_update_application({
                            "id": f"app_{uuid.uuid4().hex[:8]}",
                            "company": job.company,
                            "role": job.title,
                            "location": job.location,
                            "salary": job.salary,
                            "apply_url": job.apply_url,
                            "status": "applied",
                            "date_applied": datetime.now().strftime("%Y-%m-%d"),
                            "notes": f"Saved from Job Searches. Match Fit: {score:.1f}%" if score is not None else "Saved from Job Searches (Discovery Mode)"
                        })
                        st.toast(f"Saved {job.title} at {job.company} to Application CRM!", icon="💼")

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    render_step_footer(1, 3, "Proceed to 4. Prepare for Interview")


# ==================================================================
# STEP 4: PREPARE FOR INTERVIEW
# ==================================================================
elif cur_idx == 3:
    st.markdown("""
    <div class="step-banner">
        <strong>Step 4 of 7 — Prepare for Interview</strong><br>
        Generate realistic mock interview questions, technical scenarios, and STAR behavioral answers customized to your target company.
    </div>
    """, unsafe_allow_html=True)

    int_col1, int_col2 = st.columns([1, 1])

    with int_col1:
        st.subheader("🎯 Interview Simulation Settings")
        
        target_co = st.selectbox(
            "Target Company:",
            ["Microsoft", "Amazon", "Google", "TCS", "Infosys", "Deloitte", "Startup", "Custom"],
            index=0
        )
        if target_co == "Custom":
            target_co = st.text_input("Enter Company Name:", value="Target Enterprise")

        target_round = st.selectbox(
            "Interview Round Type:",
            ["Technical Deep Dive", "Data Modeling & SQL", "Behavioral STAR", "HR & Culture Fit"],
            index=0
        )
        
        int_role = st.text_input("Interview Role:", value=st.session_state.target_role)
        q_count = st.slider("Number of Questions:", min_value=3, max_value=8, value=4)

        gen_int_btn = st.button("🎙️ Generate Mock Interview Questions", type="primary", use_container_width=True)

    with int_col2:
        st.subheader("📝 Interview Questions & Model Answers")

        if gen_int_btn or "cached_questions" in st.session_state:
            if gen_int_btn:
                with st.spinner(f"Simulating {target_co} {target_round} interview..."):
                    q_data = generate_interview_questions(
                        role=int_role,
                        skills=st.session_state.resume_data.skills,
                        resume_context=st.session_state.resume_data.career_summary,
                        question_count=q_count,
                        company=target_co,
                        round_type=target_round
                    )
                    st.session_state.cached_questions = q_data.get("questions", [])

            questions = st.session_state.get("cached_questions", [])
            for idx, q_item in enumerate(questions):
                with st.expander(f"Question {idx+1}: {q_item.get('question', '')}", expanded=(idx==0)):
                    st.markdown(f"**Type:** `{q_item.get('type', 'Technical')}`")
                    st.info(f"💡 **Key Talking Points:** {q_item.get('answer_tips', 'Focus on concrete metrics and design choices.')}")
                    st.success(f"🎯 **Model Answer:** {q_item.get('sample_answer', 'In my previous project, I solved this by...')}")
                    
                    st.text_area(f"Practice Your Answer (Q{idx+1}):", height=80, key=f"ans_{idx}", placeholder="Type your answer here to self-evaluate...")
        else:
            st.info("Configure your interview settings on the left and click 'Generate Mock Interview Questions'.")

    render_step_footer(2, 4, "Proceed to 5. Cover Letter Preparation")


# ==================================================================
# STEP 5: COVER LETTER PREPARATION
# ==================================================================
elif cur_idx == 4:
    st.markdown("""
    <div class="step-banner">
        <strong>Step 5 of 7 — Cover Letter Preparation</strong><br>
        Create a compelling, professional cover letter highlighting your skills, achievements, and motivation for the target employer.
    </div>
    """, unsafe_allow_html=True)

    cl_col1, cl_col2 = st.columns([1, 1])

    top_companies = list({j.company for j in st.session_state.matched_jobs[:6]}) or ["Google", "Amazon", "Microsoft"]

    with cl_col1:
        st.subheader("🎯 Target Opportunity")
        cl_company = st.selectbox("Company Name:", top_companies)
        cl_role = st.text_input("Target Position:", value=st.session_state.target_role)
        cl_desc = st.text_area(
            "Job Description Context:",
            value="Looking for a Data Analyst skilled in Python, SQL query optimization, data modeling, Tableau dashboard development, and business analytics. Strong communication and ETL experience preferred.",
            height=140
        )
        gen_cl_btn = st.button("✨ Generate Tailored Cover Letter", type="primary", use_container_width=True)

    with cl_col2:
        st.subheader("📄 Tailored Cover Letter")

        if gen_cl_btn or "cached_cover_letter" in st.session_state:
            if gen_cl_btn:
                with st.spinner("Generating tailored cover letter..."):
                    cl_result = generate_cover_letter(
                        name=st.session_state.resume_data.name,
                        skills=st.session_state.resume_data.skills,
                        job_title=cl_role,
                        company=cl_company,
                        job_desc=cl_desc
                    )
                    st.session_state.cached_cover_letter = cl_result

            cl = st.session_state.get("cached_cover_letter", {})
            
            # Format letter as text
            body_text = "\n\n".join(cl.get("body_paragraphs", []))
            full_letter_str = (
                f"{st.session_state.resume_data.name}\n"
                f"{st.session_state.resume_data.email} | {st.session_state.resume_data.phone}\n\n"
                f"Subject: {cl.get('subject', 'Application')}\n\n"
                f"{cl.get('salutation', 'Dear Hiring Team,')}\n\n"
                f"{cl.get('introduction', '')}\n\n"
                f"{body_text}\n\n"
                f"{cl.get('conclusion', '')}\n\n"
                f"{cl.get('sign_off', 'Sincerely,')}"
            )

            st.markdown(f"""
            <div class="letter-paper">
                <div style="font-size: 0.88rem; color: #94a3b8; margin-bottom: 1rem;">
                    <strong style="color: #ffffff; font-size: 1.1rem;">{st.session_state.resume_data.name}</strong><br>
                    {st.session_state.resume_data.email} | {st.session_state.resume_data.phone}
                </div>
                <p><strong>Subject:</strong> {cl.get('subject', 'Job Application')}</p>
                <p>{cl.get('salutation', 'Dear Hiring Team,')}</p>
                <p>{cl.get('introduction', '')}</p>
                {''.join([f'<p>{p}</p>' for p in cl.get('body_paragraphs', [])])}
                <p>{cl.get('conclusion', '')}</p>
                <p>{cl.get('sign_off', 'Sincerely,')}</p>
            </div>
            """, unsafe_allow_html=True)

            st.download_button(
                "💾 Download Cover Letter (.txt)",
                data=full_letter_str,
                file_name=f"Cover_Letter_{cl_company.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.info("Select a target company on the left and click 'Generate Tailored Cover Letter'.")

    render_step_footer(3, 5, "Proceed to 6. Mail Preparation")


# ==================================================================
# STEP 6: MAIL PREPARATION
# ==================================================================
elif cur_idx == 5:
    st.markdown("""
    <div class="step-banner">
        <strong>Step 6 of 7 — Mail Preparation</strong><br>
        Generate high-converting cold outreach emails, LinkedIn InMail notes, and formal job application emails.
    </div>
    """, unsafe_allow_html=True)

    mail_col1, mail_col2 = st.columns([1, 1])

    with mail_col1:
        st.subheader("📬 Mail Configuration")
        mail_company = st.text_input("Target Company Name:", value="Google")
        mail_role = st.text_input("Position Title:", value=st.session_state.target_role)
        mail_recruiter = st.text_input("Recipient / Hiring Manager Name:", value="Alex Mercer")
        
        gen_mail_btn = st.button("✉️ Generate Application & Outreach Emails", type="primary", use_container_width=True)

    with mail_col2:
        st.subheader("📨 Generated Email Templates")

        if gen_mail_btn or "cached_emails" in st.session_state:
            if gen_mail_btn:
                with st.spinner("Writing personalized email suite..."):
                    res = st.session_state.resume_data
                    emails_data = generate_job_emails(
                        name=res.name,
                        skills=res.skills,
                        role=mail_role,
                        company=mail_company,
                        email=res.email,
                        phone=res.phone,
                        resume_context=res.career_summary
                    )
                    st.session_state.cached_emails = emails_data

            em = st.session_state.get("cached_emails", {})
            
            tab_cold, tab_inmail, tab_followup, tab_app = st.tabs([
                "❄️ Cold Outreach",
                "🔗 LinkedIn InMail",
                "⏰ Follow-Up",
                "📄 Formal Application"
            ])

            with tab_cold:
                cold = em.get("cold_outreach", {})
                st.markdown(f"**Subject:** `{cold.get('subject', 'Application')}`")
                st.text_area("Email Body:", cold.get("body", ""), height=220, key="txt_cold")

            with tab_inmail:
                inmail = em.get("linkedin_inmail", {})
                st.markdown(f"**Note Length:** `< 300 characters`")
                st.text_area("InMail Body:", inmail.get("body", ""), height=150, key="txt_inmail")

            with tab_followup:
                follow = em.get("follow_up_email", {})
                st.markdown(f"**Subject:** `{follow.get('subject', 'Follow Up')}`")
                st.text_area("Follow-up Body:", follow.get("body", ""), height=200, key="txt_follow")

            with tab_app:
                app_mail = em.get("job_application", {})
                st.markdown(f"**Subject:** `{app_mail.get('subject', 'Job Application')}`")
                st.text_area("Application Body:", app_mail.get("body", ""), height=220, key="txt_app")
        else:
            st.info("Fill in the company and position details on the left and click 'Generate Application & Outreach Emails'.")

    render_step_footer(4, 6, "Proceed to 7. Application CRM")


# ==================================================================
# STEP 7: APPLICATION CRM
# ==================================================================
elif cur_idx == 6:
    st.markdown("""
    <div class="step-banner">
        <strong>Step 7 of 7 — Application CRM</strong><br>
        Track and advance your job applications across every stage: Saved, Applied, Interviewing, Offer, and Rejected.
    </div>
    """, unsafe_allow_html=True)

    # Add Application Form in Expander
    with st.expander("➕ Add New Application to CRM", expanded=False):
        with st.form("new_app_form"):
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                app_comp = st.text_input("Company Name:", value="Amazon")
                app_role = st.text_input("Role Title:", value="Data Analyst")
            with fc2:
                app_loc = st.text_input("Location:", value="Hyderabad / Remote")
                app_sal = st.text_input("Salary:", value="₹12 - ₹18 LPA")
            with fc3:
                app_stg = st.selectbox("Initial Stage:", ["saved", "applied", "interview", "offer", "rejected"])
                app_date = st.date_input("Date Applied:", datetime.now())

            submit_app = st.form_submit_button("Save Application", type="primary")
            if submit_app and app_comp and app_role:
                add_or_update_application({
                    "id": f"app_{uuid.uuid4().hex[:8]}",
                    "company": app_comp,
                    "role": app_role,
                    "location": app_loc,
                    "salary": app_sal,
                    "status": app_stg,
                    "date_applied": app_date.strftime("%Y-%m-%d"),
                    "notes": "Added manually via Application CRM"
                })
                st.success(f"Added {app_role} at {app_comp} to CRM!")
                st.rerun()

    # Load All Current Applications from CRM
    all_apps = get_all_applications()
    stages = ["saved", "applied", "interview", "offer", "rejected"]
    counts = {s: len([a for a in all_apps if a.get("status") == s]) for s in stages}

    # Metric Row
    m_cols = st.columns(5)
    stage_titles = {"saved": "Saved", "applied": "Applied", "interview": "Interview", "offer": "Offer", "rejected": "Rejected"}
    for idx, s in enumerate(stages):
        with m_cols[idx]:
            st.metric(stage_titles[s], counts[s])

    st.markdown("---")
    st.subheader("📋 Active Applications Pipeline")

    # Display applications grouped by stage
    for stage_key in stages:
        stage_apps = [a for a in all_apps if a.get("status") == stage_key]
        if stage_apps:
            st.markdown(f"##### 📌 {stage_titles[stage_key]} ({len(stage_apps)})")
            for a in stage_apps:
                with st.container():
                    st.markdown(f"""
                    <div class="job-card">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <h4 style="margin: 0; color: #ffffff;">{a.get('role', 'Role')}</h4>
                                <div style="color: #60a5fa; font-size: 0.92rem;">
                                    {a.get('company', 'Company')} • 📍 {a.get('location', 'N/A')} • 💰 {a.get('salary', 'Competitive')}
                                </div>
                                <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 4px;">
                                    Applied: {a.get('date_applied', 'N/A')} • Follow-up due: {a.get('followup_date', 'N/A')}
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    c_mv, c_del = st.columns([3, 1])
                    with c_mv:
                        new_stage = st.selectbox(
                            "Move stage:",
                            stages,
                            index=stages.index(stage_key),
                            key=f"stage_sel_{a.get('id')}",
                            label_visibility="collapsed"
                        )
                        if new_stage != stage_key:
                            a["status"] = new_stage
                            add_or_update_application(a)
                            st.rerun()
                    with c_del:
                        if st.button("🗑️ Delete", key=f"del_{a.get('id')}", use_container_width=True):
                            delete_application(a.get("id"))
                            st.rerun()

    render_step_footer(5, None)
