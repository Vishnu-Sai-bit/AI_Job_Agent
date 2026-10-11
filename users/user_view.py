"""
==========================================================
AI JobAgent - User Authentication & Account View
Author : Beere Vishnu Sai
Description:
    Pure Python Streamlit component for user login, registration,
    and profile settings.
==========================================================
"""

import streamlit as st
from users.user_service import user_service

def render_user_auth_modal():
    """
    Render login/registration dialog in Streamlit.
    """
    if "user_token" not in st.session_state:
        st.session_state.user_token = None
    if "current_user" not in st.session_state:
        st.session_state.current_user = None

    if st.session_state.current_user:
        u = st.session_state.current_user
        st.markdown(f"**Logged in as:** `{u.get('full_name')} ({u.get('email')})`")
        if st.button("🚪 Logout", key="btn_logout", use_container_width=True):
            st.session_state.user_token = None
            st.session_state.current_user = None
            st.rerun()
    else:
        auth_mode = st.radio("Account Access", ["Guest Mode", "Login", "Register"], horizontal=True, key="auth_mode_selector")
        
        if auth_mode == "Guest Mode":
            st.info("You are currently browsing with full candidate features enabled.")
            if st.button("⚡ Continue as Guest", key="btn_guest_login", use_container_width=True):
                guest_data = user_service.create_guest_session()
                st.session_state.user_token = guest_data["access_token"]
                st.session_state.current_user = guest_data["user"]
                st.success("Signed in as Guest!")
                st.rerun()

        elif auth_mode == "Login":
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("🔓 Sign In", type="primary", key="btn_submit_login", use_container_width=True):
                try:
                    res = user_service.login_user(email, password)
                    st.session_state.user_token = res["access_token"]
                    st.session_state.current_user = res["user"]
                    st.success(f"Welcome back, {res['user']['full_name']}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {e}")

        elif auth_mode == "Register":
            name = st.text_input("Full Name", key="reg_name")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_pass")
            if st.button("✨ Create Account", type="primary", key="btn_submit_reg", use_container_width=True):
                try:
                    res = user_service.register_user(email, password, name)
                    st.session_state.user_token = res["access_token"]
                    st.session_state.current_user = res["user"]
                    st.success(f"Account created successfully for {name}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Registration failed: {e}")
