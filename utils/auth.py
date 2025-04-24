# utils/auth.py
import streamlit as st
import os
from dotenv import load_dotenv
import hashlib

load_dotenv()

def check_auth():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    return st.session_state.authenticated

def login():
    st.title("🔐 Login")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("assets/login_illustration.png", width=200)  # Optional login image
    
    with col2:
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

def logout():
    st.session_state.authenticated = False
    st.session_state.pop("username", None)
    st.success("You have been logged out")
    st.stop()  # This forces a full page refresh
