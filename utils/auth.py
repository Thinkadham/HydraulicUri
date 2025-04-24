import streamlit as st
import os
from dotenv import load_dotenv
import hashlib
import hmac

# Load environment variables
load_dotenv()

def initialize_auth_session():
    """Initialize session state variables for authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0

def secure_password_compare(input_password, stored_hash):
    """Securely compare passwords using HMAC to prevent timing attacks"""
    salt = os.getenv("PASSWORD_SALT", "default-salt-value").encode()
    input_hash = hashlib.pbkdf2_hmac(
        'sha256',
        input_password.encode(),
        salt,
        100000
    ).hex()
    return hmac.compare_digest(input_hash, stored_hash)

def check_auth():
    """Check if user is authenticated"""
    initialize_auth_session()
    return st.session_state.authenticated

def login():
    """Login form with security features"""
    st.title("🔐 System Login")
    st.markdown("---")
    
    with st.form("login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.form_submit_button("Login"):
            # Get credentials from environment
            admin_user = os.getenv("ADMIN_USER")
            admin_pass_hash = os.getenv("ADMIN_PASS_HASH")  # Should be pre-hashed
            
            # Security checks
            if st.session_state.login_attempts >= 3:
                st.error("Too many attempts. Please try again later.")
                return
            
            if (username == admin_user and 
                secure_password_compare(password, admin_pass_hash)):
                # Successful login
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.login_attempts = 0
                st.rerun()
            else:
                # Failed attempt
                st.session_state.login_attempts += 1
                st.error("Invalid credentials")
                if st.session_state.login_attempts >= 2:
                    st.warning(f"Remaining attempts: {3 - st.session_state.login_attempts}")
    
    st.markdown("---")
    st.caption("For security reasons, please log out after each session")

def logout():
    """Complete session cleanup"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.login_attempts = 0
    
    # Clear other sensitive session data
    sensitive_keys = [k for k in st.session_state.keys() 
                    if not k.startswith('_') and k not in ['login_attempts']]
    for key in sensitive_keys:
        del st.session_state[key]
    
    st.rerun()

def require_auth(func):
    """Decorator to protect routes"""
    def wrapper(*args, **kwargs):
        if not check_auth():
            st.warning("Please login to access this page")
            login()
            st.stop()
        return func(*args, **kwargs)
    return wrapper
