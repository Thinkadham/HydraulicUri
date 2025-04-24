import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_auth():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    return st.session_state.authenticated

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # In a real app, verify credentials against Supabase auth
        if username == os.getenv("ADMIN_USER") and password == os.getenv("ADMIN_PASS"):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid credentials")
