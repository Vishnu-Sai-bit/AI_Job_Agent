"""
==========================================================
AI JobAgent - ATS Analysis View Component
Author : Beere Vishnu Sai
Description:
    Pure Python Streamlit view rendering ATS compliance,
    6-dimension score gauges, projects, certs, and skills.
==========================================================
"""

import streamlit as st
from typing import Dict, Any

def render_ats_view(res: Dict[str, Any]):
    """
    Render ATS score metrics, dimensional breakdown, and resume details.
    """
    st.markdown("### 📊 ATS Optimization & Candidate Profile")

    c1, c2 = st.columns([1, 2])
    with c1:
        score = res.get("ats_score", 79)
        color = "#10b981" if score >= 80 else ("#f59e0b" if score >= 65 else "#ef4444")
        st.markdown(f"""
        <div class="metric-card" style="text-align: center; padding: 2rem;">
            <h4 style="margin: 0; color: #94a3b8;">OVERALL ATS SCORE</h4>
            <div style="font-size: 3.8rem; font-weight: 900; color: {color}; margin: 0.5rem 0;">{score}%</div>
            <span style="background: rgba(16, 185, 129, 0.15); color: {color}; padding: 0.3rem 0.8rem; border-radius: 9999px; font-weight: 700; font-size: 0.85rem;">
                {'Excellent Recruiter Compatibility' if score >= 80 else ('Competitive Profile' if score >= 65 else 'Needs Optimization')}
            </span>
        </div>
        """, unsafe_allow_html=True)

        bd = res.get("ats_breakdown", {})
        st.markdown("**6-Dimension ATS Breakdown:**")
        st.progress(min(1.0, bd.get("contact_score", 10.0) / 10.0), text=f"📇 Contact Details: {bd.get('contact_score', 10.0)}/10")
        st.progress(min(1.0, bd.get("skills_score", 30.0) / 30.0), text=f"🛠️ Technical Skills Depth: {bd.get('skills_score', 30.0)}/30")
        st.progress(min(1.0, bd.get("experience_score", 5.0) / 20.0), text=f"💼 Experience Relevance: {bd.get('experience_score', 5.0)}/20")
        st.progress(min(1.0, bd.get("education_score", 15.0) / 15.0), text=f"🎓 Education Background: {bd.get('education_score', 15.0)}/15")
        st.progress(min(1.0, bd.get("projects_score", 11.0) / 15.0), text=f"🚀 Project Portfolio: {bd.get('projects_score', 11.0)}/15")
        st.progress(min(1.0, bd.get("certifications_score", 8.0) / 10.0), text=f"📜 Certifications & Licenses: {bd.get('certifications_score', 8.0)}/10")

        # Discovered Web Profiles
        st.markdown("**Discovered External Profiles:**")
        btn_cols = st.columns(3)
        if res.get("linkedin"):
            with btn_cols[0]:
                st.link_button("🌐 LinkedIn", res.get("linkedin"), use_container_width=True)
        if res.get("github"):
            with btn_cols[1]:
                st.link_button("🐙 GitHub", res.get("github"), use_container_width=True)
        if res.get("portfolio"):
            with btn_cols[2]:
                st.link_button("💼 Portfolio", res.get("portfolio"), use_container_width=True)

    with c2:
        st.markdown(f"#### 👤 Candidate: **{res.get('candidate_name', 'BEERE VISHNU SAI')}**")
        st.markdown(f"**Target Role:** `{res.get('preferred_role', 'Data Analyst')}` | **Location:** `{res.get('preferred_location', 'Hyderabad')}` | **Experience:** `{res.get('experience_years', 0.5)} yrs`")
        st.markdown(f"**Email:** `{res.get('email', 'beerevishnusai776600@gmail.com')}` | **Phone:** `{res.get('phone', '+91 98765 43210')}`")
        if res.get("career_summary"):
            st.info(f"**Profile Summary:**\n\n{res.get('career_summary')}")

        sub_tab_skills, sub_tab_proj, sub_tab_cert, sub_tab_edu, sub_tab_rec = st.tabs([
            f"🛠️ Skills ({len(res.get('skills', []))})",
            f"🚀 Projects ({len(res.get('projects', []))})",
            f"📜 Certifications ({len(res.get('certifications', []))})",
            f"🎓 Education ({len(res.get('education', []))})",
            "💡 ATS Suggestions"
        ])

        with sub_tab_skills:
            st.caption("Universal multi-tier extracted skills verified from resume content:")
            skills_html = "".join([f'<span class="skill-pill">{s}</span>' for s in res.get("skills", [])])
            st.markdown(skills_html, unsafe_allow_html=True)

        with sub_tab_proj:
            projects = res.get("projects", [])
            if projects:
                for p in projects:
                    p_title = p.get("title") or p.get("name") or "Project"
                    p_tech = p.get("technologies") or ""
                    p_desc = p.get("description") or ""
                    st.markdown(f"**{p_title}**" + (f" — `{p_tech}`" if p_tech else ""))
                    if p_desc:
                        st.caption(p_desc)
                    st.markdown("---")
            else:
                st.info("No explicit project records detected.")

        with sub_tab_cert:
            certs = res.get("certifications", [])
            if certs:
                for c in certs:
                    st.markdown(f"• **{c}**")
            else:
                st.info("No certifications detected.")

        with sub_tab_edu:
            edu_items = res.get("education", [])
            if edu_items:
                for e in edu_items:
                    st.markdown(f"**{e.get('degree', 'Degree')}**")
                    if e.get("details"):
                        st.caption(f"🏛️ {e.get('details')}")
                    st.markdown("---")
            else:
                st.info("No explicit education records detected.")

        with sub_tab_rec:
            st.markdown("##### 🎯 Strengths Identified by ATS")
            for st_item in res.get("strengths", ["Strong technical skill set.", "Good project portfolio.", "Relevant certifications."]):
                st.success(f"✔ {st_item}")
            
            st.markdown("##### ⚠️ Actionable Suggestions to Reach 90%+ ATS Score")
            for sug in res.get("suggestions", ["Add continuous data engineering credentials.", "Target senior impact statements."]):
                st.warning(f"💡 {sug}")
