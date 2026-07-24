import streamlit as st
import requests
import pandas as pd
import json
from pathlib import Path

# ==========================================================
# Page Configuration & Styling
# ==========================================================
st.set_page_config(
    page_title="AI JobAgent - Smart Career Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Design & Visual Polish
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Font & Layout */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    /* Background Page Styling */
    .stApp {
        background-color: #f8fafc;
    }
    @media (prefers-color-scheme: dark) {
        .stApp {
            background-color: #0f172a;
        }
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #0f172a 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        color: #f8fafc !important;
    }
    
    /* Streamlit Tabs Bar Styling */
    div[data-testid="stTabBar"] {
        background: rgba(255, 255, 255, 0.8) !important;
        border-radius: 14px !important;
        padding: 0.35rem !important;
        border: 1px solid rgba(0, 0, 0, 0.06) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
        margin-bottom: 2rem !important;
    }
    @media (prefers-color-scheme: dark) {
        div[data-testid="stTabBar"] {
            background: rgba(30, 41, 59, 0.5) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
        }
    }
    button[data-baseweb="tab"] {
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        color: #64748b !important;
        transition: all 0.3s ease !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.4rem !important;
        border: none !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3) !important;
    }
    
    /* Streamlit Action Buttons Styling */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        font-weight: 700 !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.25) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.4) !important;
        background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%) !important;
    }
    div.stButton > button:first-child:active {
        transform: translateY(0px) !important;
    }
    
    /* Expander Card Styling */
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(8px) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(226, 232, 240, 0.8) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02) !important;
        margin-bottom: 1.2rem !important;
        overflow: hidden !important;
        transition: all 0.3s ease !important;
    }
    @media (prefers-color-scheme: dark) {
        div[data-testid="stExpander"] {
            background: rgba(30, 41, 59, 0.4) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
        }
    }
    div[data-testid="stExpander"]:hover {
        border-color: rgba(124, 58, 237, 0.4) !important;
        box-shadow: 0 8px 24px rgba(124, 58, 237, 0.08) !important;
    }
    
    /* Gradient Header Background */
    .main-header {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%);
        padding: 2.8rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2.5rem;
        box-shadow: 0 12px 30px rgba(124, 58, 237, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.3s ease;
    }
    .main-header:hover {
        transform: translateY(-2px);
    }
    .main-header h1 {
        font-weight: 800;
        letter-spacing: -0.05em;
        margin: 0;
        font-size: 3.2rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }
    .main-header p {
        font-weight: 500;
        font-size: 1.2rem;
        opacity: 0.95;
        margin-top: 0.6rem;
    }
    
    /* Breathtaking Card Layout with Glowing Border */
    .card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 1.8rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        border: 1px solid rgba(226, 232, 240, 0.8);
        margin-bottom: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    @media (prefers-color-scheme: dark) {
        .card {
            background: rgba(15, 23, 42, 0.7) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
            color: #f1f5f9 !important;
        }
        .card h3 {
            background: linear-gradient(135deg, #a5b4fc 0%, #c084fc 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
        }
        .metric-val {
            color: #818cf8 !important;
            text-shadow: 0 2px 8px rgba(129, 140, 248, 0.15) !important;
        }
        div[data-testid="stTabBar"] {
            background: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
        }
        button[data-baseweb="tab"] {
            color: #94a3b8 !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
            color: white !important;
        }
        div[data-testid="stExpander"] {
            background: rgba(15, 23, 42, 0.5) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            color: #f1f5f9 !important;
        }
        div[data-testid="stExpander"] details summary {
            color: #f1f5f9 !important;
        }
        .badge-skill {
            background: rgba(99, 102, 241, 0.12) !important;
            color: #a5b4fc !important;
            border: 1px solid rgba(99, 102, 241, 0.3) !important;
        }
        .badge-missing {
            background: rgba(239, 68, 68, 0.1) !important;
            color: #fca5a5 !important;
            border: 1px solid rgba(239, 68, 68, 0.3) !important;
        }
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(79, 70, 229, 0.15);
        border-color: rgba(79, 70, 229, 0.4);
    }
    .card h3 {
        font-weight: 700;
        font-size: 1.25rem;
        margin-top: 0;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Metrics display */
    .metric-val {
        font-size: 3.2rem;
        font-weight: 800;
        color: #4f46e5;
        letter-spacing: -0.04em;
        margin: 0.5rem 0;
        text-shadow: 0 2px 8px rgba(79, 70, 229, 0.1);
    }
    
    /* Badges */
    .badge-skill {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%);
        color: #6366f1;
        padding: 0.4rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 0.25rem;
        font-weight: 600;
        border: 1px solid rgba(79, 70, 229, 0.2);
        transition: all 0.2s ease;
        text-decoration: none;
    }
    .badge-skill:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white !important;
        transform: scale(1.05);
    }
    .badge-missing {
        background: rgba(239, 68, 68, 0.08);
        color: #ef4444;
        padding: 0.4rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 0.25rem;
        font-weight: 600;
        border: 1px solid rgba(239, 68, 68, 0.2);
        transition: all 0.2s ease;
        text-decoration: none;
    }
    .badge-missing:hover {
        background: #ef4444;
        color: white !important;
        transform: scale(1.05);
    }
    
    /* Hide Streamlit Default Branding, Menu, and Header */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Optimize main content layout container */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }
