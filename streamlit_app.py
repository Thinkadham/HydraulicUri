import streamlit as st
from utils.auth import check_auth, login
import os

# App Configuration
st.set_page_config(
    page_title="Auto Payment System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Force-hide sidebar completely before login
    if not check_auth():
        st.markdown("""
            <style>
                section[data-testid="stSidebar"] {
                    display: none !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Centered login form
        login_container = st.container()
        with login_container:
            cols = st.columns([1, 2, 1])
            with cols[1]:
                login()
        st.stop()
    
    # Clear sidebar completely before rebuilding
    st.sidebar.empty()
    
    # Build fresh sidebar navigation
    with st.sidebar:
        # App title and logo
        st.title("Auto Payment System")
        st.markdown("---")
        
        # Single navigation system (radio buttons with icons)
        nav_options = {
            "Dashboard": "🏠",
            "Create Bill": "🧾", 
            "Contractors": "👷",
            "Works": "🏗️",
            "Reports": "📊",
            "Settings": "⚙️"
        }
        
        selected = st.radio(
            "Menu",
            options=list(nav_options.keys()),
            format_func=lambda x: f"{nav_options[x]} {x}",
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # User info and logout
        if st.session_state.get('username'):
            st.markdown(f"Logged in as: **{st.session_state.username}**")
        if st.button("🚪 Logout"):
            from utils.auth import logout
            logout()
    
    # Page routing - only import when needed
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
    # Clear any residual sidebar elements
    if 'sidebar_cleared' not in st.session_state:
        st.sidebar.empty()
        st.session_state.sidebar_cleared = True
    
    main()
