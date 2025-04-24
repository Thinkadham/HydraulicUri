import streamlit as st
import os
from dotenv import load_dotenv
import hashlib

# Load environment variables
load_dotenv()

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_auth():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    return st.session_state.authenticated

def login():
    """Login form with proper credential validation"""
    st.title("Login")
    
    # Get credentials from environment
    admin_user = os.getenv("ADMIN_USER")
    admin_pass = os.getenv("ADMIN_PASS")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Login"):
            if username == admin_user and password == admin_pass:
                st.session_state.authenticated = True
                st.session_state.username = username  # Store username
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    # For development only - remove in production
    if os.getenv("ENVIRONMENT") == "development":
        st.warning("Development mode active")
        if st.button("Bypass Login (Dev Only)"):
            st.session_state.authenticated = True
            st.session_state.username = "dev_user"
            st.rerun()

def logout():
    """Logout the current user"""
    st.session_state.authenticated = False
    st.session_state.pop("username", None)
    st.info("You have been logged out")
    st.stop()
