import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

def check_auth():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def login():
    """Simple login form"""
    st.title("Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Login"):
            if (username == os.getenv("ADMIN_USER") and 
                password == os.getenv("ADMIN_PASS")):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")

def logout():
    """Clear session and refresh"""
    st.session_state.authenticated = False
    st.rerun()
