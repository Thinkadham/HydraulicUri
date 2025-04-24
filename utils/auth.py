import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_auth():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    return st.session_state.authenticated

def login():
    """Simple login form"""
    st.title("🔑 Login")
    st.markdown("---")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Login"):
            if (username == os.getenv("ADMIN_USER") and 
                password == os.getenv("ADMIN_PASS")):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    st.markdown("---")

def logout():
    """Clear session and refresh"""
    st.session_state.authenticated = False
    st.session_state.pop("username", None)
    st.rerun()
