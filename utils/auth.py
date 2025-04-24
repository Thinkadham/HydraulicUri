import streamlit as st
import os

def check_auth():
    """Check authentication status with fail-safe defaults"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    return st.session_state.authenticated

def login():
    """Login form with Streamlit Cloud secrets support"""
    st.title("🔑 Login")
    st.markdown("---")
    
    with st.form("login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.form_submit_button("Login"):
            # Get credentials from Streamlit secrets or .env
            admin_user = os.environ.get("ADMIN_USER", "admin")  # Fallback for local dev
            admin_pass = os.environ.get("ADMIN_PASS", "admin123")  # Fallback
            
            if username == admin_user and password == admin_pass:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error(f"Invalid credentials. Expected user: '{admin_user}'")
    
    st.markdown("---")

def logout():
    """Secure logout with full session clear"""
    st.session_state.clear()  # Complete reset
    st.session_state.authenticated = False  # Reinitialize needed state
    st.rerun()
