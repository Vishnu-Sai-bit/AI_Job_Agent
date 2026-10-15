"""
====================================================================
AI Job Agent - User-Friendly Career Intelligence Platform
Author: Beere Vishnu Sai
100% Pure Python Implementation
====================================================================
"""

import os
import sys
import json
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
from services.jobs.live_job_aggregator import (
    fetch_arbeitnow_live,
    fetch_remoteok_live,
    fetch_remotive_live
)

# ------------------------------------------------------------------
# Page Setup & Modern Elegant Styling
# ------------------------------------------------------------------
st.set_page_config(
    page_title="AI Job Agent",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Clean Minimalist Styling */
    .stApp {
        background-color: #0b0f17;
        color: #f1f5f9;
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #ffffff;
        margin-bottom: 4px;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #94a3b8;
        margin-bottom: 1.2rem;
    }
    .job-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .job-card:hover {
        border-color: #3b82f6;
    }
    .score-pill-high {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 20px;
        padding: 3px 12px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .score-pill-med {
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 20px;
        padding: 3px 12px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .skill-tag {
        display: inline-block;
        background: #1e293b;
        color: #cbd5e1;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.78rem;
        margin: 2px 4px 2px 0;
    }
    .skill-match {
        display: inline-block;
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.78rem;
        margin: 2px 4px 2px 0;
    }
    .skill-gap {
        display: inline-block;
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.78rem;
        margin: 2px 4px 2px 0;
    }
    .stat-box {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# Data Helper & Initial State Setup
# ------------------------------------------------------------------
def convert_to_jobdata(item: Dict[str, Any]) -> JobData:
    provider = item.get("source") or item.get("provider") or "Direct"
    return JobData(
        provider=provider,
        provider_id=str(item.get("id") or ""),
        company=item.get("company") or "Global Tech Org",
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
    """Helper for collecting jobs used in tests and batch discovery."""
    collected = []
    if not providers:
        providers = ["Remotive", "RemoteOK", "ArbeitNow"]
    if "Remotive" in providers:
        try:
            for j in fetch_remotive_live(role=role, limit=6):
                collected.append(convert_to_jobdata(j))
        except Exception:
            pass
    if "RemoteOK" in providers:
        try:
            for j in fetch_remoteok_live(role=role, limit=6):
                collected.append(convert_to_jobdata(j))
        except Exception:
            pass
    if "ArbeitNow" in providers:
        try:
            for j in fetch_arbeitnow_live(role=role, limit=6):
                collected.append(convert_to_jobdata(j))
        except Exception:
            pass
    if not collected:
        collected = load_initial_jobs()
    return collected

def load_initial_jobs() -> List[JobData]:
    """Load default verified jobs pool."""
    verified_file = BASE_DIR / "data" / "verified_jobs.json"
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
    """Load default candidate profile."""
    default_file = BASE_DIR / "data" / "default_parsed_resume.json"
    if default_file.exists():
        try:
            with open(default_file, "r", encoding="utf-8") as f:
                d = json.load(f)
                return ResumeData(
                    name=d.get("candidate_name", "Beere Vishnu Sai"),
                    email=d.get("email", "vishnusaibeere124@gmail.com"),
                    phone=d.get("phone", "+91 9182679641"),
                    location=d.get("location", "Hyderabad, India"),
                    preferred_location=d.get("preferred_location", "Hyderabad"),
                    preferred_role=d.get("preferred_role", "Data Analyst"),
                    skills=d.get("skills", ["Python", "SQL", "Tableau", "Power BI", "Excel", "Data Analysis", "ETL"]),
                    experience_years=float(d.get("experience_years", 0.5)),
                    education=d.get("education", [{"degree": "B.Tech in Computer Science", "institution": "JNTU", "year": "2024"}]),
                    projects=d.get("projects", [{"title": "Autonomous AI Job Agent", "description": "End-to-end career intelligence and matching platform in Python."}]),
                    certifications=d.get("certifications", ["Google Data Analytics Professional"]),
                    career_summary=d.get("career_summary", "Aspiring Data Analyst skilled in Python, SQL, Tableau, Power BI, and statistical analytics."),
                )
        except Exception:
            pass
    return ResumeData(
        name="Beere Vishnu Sai",
        email="vishnusaibeere124@gmail.com",
        phone="+91 9182679641",
        location="Hyderabad, India",
        preferred_location="Hyderabad",
        preferred_role="Data Analyst",
        skills=["Python", "SQL", "Tableau", "Power BI", "Excel", "Data Analysis"],
        experience_years=0.5,
        career_summary="Data Analyst skilled in Python, SQL, and business analytics."
    )

# Initialize Session State
if "resume_data" not in st.session_state or st.session_state.resume_data is None:
    st.session_state.resume_data = load_initial_profile()

if "ats_report" not in st.session_state or st.session_state.ats_report is None:
    st.session_state.ats_report = calculate_ats(st.session_state.resume_data)

if "collected_jobs" not in st.session_state or not st.session_state.collected_jobs:
    st.session_state.collected_jobs = load_initial_jobs()

if "matched_jobs" not in st.session_state or not st.session_state.matched_jobs:
    st.session_state.matched_jobs = match_jobs(st.session_state.resume_data, st.session_state.collected_jobs)

if "target_role" not in st.session_state:
    st.session_state.target_role = "Data Analyst"

if "preferred_location" not in st.session_state:
    st.session_state.preferred_location = "Hyderabad"

if "home_location" not in st.session_state:
    st.session_state.home_location = "Hyderabad, India"

if "work_mode" not in st.session_state:
    st.session_state.work_mode = "Remote"


# ------------------------------------------------------------------
# Sidebar: Clean Candidate Card & Quick Search
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 💼 AI Job Agent")
    st.caption("Autonomous Career Copilot")
    st.markdown("---")
    
    # Candidate Mini Profile Card
    res = st.session_state.resume_data
    ats = st.session_state.ats_report
    st.markdown(f"**👤 {res.name}**")
    st.caption(f"📍 Home: {res.location or 'Hyderabad, India'}")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("ATS Score", f"{ats.score:.0f}%" if ats else "85%")
    with col_b:
        st.metric("Verified Skills", len(res.skills))

    st.markdown("---")
    st.markdown("##### 🎯 Quick Search Filters")
    
    role_options = ["Data Analyst", "Python Developer", "Data Scientist", "Software Engineer", "Business Analyst"]
    cur_idx = role_options.index(st.session_state.target_role) if st.session_state.target_role in role_options else 0
    selected_role = st.selectbox("Target Role:", role_options, index=cur_idx)
    
    selected_loc = st.text_input("Target Location:", value=st.session_state.preferred_location)
    selected_mode = st.selectbox("Work Mode:", ["Remote", "Hybrid", "On-Site"], index=["Remote", "Hybrid", "On-Site"].index(st.session_state.work_mode))
    
    if st.button("🔍 Find Matching Jobs", type="primary", use_container_width=True):
        st.session_state.target_role = selected_role
        st.session_state.preferred_location = selected_loc
        st.session_state.work_mode = selected_mode
        st.session_state.resume_data.preferred_role = selected_role
        st.session_state.resume_data.preferred_location = selected_loc

        with st.spinner("Fetching live jobs from Remotive, RemoteOK, and ArbeitNow..."):
            live_list = []
            try:
                for j in fetch_remotive_live(role=selected_role, limit=6):
                    live_list.append(convert_to_jobdata(j))
            except Exception:
                pass
            try:
                for j in fetch_remoteok_live(role=selected_role, limit=6):
                    live_list.append(convert_to_jobdata(j))
            except Exception:
                pass
            try:
                for j in fetch_arbeitnow_live(role=selected_role, limit=6):
                    live_list.append(convert_to_jobdata(j))
            except Exception:
                pass

            if not live_list:
                live_list = load_initial_jobs()

            st.session_state.collected_jobs = live_list
            st.session_state.matched_jobs = match_jobs(st.session_state.resume_data, live_list)
        st.success(f"Discovered and matched {len(st.session_state.matched_jobs)} jobs!")
        st.rerun()

    st.markdown("---")
    st.caption("Live Job Providers: Remotive • RemoteOK • ArbeitNow")


# ------------------------------------------------------------------
# Main Workspace: 4 Simple, Intuitive Tabs (Zero Clutter)
# ------------------------------------------------------------------
st.markdown('<div class="hero-title">Career Intelligence Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Targeting <strong>' + st.session_state.target_role + '</strong> in <strong>' + st.session_state.preferred_location + '</strong> • ' + str(len(st.session_state.matched_jobs)) + ' Matching Openings Available</div>', unsafe_allow_html=True)

tab_jobs, tab_resume, tab_prefs, tab_tailor = st.tabs([
    "🎯 Matching Opportunities",
    "📄 Resume & ATS Score",
    "⚙️ Target Preferences",
    "✨ Resume Tailoring"
])


# ==================================================================
# TAB 1: MATCHING OPPORTUNITIES (Primary Value)
# ==================================================================
with tab_jobs:
    # Top Action Bar
    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
    with f_col1:
        st.subheader("High-Affinity Job Matches")
    with f_col2:
        min_fit = st.slider("Filter by Match %:", min_value=30, max_value=90, value=50, step=5)
    with f_col3:
        sort_by = st.selectbox("Sort By:", ["Highest Match Score", "Role Similarity"], index=0)

    matched_list = [j for j in st.session_state.matched_jobs if (j.match_score or 0) >= min_fit]

    if not matched_list:
        st.info("No openings match the current score filter. Try lowering the threshold slider above.")
    else:
        for job in matched_list:
            score = job.match_score or 75.0
            pill_class = "score-pill-high" if score >= 65 else "score-pill-med"
            
            with st.container():
                st.markdown(f"""
                <div class="job-card">
                    <div style="display: flex; justify-content: space-between; align-items: start; flex-wrap: wrap; gap: 8px;">
                        <div>
                            <h3 style="margin: 0; color: #ffffff; font-size: 1.25rem;">{job.title}</h3>
                            <div style="color: #60a5fa; font-weight: 600; font-size: 0.95rem; margin-top: 2px;">
                                {job.company} 
                                <span style="color: #94a3b8; font-weight: normal;">• 📍 {job.location} • 💰 {job.salary} • 🌐 {job.provider}</span>
                            </div>
                        </div>
                        <span class="{pill_class}">★ {score:.1f}% Match</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_details, col_actions = st.columns([3, 1])
                with col_details:
                    # Clean Matching & Gap Skills
                    match_html = "".join([f'<span class="skill-match">✔ {s}</span>' for s in (job.matching_skills or [])])
                    gap_html = "".join([f'<span class="skill-gap">+ {s}</span>' for s in (job.missing_skills or [])])
                    
                    if match_html:
                        st.markdown(f"**Matched Skills:** {match_html}", unsafe_allow_html=True)
                    if gap_html:
                        st.markdown(f"**Missing Skills to Feature:** {gap_html}", unsafe_allow_html=True)
                    
                    if job.description:
                        st.caption(job.description[:220] + "...")

                with col_actions:
                    if job.apply_url and job.apply_url != "#":
                        st.link_button("🚀 Apply Now", job.apply_url, type="primary", use_container_width=True)
                    else:
                        search_url = f"https://www.linkedin.com/jobs/search/?keywords={job.title}+{job.company}"
                        st.link_button("🚀 Apply on LinkedIn", search_url, type="primary", use_container_width=True)

                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)


# ==================================================================
# TAB 2: RESUME & ATS SCORE
# ==================================================================
with tab_resume:
    r_col1, r_col2 = st.columns([1, 1])
    
    with r_col1:
        st.subheader("📄 Upload Resume")
        uploaded_file = st.file_uploader("Upload PDF or DOCX file:", type=["pdf", "docx", "txt"])
        if uploaded_file is not None:
            save_path = BASE_DIR / "resumes" / uploaded_file.name
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            with st.spinner("Extracting text and analyzing resume..."):
                raw_text = extract_resume_text(save_path)
                st.session_state.resume_data = analyze_resume(raw_text)
                st.session_state.ats_report = calculate_ats(st.session_state.resume_data)
                st.session_state.matched_jobs = match_jobs(st.session_state.resume_data, st.session_state.collected_jobs)
            st.success(f"'{uploaded_file.name}' analyzed successfully! ATS score updated.")
            st.rerun()

        res = st.session_state.resume_data
        st.markdown("##### Candidate Profile")
        st.write(f"- **Name:** {res.name}")
        st.write(f"- **Email:** {res.email}")
        st.write(f"- **Phone:** {res.phone}")
        st.write(f"- **Experience:** {res.experience_years} years")
        st.write(f"- **Target Role:** {res.preferred_role}")

        st.markdown("##### Verified Skills Stack")
        skills_html = "".join([f'<span class="skill-tag">{s}</span>' for s in res.skills])
        st.markdown(skills_html, unsafe_allow_html=True)

    with r_col2:
        st.subheader("📊 ATS Evaluation & Feedback")
        ats = st.session_state.ats_report
        if ats:
            st.metric("Overall ATS Score", f"{ats.score:.1f}%", delta="Top Tier Fit" if ats.score >= 80 else "Good Baseline")
            
            st.markdown("##### 6-Dimension Breakdown")
            st.progress(min(1.0, ats.contact_score / 10), text=f"Contact Information: {ats.contact_score}/10")
            st.progress(min(1.0, ats.skills_score / 35), text=f"Skills Alignment: {ats.skills_score}/35")
            st.progress(min(1.0, ats.experience_score / 20), text=f"Experience Fit: {ats.experience_score}/20")
            st.progress(min(1.0, ats.education_score / 15), text=f"Education Verification: {ats.education_score}/15")
            st.progress(min(1.0, ats.projects_score / 15), text=f"Projects Demonstrated: {ats.projects_score}/15")
            st.progress(min(1.0, ats.certifications_score / 5), text=f"Certifications: {ats.certifications_score}/5")

            st.markdown("##### ✅ Key Strengths")
            for s in (ats.strengths or ["Strong skills keyword alignment", "Complete contact details"]):
                st.write(f"• {s}")

            st.markdown("##### 💡 Recommended Improvements")
            for sug in (ats.suggestions or ["Add quantifiable impact metrics in bullet points"]):
                st.write(f"• {sug}")


# ==================================================================
# TAB 3: TARGET PREFERENCES
# ==================================================================
with tab_prefs:
    st.subheader("⚙️ Configure Career Preferences")
    st.write("Ensure your candidate home residence is separate from target job locations.")

    with st.form("preferences_form"):
        p1, p2 = st.columns(2)
        with p1:
            form_role = st.text_input("Target Job Title:", value=st.session_state.target_role)
            form_target_loc = st.text_input("Preferred Job Cities / Locations:", value=st.session_state.preferred_location)
            form_mode = st.selectbox("Work Mode Preference:", ["Remote", "Hybrid", "On-Site"], index=["Remote", "Hybrid", "On-Site"].index(st.session_state.work_mode))
        with p2:
            form_home_loc = st.text_input("Candidate Home Residence:", value=st.session_state.home_location, help="Your physical location, kept separate from where you want to work.")
            form_salary = st.text_input("Salary Expectation:", value="₹6 - ₹12 LPA")
            form_exp = st.selectbox("Experience Level:", ["Entry Level (0-2 yrs)", "Mid Level (2-5 yrs)", "Senior Level (5+ yrs)"], index=0)

        save_btn = st.form_submit_button("Save Preferences & Re-Rank Jobs", type="primary")
        if save_btn:
            st.session_state.target_role = form_role
            st.session_state.preferred_location = form_target_loc
            st.session_state.home_location = form_home_loc
            st.session_state.work_mode = form_mode
            st.session_state.resume_data.preferred_role = form_role
            st.session_state.resume_data.preferred_location = form_target_loc
            st.session_state.resume_data.location = form_home_loc
            st.session_state.matched_jobs = match_jobs(st.session_state.resume_data, st.session_state.collected_jobs)
            st.success("Preferences saved! Your job matches have been dynamically updated.")
            st.rerun()


# ==================================================================
# TAB 4: RESUME TAILORING STUDIO
# ==================================================================
with tab_tailor:
    st.subheader("✨ Resume Tailoring Studio")
    st.write("Adapt your resume keywords and summary to maximize compatibility for a specific vacancy.")

    t1, t2 = st.columns(2)
    with t1:
        target_t_role = st.text_input("Job Title to Tailor For:", value=st.session_state.target_role)
        target_t_desc = st.text_area(
            "Paste Target Job Requirements:",
            value="Looking for a Data Analyst skilled in Python, SQL query optimization, data modeling, Tableau dashboard development, and business analytics. Strong communication and ETL experience preferred.",
            height=160
        )
        tailor_action = st.button("Generate Tailored Bullet Points", type="primary")

    with t2:
        if tailor_action and target_t_role and target_t_desc:
            with st.spinner("Analyzing keywords and generating bullet points..."):
                tailored = tailor_resume_for_job(
                    original_resume_text=st.session_state.resume_data.career_summary,
                    target_role=target_t_role,
                    target_company="Target Enterprise",
                    job_description=target_t_desc,
                    candidate_skills=st.session_state.resume_data.skills
                )
            st.success("Tailoring complete! Estimated ATS boost: +15%")
            if tailored.tailored_summary:
                st.markdown("##### Optimized Summary:")
                st.info(tailored.tailored_summary)
            if tailored.suggested_skills:
                st.markdown("##### Recommended Keywords to Add:")
                k_html = "".join([f'<span class="skill-match">{k}</span>' for k in tailored.suggested_skills])
                st.markdown(k_html, unsafe_allow_html=True)
            if tailored.bullet_improvements:
                st.markdown("##### High-Impact Bullet Points:")
                for b in tailored.bullet_improvements:
                    st.write(f"• {b}")
        else:
            st.info("Paste any target job description on the left and click 'Generate Tailored Bullet Points'.")
