import streamlit as st
import os
import hashlib # For password hashing
from .db import get_user_by_username # Import the database function

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
            if not username or not password:
                st.warning("Please enter both username and password.")
            else:
                try:
                    user_data = get_user_by_username(username)

                    if user_data:
                        # User found, verify password
                        stored_hash = user_data[0]['hashed_password']
                        provided_hash = hashlib.sha256(password.encode()).hexdigest()

                        if provided_hash == stored_hash:
                            # Passwords match - Authenticate
                            st.session_state.authenticated = True
                            st.session_state.username = user_data[0]['username']
                            st.session_state.user_role = user_data[0]['role'] # Store the role
                            # Store allowed pages if the user is restricted
                            if user_data[0]['role'] == 'restricted':
                                st.session_state.allowed_pages = user_data[0].get('allowed_pages', ['Dashboard']) # Default to Dashboard if null/missing
                            else:
                                # Admins have access to all pages, don't need specific list
                                if 'allowed_pages' in st.session_state:
                                    del st.session_state.allowed_pages # Remove if switching from restricted to admin

                            st.success("Login successful!") # Optional success message
                            st.rerun()
                        else:
                            # Password incorrect
                            st.error("Invalid username or password.")
                    else:
                        # User not found
                        st.error("Invalid username or password.")
                except Exception as e:
                    st.error(f"An error occurred during login: {e}")


    st.markdown("---")

def logout():
    """Secure logout with full session clear"""
    st.session_state.clear()  # Complete reset
    st.session_state.authenticated = False  # Reinitialize needed state
    st.rerun()
