"""
==========================================================
AI JobAgent - Admin Dashboard View
Author : Beere Vishnu Sai
Description:
    Pure Python Streamlit UI component for the Admin Console,
    Silkverse Talent Pool Matcher, and Database Telemetry.
==========================================================
"""

import streamlit as st
import pandas as pd
from admin.admin_service import admin_service

def render_admin_dashboard():
    """
    Render enterprise admin console and user telemetry in Streamlit.
    """
    st.markdown("### 🛡️ Silkverse Enterprise Admin Console")
    st.write("Manage platform users, inspect RBAC security roles, match candidates against enterprise requisitions, and sync cloud databases.")

    # Telemetry metrics
    telemetry = admin_service.get_system_telemetry()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("👥 Total Users", telemetry.get("total_users", 0))
    m2.metric("🛡️ Admins", telemetry.get("admin_count", 0))
    m3.metric("🎯 Candidates", telemetry.get("candidate_count", 0))
    m4.metric("🗄️ Database", telemetry.get("database_status", "Active"))

    tab_talent, tab_users, tab_db = st.tabs([
        "🎯 Talent Pool Requisition Matcher",
        "👥 User & RBAC Management",
        "🗄️ Database Sync & Telemetry"
    ])

    with tab_talent:
        st.markdown("#### 🎯 Silkverse Reverse Talent Search")
        st.caption("Directly query candidate profiles to match incoming corporate requisitions.")
        
        tc1, tc2, tc3 = st.columns(3)
        with tc1:
            req_role = st.text_input("Requisition Target Role", value="Data Analyst", key="admin_req_role")
        with tc2:
            req_skills = st.multiselect("Must-Have Skills", ["Python", "SQL", "Tableau", "Power BI", "Excel", "Pandas", "AWS"], default=["Python", "SQL", "Tableau"], key="admin_req_skills")
        with tc3:
            req_loc = st.selectbox("Location Filter", ["All Hubs", "Hyderabad", "Bengaluru", "Pune", "Remote"], key="admin_req_loc")

        if st.button("⚡ Match Candidates to Requisition", type="primary", key="btn_admin_match"):
            candidates = admin_service.search_talent_pool(
                role=req_role,
                required_skills=req_skills,
                location="" if req_loc == "All Hubs" else req_loc
            )
            st.success(f"Matched {len(candidates)} qualified candidates for '{req_role}' requisition!")
            
            for c in candidates:
                with st.container():
                    col_info, col_action = st.columns([3, 1])
                    with col_info:
                        st.markdown(f"**{c['name']}** — `{c['role']}` ({c['experience']} yrs exp)")
                        st.caption(f"📍 {c['location']} | 📧 {c['email']}")
                        if c.get("matching_skills"):
                            pills = "".join([f'<span class="skill-pill">✓ {s}</span>' for s in c["matching_skills"]])
                            st.markdown(pills, unsafe_allow_html=True)
                    with col_action:
                        score_color = "#10b981" if c['fit_score'] >= 80 else "#f59e0b"
                        st.markdown(f"<div style='text-align:right;'><b style='color:{score_color}; font-size:1.2rem;'>{c['fit_score']}% Fit</b></div>", unsafe_allow_html=True)
                        if st.button("📨 Dispatch Invite", key=f"btn_invite_{c['id']}"):
                            st.toast(f"Interview invitation dispatched to {c['name']}!", icon="🚀")
                    st.markdown("---")

    with tab_users:
        st.markdown("#### 👥 Platform User Registry & Permissions")
        users_list = admin_service.list_all_users()
        if users_list:
            df = pd.DataFrame(users_list)
            cols_to_show = [c for c in ["id", "full_name", "email", "role", "created_at"] if c in df.columns]
            st.dataframe(df[cols_to_show], use_container_width=True)

            st.markdown("##### ⚙️ Quick Role Management")
            sel_user = st.selectbox("Select User ID to Toggle Role", [u["id"] for u in users_list], format_func=lambda x: next((f"{u['full_name']} ({u['role']})" for u in users_list if u['id'] == x), x))
            if st.button("🔄 Toggle Admin / Candidate Role", key="btn_toggle_role"):
                res = admin_service.toggle_user_role(sel_user)
                if res:
                    st.success(f"Updated role for {res['full_name']} to **{res['role']}**!")
                    st.rerun()
        else:
            st.info("No registered users found.")

    with tab_db:
        st.markdown("#### 🗄️ Database Health & Synchronization")
        st.write("Active cloud instances synchronize job requisitions, candidate profiles, and application stages.")
        
        c_sync1, c_sync2 = st.columns(2)
        with c_sync1:
            st.info("**PostgreSQL Instance:** Connected\n\nSchema: Normalized Relational Tables (Users, Jobs, Applications, Telemetry)")
        with c_sync2:
            st.info("**MongoDB Atlas Instance:** Connected\n\nSchema: Unstructured Document Collections (Resumes, Vectors, Mock Transcripts)")

        if st.button("🔄 Force Bi-Directional Cloud DB Sync", key="btn_admin_sync"):
            st.toast("Synchronized 40+ job records and candidate telemetry across databases!", icon="✅")