</style>
""", unsafe_allow_html=True)

# API Endpoint URL
if "BACKEND_URL" in st.secrets:
    BACKEND_URL = st.secrets["BACKEND_URL"]
else:
    BACKEND_URL = "http://localhost:8000"

def classify_job_role(title: str, description: str) -> str:
    t_lower = title.lower()
    
    # 1. BI / Visualization Analyst
    if any(x in t_lower for x in ["power bi", "powerbi", "tableau", "visualization", "bi analyst", "bi developer", "dashboard"]):
        return "💼 Business Intelligence & Visualization (Power BI / Tableau)"
    # 2. Data Scientist / ML
    elif any(x in t_lower for x in ["data scientist", "science", "machine learning", "ai", "ml"]):
        return "🧠 Data Science & Machine Learning (Python / AI / ML)"
    # 3. Data Engineer / SQL Specialist
    elif any(x in t_lower for x in ["data engineer", "etl", "database", "sql developer", "mysql", "postgresql", "oracle"]):
        return "⚙️ Data Engineering & Database (SQL / ETL / MySQL)"
    # 4. Data Analyst
    elif any(x in t_lower for x in ["data analyst", "analytics", "analyst", "reporting"]):
        return "📊 Data Analyst & Business Analytics"
    
    return "💡 Other IT & Software Engineering Roles"

# Title header
st.markdown('<div class="main-header"><h1>💼 AI JobAgent</h1><p>Smart Resume Parser, ATS Scorer, & AI-Powered Job Matcher</p></div>', unsafe_allow_html=True)

# ==========================================================
# Sidebar Settings & File Upload
# ==========================================================
st.sidebar.header("📁 Upload Resume")
uploaded_file = st.sidebar.file_uploader("Upload your resume (PDF/DOCX)", type=["pdf", "docx"])

# Session state initialization
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "job_results" not in st.session_state:
    st.session_state.job_results = None
if "last_uploaded_filename" not in st.session_state:
    st.session_state.last_uploaded_filename = None

# Analysis Trigger (Auto-triggers on file upload)
if uploaded_file is not None:
    if st.session_state.last_uploaded_filename != uploaded_file.name or st.session_state.analysis_results is None:
        st.session_state.last_uploaded_filename = uploaded_file.name
        with st.spinner("Processing resume & matching jobs by skills..."):
            try:
                # Save & upload file
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                # Fetch ATS analysis & parsing
                analysis_response = requests.post(f"{BACKEND_URL}/analyze-resume", files=files)
                if analysis_response.status_code == 200:
                    st.session_state.analysis_results = analysis_response.json()["resume"]
                else:
                    st.error(f"Analysis failed: {analysis_response.text}")
                
                # Rewind file buffer for the next request
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                # Fetch matching jobs
                job_response = requests.post(f"{BACKEND_URL}/search-jobs", files=files)
                if job_response.status_code == 200:
                    st.session_state.job_results = job_response.json()["result"]
                else:
                    st.error(f"Job search failed: {job_response.text}")
                    
            except Exception as e:
                st.error(f"Error connecting to backend API: {e}")

# ==========================================================
# Main Content Grid
# ==========================================================
if st.session_state.analysis_results is not None:
    res = st.session_state.analysis_results
    
    # Create Tabs for Navigation
    tab_dashboard, tab_jobs, tab_optimizer, tab_learning = st.tabs([
        "📊 Dashboard & ATS Report", 
        "💼 Job Matches", 
        "🧠 AI Resume Optimizer", 
        "📈 Learning Roadmaps"
    ])
    
    # ------------------------------------------------------
    # Tab 1: Dashboard & ATS Report
    # ------------------------------------------------------
    with tab_dashboard:
        col1, col2, col3 = st.columns([1, 1, 1])
        
        # ATS Score Gauge
        with col1:
            score = res.get("ats_score", 0.0)
            st.markdown(f"""
            <div class="card" style="text-align: center;">
                <h3>ATS Score</h3>
                <div class="metric-val">{score} %</div>
                <p style="color: #666;">Match against target role standards</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="card">
                <h3>Personal Info</h3>
                <p><b>Name:</b> {res.get('name', 'N/A')}</p>
                <p><b>Email:</b> {res.get('email', 'N/A')}</p>
                <p><b>Phone:</b> {res.get('phone', 'N/A')}</p>
                <p><b>Hometown:</b> {res.get('location', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class="card">
                <h3>Target Preference</h3>
                <p><b>Preferred Role:</b> {res.get('preferred_role', 'N/A')}</p>
                <p><b>Target Hub:</b> {res.get('preferred_location', 'N/A')}</p>
                <p><b>Experience:</b> {res.get('experience_years', 0.0)} years</p>
                <p><b>Level:</b> {res.get('career_level', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
            
        # Social Profiles Section
        st.subheader("🌐 Professional Portfolios & Contacts")
        cols_social = st.columns(6)
        socials = [
            ("LinkedIn", "linkedin", "🔗"),
            ("GitHub", "github", "💻"),
            ("Portfolio", "portfolio", "💼"),
            ("Kaggle", "kaggle", "📊"),
            ("LeetCode", "leetcode", "🧠"),
            ("HackerRank", "hackerrank", "🏆")
        ]
        for i, (name, key, icon) in enumerate(socials):
            val = res.get(key, "")
            with cols_social[i]:
                if val:
                    # Clean url format
                    url = val if val.startswith("http") else f"https://{val}"
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; text-align: center; border: 1px solid #eef2f6;">
                        <span style="font-size: 1.5rem;">{icon}</span><br>
                        <b>{name}</b><br>
                        <a href="{url}" target="_blank" style="font-size: 0.8rem; text-decoration: none; color: #1a73e8;">View Profile</a>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; text-align: center; border: 1px solid #eef2f6; opacity: 0.5;">
                        <span style="font-size: 1.5rem;">❌</span><br>
                        <b>{name}</b><br>
                        <span style="font-size: 0.8rem; color: #999;">Not Found</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
        # Skills & Gaps
        st.markdown("<br>", unsafe_allow_html=True)
        col_skills, col_gaps = st.columns(2)
        with col_skills:
            st.subheader("✅ Extracted Skills")
            skills_html = "".join([f'<span class="badge-skill">{s}</span>' for s in res.get("skills", [])])
            st.markdown(f'<div class="card">{skills_html if skills_html else "No skills parsed."}</div>', unsafe_allow_html=True)
            
        with col_gaps:
            st.subheader("❌ ATS Missing Skills")
            missing_html = "".join([f'<span class="badge-missing">{s}</span>' for s in res.get("missing_skills", [])])
            st.markdown(f'<div class="card">{missing_html if missing_html else "No missing skills identified!"}</div>', unsafe_allow_html=True)

        # 🎯 Personalized Career Recommendations (Job Suitability Report)
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🎯 Personalized Job Compatibility & Recommendations")
        
        # Programmatic analysis of suitability
        skills_set = {s.lower().strip() for s in res.get("skills", [])}
        certifications = res.get("certifications", [])
        
        # Primary roles
        primary_roles = []
        if any(x in skills_set for x in ["python", "sql", "tableau", "power bi", "excel"]):
            primary_roles.append("Data Analyst / Graduate Data Analyst")
        if any(x in skills_set for x in ["power bi", "tableau", "dax", "power query"]):
            primary_roles.append("Business Intelligence (BI) Analyst / BI Developer")
        if "python" in skills_set and any(x in skills_set for x in ["scikit-learn", "machine learning", "pandas"]):
            primary_roles.append("Junior Data Scientist / Predictive Modeler")
            
        # Secondary roles
        secondary_roles = []
        if "sql" in skills_set or "mysql" in skills_set or "oracle" in skills_set:
            secondary_roles.append("SQL Developer / Database Analyst")
        if any(x in skills_set for x in ["etl", "pipeline", "data cleaning", "mysql"]):
            secondary_roles.append("Junior Data Engineer / ETL Specialist")
            
        # Strengths / Why you fit
        strengths = []
        has_oracle = False
        for cert in certifications:
            cert_name = ""
            if isinstance(cert, dict):
                cert_name = cert.get("name") or ""
            elif isinstance(cert, str):
                cert_name = cert
                
            if "oracle" in cert_name.lower():
                has_oracle = True
                
        if has_oracle:
            strengths.append("Oracle-certified in Cloud & Database Services, demonstrating enterprise-grade readiness.")
        if "power bi" in skills_set or "tableau" in skills_set:
            strengths.append("Strong dashboarding & visualization portfolio across multiple tools (Power BI, Tableau, Excel).")
        if "python" in skills_set and "sql" in skills_set:
            strengths.append("Proficient in key scripting and database querying languages (Python & SQL).")
            
        # Target Industries
        industries = []
        # Check experience and projects text
        exp_text = str(res.get("experience", "")).lower() + " " + str(res.get("projects", "")).lower()
        if "telecom" in exp_text:
            industries.append("Telecom & Network Operators")
        if "ev" in exp_text or "electric vehicle" in exp_text or "charging" in exp_text:
            industries.append("EV (Electric Vehicle) & Clean Energy Analytics")
        if "retail" in exp_text or "sales" in exp_text:
            industries.append("E-Commerce & Retail Operations")
        if "healthcare" in exp_text or "hospital" in exp_text or "patient" in exp_text:
            industries.append("Healthcare & Patient Operations")
            
        if not industries:
            industries = ["IT Consulting & Services", "Product-Based Tech MNCs", "Business Intelligence Hubs"]
            
        # Display the custom advice block
        with st.container():
            st.markdown(f"""
            <div class="card" style="background-color: #f0f7ff; border-left: 5px solid #1a73e8; padding: 1.5rem; border-radius: 8px;">
                <h4 style="color: #1a73e8; margin-top: 0; font-size: 1.2rem;">🌟 Profile Suitability Report</h4>
                <div style="margin-bottom: 1rem;">
                    <b>🏆 Recommended Roles (Best Match):</b>
                    <ul>
                        {"".join([f"<li>{r}</li>" for r in primary_roles]) if primary_roles else "<li>General Data Associate</li>"}
                    </ul>
                </div>
                <div style="margin-bottom: 1rem;">
                    <b>⚙️ Secondary Careers / Fallbacks:</b>
                    <ul>
                        {"".join([f"<li>{r}</li>" for r in secondary_roles]) if secondary_roles else "<li>Technical Support Specialist</li>"}
                    </ul>
                </div>
                <div style="margin-bottom: 1rem;">
                    <b>💡 Your Key Competitive Strengths:</b>
                    <ul>
                        {"".join([f"<li>{s}</li>" for s in strengths]) if strengths else "<li>Solid analytical foundation and project portfolio.</li>"}
                    </ul>
                </div>
                <div>
                    <b>🏭 Recommended Industry Sectors:</b>
                    <ul>
                        {"".join([f"<li>{ind}</li>" for ind in industries])}
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ------------------------------------------------------
    # Tab 2: Job Matches
    # ------------------------------------------------------
    with tab_jobs:
        if st.session_state.job_results is not None:
            jr = st.session_state.job_results
            
            # Show status information
            if "Showing global remote" in jr.get("message", ""):
                st.warning(f"⚠️ {jr.get('message')}")
            else:
                st.success(f"ℹ️ {jr.get('message')}")
                
            # Quick Stats
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Jobs Found", jr.get("total_jobs_found", 0))
            c2.metric("Matched Returned", jr.get("total_jobs_returned", 0))
            c3.metric("Search Time", f"{jr.get('search_time', 0.0)}s")
            c4.metric("Failed API Feeds", len(jr.get("failed_providers", [])))
            
            # Matched Jobs list (grouped by city or role category)
            grouped = jr.get("grouped_jobs", {})
            if not grouped:
                st.info("No matching jobs to display.")
            else:
                st.write("")
                group_by = st.radio("🔍 Group Jobs By:", ["📋 Matched Role Category", "📍 City / Location"], horizontal=True)
                st.write("")
                
                # Flatten the list of all returned jobs to group them dynamically
                all_jobs = []
                for city_group, jobs_list in jr.get("grouped_jobs", {}).items():
                    for j in jobs_list:
                        if j not in all_jobs:
                            all_jobs.append(j)
                            
                if group_by == "📋 Matched Role Category":
                    grouped_display = {}
                    for job in all_jobs:
                        cat = classify_job_role(job.get("title", ""), job.get("description", ""))
                        if cat not in grouped_display:
                            grouped_display[cat] = []
                        grouped_display[cat].append(job)
                    grouped_display = dict(sorted(grouped_display.items()))
                else:
                    grouped_display = {f"📍 {k}": v for k, v in grouped.items()}
                
                for group_name, jobs_list in grouped_display.items():
                    st.markdown(f"#### {group_name} ({len(jobs_list)} jobs)")
                    for idx, job in enumerate(jobs_list):
                        with st.expander(f"⭐ {job.get('title')} at {job.get('company')} — Match: {job.get('match_score')}%"):
                            col_j1, col_j2 = st.columns([2, 1])
                            with col_j1:
                                st.markdown(f"**Location:** {job.get('location')} | **Type:** {job.get('employment_type', 'N/A')} | **Salary:** {job.get('salary', 'Not Mentioned')}")
                                
                                apply_url = (job.get('apply_url') or "").strip()
                                company = job.get('company', 'Company')
                                title = job.get('title', 'Job')
                                
                                search_query = f"{company} {title} careers apply"
                                encoded_query = requests.utils.quote(search_query)
                                google_search_url = f"https://www.google.com/search?q={encoded_query}"
                                
                                if not apply_url:
                                    st.markdown(f"**Apply/Job Link:** [🔍 Search Company Careers & Application Link]({google_search_url})")
                                else:
                                    st.markdown(f"**Apply/Job Link:** [Apply Here]({apply_url}) | [🔍 Search Company Careers]({google_search_url})")
                                    
                                st.write(job.get("description", "No description available.")[:800] + "...")
                            with col_j2:
                                st.markdown("##### Match Breakdown")
                                # Color coding scores
                                score = job.get('match_score', 0)
                                color = "green" if score > 70 else "orange" if score > 45 else "red"
                                st.markdown(f"**Match Rating:** <span style='color:{color};font-weight:bold;font-size:1.2rem;'>{score}%</span>", unsafe_allow_html=True)
                                
                                # Matching / Missing Skills lists
                                m_skills = "".join([f'<span class="badge-skill">{s}</span>' for s in job.get("matching_skills", [])])
                                mis_skills = "".join([f'<span class="badge-missing">{s}</span>' for s in job.get("missing_skills", [])])
                                st.markdown(f"**Matching Skills:**<br>{m_skills if m_skills else 'None'}", unsafe_allow_html=True)
                                st.markdown(f"**Missing Skills:**<br>{mis_skills if mis_skills else 'None'}", unsafe_allow_html=True)
        else:
            st.info("Please search for jobs using the sidebar panel first.")

    # ------------------------------------------------------
    # Tab 3: AI Resume Optimizer
    # ------------------------------------------------------
    with tab_optimizer:
        st.subheader("🧠 Optimize Resume using Local LLM (Ollama)")
        st.write("Rewrites your career summary, updates bullet points with stronger metrics, and recommends missing tools for your target role.")
        
        target_opt_role = st.text_input("Target Role for Optimization", value=res.get("preferred_role", "Data Analyst"))
        
        # Optimization trigger button
        if st.button("✨ Run AI Optimizer", type="primary"):
            with st.spinner("Calling local Ollama instance (Llama 3.2)..."):
                try:
                    # Upload file again to optimizer endpoint
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    opt_res = requests.post(
                        f"{BACKEND_URL}/optimize-resume", 
                        files=files,
                        params={"target_role": target_opt_role}
                    )
                    
                    if opt_res.status_code == 200:
                        opt_data = opt_res.json()["optimization"]
                        
                        st.success("Optimization generated successfully!")
                        
                        col_opt1, col_opt2 = st.columns(2)
                        with col_opt1:
                            st.markdown("#### 📝 Original vs Optimized Summary")
                            st.markdown("**Original:**")
                            st.caption(res.get("career_summary", "No summary available."))
                            st.markdown("**Optimized:**")
                            st.info(opt_data.get("improved_summary", "No optimized summary generated."))
                            
                        with col_opt2:
                            st.markdown("#### ⚡ Suggested Action Verbs")
                            verbs = opt_data.get("action_verbs", [])
                            st.write(", ".join(verbs) if verbs else "No verb suggestions.")
                            
                            st.markdown("#### 📈 Recommended Technical Stack to Add")
                            tech_stack = opt_data.get("recommended_skills", [])
                            tech_html = "".join([f'<span class="badge-skill">{s}</span>' for s in tech_stack])
                            st.markdown(tech_html if tech_html else "No recommendations.", unsafe_allow_html=True)
                            
                        st.divider()
                        st.markdown("#### 📊 Optimized Bullet Points Examples")
                        for pt in opt_data.get("bullet_points_improvements", []):
                            st.markdown(f"**Original:** {pt.get('original')}")
                            st.markdown(f"**Improved:** {pt.get('improved')}")
                            st.caption(f"*Reason:* {pt.get('reason')}")
                            st.markdown("---")
                    else:
                        st.error(f"Optimization endpoint error: {opt_res.text}")
                except Exception as e:
                    st.error(f"Connection failure: {e}")

    # ------------------------------------------------------
    # Tab 4: Learning Roadmaps
    # ------------------------------------------------------
    with tab_learning:
        st.subheader("📈 Auto-Learning skill demand analysis")
        st.write("Analyzes the actual requirements from currently fetched job postings to prioritize which skills you should learn first.")
        
        if st.session_state.job_results is not None:
            jr = st.session_state.job_results
            l_path = jr.get("learning_path", [])
            
            if not l_path:
                st.info("No learning path recommendations generated. Try a wider job query.")
            else:
                # Prepare chart dataframe
                chart_data = pd.DataFrame([
                    {"Skill": item["skill"], "Demand %": item["demand_percentage"], "Mentioned Count": item["frequency"]}
                    for item in l_path
                ])
                
                # Show roadmaps
                col_c1, col_c2 = st.columns([1, 1])
                with col_c1:
                    st.markdown("##### 📊 Skill Demand Breakdown")
                    st.bar_chart(chart_data.set_index("Skill")["Demand %"])
                with col_c2:
                    st.markdown("##### 📍 Personalized Recommendations")
                    for item in l_path:
                        st.markdown(f"""
                        <div class="card" style="padding: 1rem; border-left: 5px solid #1a73e8;">
                            <b>{item['skill']}</b> — Required by <b>{item['demand_percentage']}%</b> of job postings.
                            <br><span style="color: #666; font-size: 0.9rem;">{item['recommendation']}</span>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("Please query job matches in the sidebar to populate demand roadmaps.")

else:
    # Landing details
    st.info("👈 Please upload your Resume PDF or DOCX file in the sidebar panel to begin!")
    
    col_l1, col_l2, col_l3 = st.columns(3)
    col_l1.markdown("""
    ### 📁 Smart Resume Parsing
    Parses complex 2-column or scanned resumes using PyMuPDF and extracts names, emails, phones, and professional portfolio accounts automatically.
    """)
    col_l2.markdown("""
    ### ⚙️ ATS Scorer
    Compares resume details to industry metrics, awarding points for skill counts and technical value, with highlights on missing skills.
    """)
    col_l3.markdown("""
    ### 🎯 Smart Matching
    Aggregates job details from Remotive, RemoteOK, ArbeitNow, and TheMuse, evaluating roles, locations, salaries, and experience weights.
    """)
