import streamlit as st
from utils.auth import check_auth, login
import os

# Initialize session state for sidebar control
if 'sidebar_initialized' not in st.session_state:
    st.session_state.sidebar_initialized = False

# App Configuration
st.set_page_config(
    page_title="Auto Payment System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def show_login_page():
    """Handles pre-login state with completely hidden sidebar"""
    # Hide sidebar completely using CSS
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Show centered login form
    login_container = st.container()
    with login_container:
        cols = st.columns([1, 2, 1])
        with cols[1]:
            login()
    st.stop()

def build_sidebar_navigation():
    """Builds the single, clean navigation system"""
    st.sidebar.empty()  # Completely clear the sidebar
    
    with st.sidebar:
        # App title
        st.title("Auto Payment System")
        st.markdown("---")
        
        # Navigation options with icons
        nav_options = {
            "Dashboard": "🏠",
            "Create Bill": "🧾", 
            "Contractors": "👷",
            "Works": "🏗️",
            "Reports": "📊",
            "Settings": "⚙️"
        }
        
        # Single navigation control
        selected = st.radio(
            "Menu",
            options=list(nav_options.keys()),
            format_func=lambda x: f"{nav_options[x]} {x}",
            label_visibility="collapsed",
            key="main_navigation"  # Unique key to prevent duplicates
        )
        
        st.markdown("---")
        
        # User info and logout
        if st.session_state.get('username'):
            st.markdown(f"Logged in as: **{st.session_state.username}**")
        if st.button("🚪 Logout", key="logout_button"):
            from utils.auth import logout
            logout()
    
    return selected

def main():
    if not check_auth():
        show_login_page()
    
    # Build the navigation system exactly once
    selected = build_sidebar_navigation()
    
    # Page routing - import only when needed
    if selected == "Dashboard":
        from pages.dashboard import show_dashboard
        show_dashboard()
    elif selected == "Create Bill":
        from pages.create_bill import create_new_bill
        create_new_bill()
    elif selected == "Contractors":
        from pages.contractors import contractor_management
        contractor_management()
    elif selected == "Works":
        from pages.works import works_management
        works_management()
    elif selected == "Reports":
        from pages.reports import show_reports
        show_reports()
    elif selected == "Settings":
        from pages.settings import show_settings
        show_settings()

if __name__ == "__main__":
    # Clear any existing sidebar elements
    st.sidebar.empty()
    main()
