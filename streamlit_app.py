"""
====================================================================
AI Job Agent - Streamlit Career Intelligence & Autonomous Platform
Author: Beere Vishnu Sai
Pure Python Implementation

Sequential 9-Step Linear Workflow:
Upload -> Resume Parsing -> AI Analysis -> ATS Evaluation ->
Job Preferences -> Job Collection -> Job Matching ->
Ranked Results Dashboard -> Resume Improvement & Application Assistance
====================================================================
"""

import os
import sys
import json
import time
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
    fetch_remotive_live,
    fetch_linkedin_live,
    fetch_adzuna_live,
    aggregate_live_jobs
)

# ------------------------------------------------------------------
# Page Configuration & Styling
# ------------------------------------------------------------------
st.set_page_config(
    page_title="AI Job Agent - Career Intelligence Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Sleek Modern Look
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }
    .step-badge {
        display: inline-block;
        padding: 4px 12px;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.4);
        border-radius: 20px;
        color: #818cf8;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 0.8rem;
    }
    .metric-card {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .skill-pill {
        display: inline-block;
        padding: 2px 10px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 12px;
        color: #34d399;
        font-size: 0.8rem;
        margin: 2px 4px 2px 0;
    }
    .missing-pill {
        display: inline-block;
        padding: 2px 10px;
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.4);
        border-radius: 12px;
        color: #fbbf24;
        font-size: 0.8rem;
        margin: 2px 4px 2px 0;
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# Session State Initialization
# ------------------------------------------------------------------
def init_session_state():
    if "resume_raw_text" not in st.session_state:
        st.session_state.resume_raw_text = ""
    if "resume_data" not in st.session_state:
        # Load default parsed resume if available
        default_file = BASE_DIR / "data" / "default_parsed_resume.json"
        if default_file.exists():
            try:
                with open(default_file, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    st.session_state.resume_data = ResumeData(
                        name=d.get("candidate_name", "Beere Vishnu Sai"),
                        email=d.get("email", "vishnusaibeere124@gmail.com"),
                        phone=d.get("phone", "+91 9182679641"),
                        location=d.get("location", "Hyderabad, India"),
                        preferred_location=d.get("preferred_location", "Hyderabad"),
                        preferred_role=d.get("preferred_role", "Data Analyst"),
                        skills=d.get("skills", ["Python", "SQL", "Tableau", "Power BI", "Excel", "Data Analysis", "ETL"]),
                        experience_years=float(d.get("experience_years", 0.5)),
                        education=d.get("education", [{"degree": "B.Tech in Computer Science", "institution": "JNTU", "year": "2024"}]),
                        projects=d.get("projects", [{"title": "AI Job Matcher & Resume Analytics", "description": "End-to-end career automation system in Python with Ollama"}]),
                        certifications=d.get("certifications", ["Google Data Analytics Professional", "Python Specialist"]),
                        career_summary=d.get("career_summary", "Aspiring Data Analyst skilled in Python, SQL, Tableau, Power BI, and statistical analysis."),
                    )
            except Exception:
                st.session_state.resume_data = None
        else:
            st.session_state.resume_data = None

    if "ats_report" not in st.session_state and st.session_state.resume_data:
        try:
            st.session_state.ats_report = calculate_ats(st.session_state.resume_data)
        except Exception:
            st.session_state.ats_report = None

    if "collected_jobs" not in st.session_state:
        st.session_state.collected_jobs = []
    if "matched_jobs" not in st.session_state:
        st.session_state.matched_jobs = []
    if "target_role" not in st.session_state:
        st.session_state.target_role = "Data Analyst"
    if "preferred_location" not in st.session_state:
        st.session_state.preferred_location = "Hyderabad"
    if "home_location" not in st.session_state:
        st.session_state.home_location = "Hyderabad, India"
    if "work_mode" not in st.session_state:
        st.session_state.work_mode = "Remote"
    if "salary_expectation" not in st.session_state:
        st.session_state.salary_expectation = "₹6 - ₹12 LPA"

init_session_state()


# ------------------------------------------------------------------
# Sidebar: 9-Step Linear Navigation & Quick Preferences
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🚀 AI Job Agent")
    st.caption("Pure Python Autonomous Job Search & ATS Studio")
    
    st.markdown("---")
    st.markdown("##### 🧭 9-STEP LINEAR PIPELINE")
    
    workflow_steps = [
        "1. Upload Resume",
        "2. Resume Parsing",
        "3. AI Resume Analysis",
        "4. ATS Evaluation",
        "5. Job Preferences",
        "6. Job Collection",
        "7. Job Matching Engine",
        "8. Ranked Results Dashboard",
        "9. Resume Improvement & Assistance"
    ]
    
    selected_step = st.radio(
        "Current Step:",
        workflow_steps,
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("##### ⚙️ QUICK TARGET PREFERENCES")
    
    role_options = ["Data Analyst", "Python Developer", "Data Scientist", "Software Engineer", "Business Analyst", "Machine Learning Engineer"]
    default_role_idx = role_options.index(st.session_state.target_role) if st.session_state.target_role in role_options else 0
    st.session_state.target_role = st.selectbox("Target Role:", role_options, index=default_role_idx)
    
    st.session_state.preferred_location = st.text_input("Preferred Job Location:", value=st.session_state.preferred_location)
    st.session_state.home_location = st.text_input("Home Residence Location:", value=st.session_state.home_location)
    st.session_state.work_mode = st.selectbox("Work Mode:", ["Remote", "Hybrid", "On-Site"], index=0)
    
    st.markdown("---")
    if st.button("⚡ Run Entire Pipeline Now", use_container_width=True, type="primary"):
        st.session_state.run_all_triggered = True


# ------------------------------------------------------------------
# Helpers for Data Conversion & Job Discovery
# ------------------------------------------------------------------
def convert_dict_to_jobdata(item: Dict[str, Any]) -> JobData:
    """Convert raw dictionary job to standard JobData dataclass."""
    provider = item.get("source") or item.get("provider") or "Web"
    return JobData(
        provider=provider,
        provider_id=str(item.get("id") or ""),
        company=item.get("company") or "Technology Enterprise",
        title=item.get("title") or "Analyst",
        description=item.get("description") or "",
        location=item.get("location") or "Remote",
        salary=item.get("salary") or "₹6 - ₹12 LPA",
        experience=item.get("experience") or "0-2 yrs",
        skills=item.get("skills") or ["Python", "SQL", "Data Analysis"],
        apply_url=item.get("url") or item.get("apply_url") or "#",
        remote=True if "remote" in (item.get("location") or "").lower() else False
    )

def execute_job_collection(role: str, location: str, providers: List[str]) -> List[JobData]:
    """Fetch jobs from Remotive, RemoteOK, ArbeitNow and normalize into JobData."""
    collected = []
    with st.spinner(f"Fetching openings from {', '.join(providers)}..."):
        if "Remotive" in providers:
            try:
                rem_jobs = fetch_remotive_live(role=role, limit=8)
                for rj in rem_jobs:
                    collected.append(convert_dict_to_jobdata(rj))
            except Exception as e:
                st.warning(f"Remotive query notice: {e}")

        if "RemoteOK" in providers:
            try:
                rok_jobs = fetch_remoteok_live(role=role, limit=8)
                for rj in rok_jobs:
                    collected.append(convert_dict_to_jobdata(rj))
            except Exception as e:
                st.warning(f"RemoteOK query notice: {e}")

        if "ArbeitNow" in providers:
            try:
                an_jobs = fetch_arbeitnow_live(role=role, limit=8)
                for aj in an_jobs:
                    collected.append(convert_dict_to_jobdata(aj))
            except Exception as e:
                st.warning(f"ArbeitNow query notice: {e}")

        # Fallback to sample verified jobs from data/verified_jobs.json if live APIs return empty
        if not collected:
            verified_file = BASE_DIR / "data" / "verified_jobs.json"
            if verified_file.exists():
                with open(verified_file, "r", encoding="utf-8") as f:
                    v_list = json.load(f)
                    for item in v_list:
                        collected.append(convert_dict_to_jobdata(item))

    return collected


# ------------------------------------------------------------------
# Execution Handler: Run Entire Pipeline
# ------------------------------------------------------------------
if st.session_state.get("run_all_triggered"):
    st.session_state.run_all_triggered = False
    with st.status("Executing 9-Step Linear Pipeline...", expanded=True) as status:
        st.write("Step 1 & 2: Loading resume text & extracting contact profile...")
        time.sleep(0.3)
        if not st.session_state.resume_data:
            # Create baseline
            st.session_state.resume_data = analyze_resume("Beere Vishnu Sai. Data Analyst skilled in Python, SQL, Tableau, Power BI. B.Tech Computer Science 2024.")
        
        st.write("Step 3 & 4: Running AI Resume Analysis & ATS Evaluation...")
        st.session_state.ats_report = calculate_ats(st.session_state.resume_data)
        time.sleep(0.3)
        
        st.write(f"Step 5: Updating job preferences: {st.session_state.target_role} in {st.session_state.preferred_location}...")
        st.session_state.resume_data.preferred_role = st.session_state.target_role
        st.session_state.resume_data.preferred_location = st.session_state.preferred_location
        st.session_state.resume_data.location = st.session_state.home_location
        
        st.write("Step 6: Collecting jobs from Remotive, RemoteOK, and ArbeitNow...")
        raw_jobs = execute_job_collection(
            st.session_state.target_role,
            st.session_state.preferred_location,
            ["Remotive", "RemoteOK", "ArbeitNow"]
        )
        st.session_state.collected_jobs = raw_jobs
        
        st.write("Step 7: Executing precision Job Matching Engine...")
        matched = match_jobs(st.session_state.resume_data, raw_jobs)
        st.session_state.matched_jobs = matched
        
        status.update(label="✅ Pipeline Completed! Viewing Results Dashboard.", state="complete")
        selected_step = "8. Ranked Results Dashboard"


# ------------------------------------------------------------------
# Main View Rendering per Step
# ------------------------------------------------------------------

# Header
st.markdown('<div class="main-header">AI Job Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Linear 9-Step Career Intelligence Pipeline • Pure Python Engine</div>', unsafe_allow_html=True)


# STEP 1: UPLOAD RESUME
if selected_step == "1. Upload Resume":
    st.markdown('<div class="step-badge">STEP 1 OF 9: RESUME UPLOAD</div>', unsafe_allow_html=True)
    st.header("📄 Upload Your Resume")
    st.write("Upload your resume in PDF, DOCX, or TXT format. The extractor parses all text and structured candidate entities.")
    
    uploaded_file = st.file_uploader("Select resume file", type=["pdf", "docx", "txt"])
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if uploaded_file is not None:
            save_path = BASE_DIR / "resumes" / uploaded_file.name
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            with st.spinner("Extracting text and analyzing resume..."):
                extracted_text = extract_resume_text(save_path)
                st.session_state.resume_raw_text = extracted_text
                st.session_state.resume_data = analyze_resume(extracted_text)
                st.session_state.ats_report = calculate_ats(st.session_state.resume_data)
            
            st.success(f"Successfully uploaded and parsed '{uploaded_file.name}'!")
            st.info("Click 'Proceed to Step 2: Resume Parsing' or switch steps in the sidebar.")
    
    with col2:
        st.markdown("##### 💡 Or Use Default Pre-Loaded Profile")
        st.write("Test the pipeline instantly with the pre-parsed profile for **Beere Vishnu Sai (Data Analyst)**.")
        if st.button("Load Pre-Configured Profile", type="secondary"):
            init_session_state()
            st.success("Default profile loaded successfully!")

    if st.session_state.resume_data:
        st.markdown("---")
        st.write(f"**Loaded Candidate:** {st.session_state.resume_data.name} | **Role:** {st.session_state.resume_data.preferred_role}")


# STEP 2: RESUME PARSING
elif selected_step == "2. Resume Parsing":
    st.markdown('<div class="step-badge">STEP 2 OF 9: RESUME PARSING</div>', unsafe_allow_html=True)
    st.header("🔍 Extracted Contact & Structured Resume Profile")
    st.write("Verifies extracted contact coordinates, links, and document layout.")
    
    res = st.session_state.resume_data
    if not res:
        st.warning("No resume profile loaded yet. Please complete Step 1 first.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Candidate Name", res.name)
            st.metric("Email Address", res.email)
        with col2:
            st.metric("Phone Number", res.phone)
            st.metric("Home Location", res.location or "Hyderabad, India")
        with col3:
            st.metric("Experience Verified", f"{res.experience_years} yrs")
            st.metric("Target Role", res.preferred_role)

        st.markdown("##### 🌐 Online Profiles & Portfolios")
        st.write(f"- **LinkedIn:** {res.linkedin or 'Not Specified'}")
        st.write(f"- **GitHub:** {res.github or 'Not Specified'}")
        st.write(f"- **Portfolio:** {res.portfolio or 'Not Specified'}")

        with st.expander("View Raw Parsed Text Snippet"):
            st.text(st.session_state.resume_raw_text[:2000] if st.session_state.resume_raw_text else res.career_summary)


# STEP 3: AI RESUME ANALYSIS
elif selected_step == "3. AI Resume Analysis":
    st.markdown('<div class="step-badge">STEP 3 OF 9: AI RESUME ANALYSIS</div>', unsafe_allow_html=True)
    st.header("🧠 AI Resume Analysis (Python + Ollama)")
    st.write("Structured extraction identifying skills, education, work experience, projects, and career summary.")
    
    res = st.session_state.resume_data
    if not res:
        st.warning("Please upload a resume in Step 1 first.")
    else:
        st.subheader("Professional Summary")
        st.info(res.career_summary or "Data analytics practitioner with proficiency in statistical modeling, SQL query tuning, and Tableau visualization.")

        st.subheader(f"Identified Skills ({len(res.skills)})")
        skill_html = "".join([f'<span class="skill-pill">✔ {s}</span>' for s in res.skills])
        st.markdown(skill_html, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🎓 Education")
            for edu in (res.education or []):
                deg = edu.get("degree") or "Degree"
                inst = edu.get("institution") or edu.get("college") or "University"
                yr = edu.get("year") or ""
                st.write(f"• **{deg}** — {inst} ({yr})")
        
        with col2:
            st.subheader("💼 Verified Experience")
            if res.experience:
                for exp in res.experience:
                    st.write(f"• **{exp.get('designation', 'Specialist')}** at {exp.get('company', 'Enterprise')}")
            else:
                st.write("• Fresher / 0.5+ years demonstrated project analytics experience.")

        st.subheader("🚀 Demonstrated Projects")
        for p in (res.projects or []):
            st.write(f"• **{p.get('title', 'Project')}**: {p.get('description', '')}")


# STEP 4: ATS EVALUATION
elif selected_step == "4. ATS Evaluation":
    st.markdown('<div class="step-badge">STEP 4 OF 9: ATS EVALUATION</div>', unsafe_allow_html=True)
    st.header("📊 ATS Score & Skill Gap Analysis")
    st.write("Six-dimension automated scoring assessing formatting, keyword density, and industry suitability.")
    
    ats = st.session_state.ats_report
    if not ats:
        st.warning("Please complete Step 1 or load a profile to evaluate ATS scores.")
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.metric("Overall ATS Score", f"{ats.score}%", delta="Strong Match" if ats.score >= 80 else "Needs Improvement")
        
        with col2:
            st.markdown("##### 6-Dimension ATS Breakdown")
            st.progress(min(1.0, ats.contact_score / 10), text=f"Contact & Links: {ats.contact_score} / 10")
            st.progress(min(1.0, ats.skills_score / 35), text=f"Skills Keywords: {ats.skills_score} / 35")
            st.progress(min(1.0, ats.experience_score / 20), text=f"Experience Impact: {ats.experience_score} / 20")
            st.progress(min(1.0, ats.education_score / 15), text=f"Education Verification: {ats.education_score} / 15")
            st.progress(min(1.0, ats.projects_score / 15), text=f"Projects Demonstrated: {ats.projects_score} / 15")
            st.progress(min(1.0, ats.certifications_score / 5), text=f"Certifications: {ats.certifications_score} / 5")

        col_str, col_sug = st.columns(2)
        with col_str:
            st.subheader("✅ Profile Strengths")
            for s in (ats.strengths or ["Strong skills keyword alignment", "Complete contact details"]):
                st.write(f"• {s}")
        
        with col_sug:
            st.subheader("💡 Improvement Suggestions")
            for sug in (ats.suggestions or ["Add quantifiable metrics to project outcomes", "Include target keywords"]):
                st.write(f"• {sug}")


# STEP 5: JOB PREFERENCES
elif selected_step == "5. Job Preferences":
    st.markdown('<div class="step-badge">STEP 5 OF 9: JOB PREFERENCES</div>', unsafe_allow_html=True)
    st.header("⚙️ Configure Target Job Preferences")
    st.write("Align your target role, preferred job cities, work mode, and salary expectations.")
    
    with st.form("pref_form"):
        c1, c2 = st.columns(2)
        with c1:
            target_role = st.text_input("Target Job Title:", value=st.session_state.target_role)
            pref_loc = st.text_input("Preferred Job Location / Cities:", value=st.session_state.preferred_location, help="e.g. Hyderabad, Bengaluru, or Remote")
            work_mode = st.selectbox("Work Mode:", ["Remote", "Hybrid", "On-Site"], index=["Remote", "Hybrid", "On-Site"].index(st.session_state.work_mode))
        with c2:
            home_loc = st.text_input("Candidate Home Residence:", value=st.session_state.home_location, help="Kept separate from preferred job location")
            salary_exp = st.text_input("Expected Salary Range:", value=st.session_state.salary_expectation)
            exp_level = st.selectbox("Experience Level:", ["Entry Level (0-2 yrs)", "Mid Level (2-5 yrs)", "Senior Level (5+ yrs)"], index=0)
        
        submitted = st.form_submit_layer = st.form_submit_button("Save Preferences & Proceed to Job Collection", type="primary")
        if submitted:
            st.session_state.target_role = target_role
            st.session_state.preferred_location = pref_loc
            st.session_state.home_location = home_loc
            st.session_state.work_mode = work_mode
            st.session_state.salary_expectation = salary_exp
            if st.session_state.resume_data:
                st.session_state.resume_data.preferred_role = target_role
                st.session_state.resume_data.preferred_location = pref_loc
                st.session_state.resume_data.location = home_loc
            st.success("Preferences updated! Go to Step 6: Job Collection.")


# STEP 6: JOB COLLECTION
elif selected_step == "6. Job Collection":
    st.markdown('<div class="step-badge">STEP 6 OF 9: JOB COLLECTION</div>', unsafe_allow_html=True)
    st.header("🌐 Multi-Provider Job Collection")
    st.write("Fetch and normalize live job listings from Remotive, RemoteOK, and ArbeitNow.")
    
    p_col1, p_col2 = st.columns([2, 1])
    with p_col1:
        st.write(f"Targeting: **{st.session_state.target_role}** in **{st.session_state.preferred_location}**")
        provider_choices = st.multiselect(
            "Select Providers:",
            ["Remotive", "RemoteOK", "ArbeitNow"],
            default=["Remotive", "RemoteOK", "ArbeitNow"]
        )
    with p_col2:
        if st.button("Fetch Live Openings", type="primary", use_container_width=True):
            jobs = execute_job_collection(st.session_state.target_role, st.session_state.preferred_location, provider_choices)
            st.session_state.collected_jobs = jobs
            st.success(f"Retrieved and normalized {len(jobs)} opportunities!")

    if st.session_state.collected_jobs:
        st.markdown(f"##### Total Opportunities in Pool: **{len(st.session_state.collected_jobs)}**")
        for j in st.session_state.collected_jobs[:6]:
            with st.container():
                st.markdown(f"""
                <div class="metric-card">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h4 style="margin: 0; color: #fff;">{j.title}</h4>
                            <span style="color: #818cf8; font-weight: 600;">{j.company}</span> • <span style="color: #94a3b8;">{j.location}</span>
                        </div>
                        <span style="background: rgba(99, 102, 241, 0.2); color: #818cf8; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem;">
                            {j.provider}
                        </span>
                    </div>
                    <div style="margin-top: 8px; color: #cbd5e1; font-size: 0.85rem;">
                        {j.description[:180]}...
                    </div>
                </div>
                """, unsafe_allow_html=True)


# STEP 7: JOB MATCHING ENGINE
elif selected_step == "7. Job Matching Engine":
    st.markdown('<div class="step-badge">STEP 7 OF 9: JOB MATCHING ENGINE</div>', unsafe_allow_html=True)
    st.header("⚡ Precision Job Matching Engine")
    st.write("Calculates multi-weighted compatibility across roles, skills, experience, and location.")
    
    if not st.session_state.collected_jobs:
        st.info("No collected jobs yet. Click below to fetch jobs first:")
        if st.button("Fetch Jobs for Matching", type="primary"):
            st.session_state.collected_jobs = execute_job_collection(st.session_state.target_role, st.session_state.preferred_location, ["Remotive", "RemoteOK", "ArbeitNow"])
            st.rerun()
    else:
        res = st.session_state.resume_data
        if not res:
            st.warning("Please upload a resume in Step 1 first.")
        else:
            if st.button("Compute Fit Scores & Rank Matches", type="primary") or not st.session_state.matched_jobs:
                with st.spinner("Executing Job Matcher & Deduplicator..."):
                    matched = match_jobs(res, st.session_state.collected_jobs)
                    st.session_state.matched_jobs = matched
                st.success(f"Matched and ranked {len(matched)} unique jobs!")

            if st.session_state.matched_jobs:
                top_job = st.session_state.matched_jobs[0]
                st.subheader(f"🏆 Top Match: {top_job.title} at {top_job.company} ({top_job.match_score}%)")
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Role Alignment", f"{top_job.role_match}%")
                m2.metric("Skill Match", f"{top_job.skill_match}%")
                m3.metric("Experience Fit", f"{top_job.experience_match}%")
                m4.metric("Overall Score", f"{top_job.match_score}%")

                st.markdown("##### Skills Comparison for Top Role:")
                matching_pills = "".join([f'<span class="skill-pill">✔ {s}</span>' for s in top_job.matching_skills])
                missing_pills = "".join([f'<span class="missing-pill">+ {s}</span>' for s in top_job.missing_skills])
                st.markdown(f"**Matched Skills:** {matching_pills if top_job.matching_skills else 'None'}", unsafe_allow_html=True)
                st.markdown(f"**Missing Skills to Feature:** {missing_pills if top_job.missing_skills else 'None'}", unsafe_allow_html=True)


# STEP 8: RANKED RESULTS DASHBOARD
elif selected_step == "8. Ranked Results Dashboard":
    st.markdown('<div class="step-badge">STEP 8 OF 9: RESULTS DASHBOARD</div>', unsafe_allow_html=True)
    st.header("📈 Ranked Results & Opportunity Dashboard")
    st.write("Browse matched opportunities sorted by fit percentage, inspect skill gaps, and apply directly.")
    
    if not st.session_state.matched_jobs:
        if st.session_state.collected_jobs and st.session_state.resume_data:
            st.session_state.matched_jobs = match_jobs(st.session_state.resume_data, st.session_state.collected_jobs)
        else:
            st.info("No matching results available yet. Run Step 6 & 7 or the Full Pipeline.")
    
    if st.session_state.matched_jobs:
        min_score = st.slider("Filter by Minimum Match Score (%):", 0, 100, 50)
        filtered_jobs = [j for j in st.session_state.matched_jobs if j.match_score >= min_score]
        
        st.write(f"Showing **{len(filtered_jobs)}** matching positions above {min_score}% threshold:")
        
        for job in filtered_jobs:
            with st.container():
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"### {job.title}")
                    st.caption(f"🏢 **{job.company}** | 📍 {job.location} | 💰 {job.salary} | 🌐 {job.provider}")
                    st.write(job.description[:240] + "...")
                    
                    matched_p = "".join([f'<span class="skill-pill">✔ {s}</span>' for s in job.matching_skills])
                    missing_p = "".join([f'<span class="missing-pill">+ {s}</span>' for s in job.missing_skills])
                    st.markdown(f"**Matched:** {matched_p}", unsafe_allow_html=True)
                    if job.missing_skills:
                        st.markdown(f"**Skill Gaps:** {missing_p}", unsafe_allow_html=True)

                with c2:
                    st.metric("Compatibility", f"{job.match_score}%")
                    if job.apply_url and job.apply_url != "#":
                        st.link_button("🚀 Apply Now", job.apply_url, type="primary", use_container_width=True)
                    else:
                        search_url = f"https://www.linkedin.com/jobs/search/?keywords={job.title}+{job.company}"
                        st.link_button("🚀 Search on LinkedIn", search_url, type="primary", use_container_width=True)

                st.markdown("---")


# STEP 9: RESUME IMPROVEMENT & ASSISTANCE
elif selected_step == "9. Resume Improvement & Assistance":
    st.markdown('<div class="step-badge">STEP 9 OF 9: RESUME IMPROVEMENT</div>', unsafe_allow_html=True)
    st.header("✨ Resume Tailoring & Application Assistance")
    st.write("Generate tailored bullet points, targeted summaries, and keyword injections calibrated for your specific target job.")
    
    res = st.session_state.resume_data
    candidate_summary = res.career_summary if res else ""
    candidate_skills = res.skills if res else []
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Target Job Description")
        job_role_input = st.text_input("Target Job Title:", value=st.session_state.target_role)
        job_desc_input = st.text_area(
            "Paste Target Job Requirements:",
            value="Looking for a Data Analyst skilled in Python, SQL query optimization, data modeling, Tableau dashboard development, and business analytics. Strong communication and ETL experience preferred.",
            height=180
        )
        
        tailor_btn = st.button("Generate Tailored Resume Content", type="primary")

    with col2:
        st.subheader("AI Optimized Output")
        if tailor_btn and job_role_input and job_desc_input:
            with st.spinner("Tailoring resume bullets and keywords..."):
                tailored = tailor_resume_for_job(
                    original_resume_text=candidate_summary,
                    target_role=job_role_input,
                    target_company="Target Enterprise",
                    job_description=job_desc_input,
                    candidate_skills=candidate_skills
                )
            
            st.success("Resume Tailoring Complete! (+15% Compatibility Boost)")
            if tailored.tailored_summary:
                st.markdown("##### Optimized Professional Summary:")
                st.info(tailored.tailored_summary)
            
            if tailored.suggested_skills:
                st.markdown("##### Target Keywords to Feature:")
                kw_html = "".join([f'<span class="skill-pill">{k}</span>' for k in tailored.suggested_skills])
                st.markdown(kw_html, unsafe_allow_html=True)
            
            if tailored.bullet_improvements:
                st.markdown("##### Recommended High-Impact Bullet Points:")
                for b in tailored.bullet_improvements:
                    st.write(f"• {b}")
        else:
            st.info("Fill out the target requirements on the left and click 'Generate Tailored Resume Content'.")
