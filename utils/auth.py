# utils/auth.py
import streamlit as st
import os
from dotenv import load_dotenv
import hashlib
import hmac
import base64
from supabase import create_client
from datetime import datetime, timedelta
import jwt

# Load environment variables
load_dotenv()

# Constants
SESSION_TIMEOUT = timedelta(hours=2)  # Session expires after 2 hours
JWT_SECRET = os.getenv("JWT_SECRET", "your-very-secret-key-here")

@st.cache_resource
def init_supabase_auth():
    """Initialize Supabase auth client"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Supabase URL and Key must be set in .env")
    return create_client(url, key).auth

def hash_password(password: str) -> str:
    """Securely hash password with salt using PBKDF2"""
    salt = os.getenv("PASSWORD_SALT", "default-salt").encode()
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt,
        100000  # Number of iterations
    ).hex()

def generate_jwt_token(username: str) -> str:
    """Generate JWT token for session management"""
    payload = {
        'username': username,
        'exp': datetime.utcnow() + SESSION_TIMEOUT
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_jwt_token(token: str) -> dict:
    """Verify JWT token and return payload if valid"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload if payload['exp'] > datetime.utcnow().timestamp() else None
    except:
        return None

def check_auth() -> bool:
    """Check if user is authenticated with valid session"""
    if 'auth' not in st.session_state:
        st.session_state.auth = init_supabase_auth()
    
    # Check both session state and JWT token
    if 'jwt_token' in st.session_state:
        payload = verify_jwt_token(st.session_state.jwt_token)
        if payload:
            st.session_state.username = payload['username']
            st.session_state.authenticated = True
            return True
    
    # Fallback to Supabase auth check
    try:
        user = st.session_state.auth.get_user()
        if user:
            st.session_state.username = user.user.email if hasattr(user, 'user') else None
            st.session_state.authenticated = True
            return True
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
    
    st.session_state.authenticated = False
    return False

def login() -> None:
    """Login form with multiple auth options"""
    st.title("🔐 Login")
    
    # Initialize Supabase auth if not already done
    if 'auth' not in st.session_state:
        st.session_state.auth = init_supabase_auth()
    
    # Login tabs
    tab1, tab2 = st.tabs(["Email/Password", "Admin Credentials"])
    
    with tab1:
        # Supabase email/password auth
        with st.form("supabase_login"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login with Email"):
                try:
                    response = st.session_state.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })
                    st.session_state.user = response.user
                    st.session_state.jwt_token = generate_jwt_token(email)
                    st.session_state.authenticated = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {str(e)}")
    
    with tab2:
        # Fallback admin auth (for emergency access)
        admin_user = os.getenv("ADMIN_USER")
        admin_pass = os.getenv("ADMIN_PASS")
        
        with st.form("admin_login"):
            username = st.text_input("Admin Username")
            password = st.text_input("Admin Password", type="password")
            
            if st.form_submit_button("Admin Login"):
                if username == admin_user and hmac.compare_digest(
                    hash_password(password),
                    hash_password(admin_pass)
                ):
                    st.session_state.username = username
                    st.session_state.jwt_token = generate_jwt_token(username)
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid admin credentials")

def logout() -> None:
    """Logout the current user and clear session"""
    try:
        if 'auth' in st.session_state:
            st.session_state.auth.sign_out()
    except Exception as e:
        st.error(f"Logout error: {str(e)}")
    
    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    st.success("You have been logged out successfully!")
    st.stop()  # Stop execution to force page reload

def require_auth(func):
    """Decorator to protect routes"""
    def wrapper(*args, **kwargs):
        if not check_auth():
            st.warning("Please login to access this page")
            login()
            st.stop()
        return func(*args, **kwargs)
    return wrapper
