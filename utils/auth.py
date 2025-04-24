import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

def check_auth():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    return st.session_state.authenticated

def login():
    """Login form that takes full page"""
    st.title("🔒 System Login")
    st.markdown("---")
    
    with st.form("login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.form_submit_button("Login"):
            if (username == os.getenv("ADMIN_USER") and 
                password == os.getenv("ADMIN_PASS")):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")
        st.markdown("---")

def logout():
    """Complete session cleanup"""
    st.session_state.authenticated = False
    for key in list(st.session_state.keys()):
        if key not in ['_pages', '_script_run_count']:
            del st.session_state[key]
    st.rerun()
