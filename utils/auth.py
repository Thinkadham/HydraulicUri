# utils/auth.py
import streamlit as st
import os
from dotenv import load_dotenv
import hashlib
from PIL import Image

load_dotenv()

def check_auth():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    return st.session_state.authenticated

def load_image_safe(path, width=None):
    """Safely load an image with fallback handling"""
    try:
        if os.path.exists(path):
            img = Image.open(path)
            if width:
                return img.resize((width, int(width * img.height / img.width)))
            return img
        return None
    except Exception:
        return None

def login():
    st.title("🔐 Login")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Try multiple possible image paths
        login_image = None
        image_paths = [
            "assets/login_illustration.png",
            "images/login_illustration.png",
            "login_illustration.png"
        ]
        
        for path in image_paths:
            login_image = load_image_safe(path, width=200)
            if login_image:
                break
        
        if login_image:
            st.image(login_image)
        else:
            # Fallback icon if image not found
            st.markdown("""
                <div style="text-align: center; font-size: 100px;">
                    🔐
                </div>
            """, unsafe_allow_html=True)
    
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
    st.stop()
