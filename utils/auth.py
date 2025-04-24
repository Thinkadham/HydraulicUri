import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

def check_auth():
    return st.session_state.get('authenticated', False)

def login():
    st.title("🔐 Login")
    with st.form("auth_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.form_submit_button("Login"):
            if (username == os.getenv("ADMIN_USER") and 
                password == os.getenv("ADMIN_PASS")):
                st.session_state.authenticated = True
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")

def logout():
    st.session_state.clear()
    st.experimental_rerun()
