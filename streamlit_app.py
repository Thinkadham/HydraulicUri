import streamlit as st
from utils.auth import check_auth, login
import os

# MUST be first command
st.set_page_config(
    page_title="Auto Payment System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Initialize session if not exists
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Show login if not authenticated
    if not st.session_state.authenticated:
        st.markdown("""
            <style>
                section[data-testid="stSidebar"] {
                    display: none !important;
                }
            </style>
        """, unsafe_allow_html=True)
        login()
        st.stop()
    
    # Build sidebar only after login
    with st.sidebar:
        st.title("Auto Payment System")
        st.markdown("---")
        
        selected = st.radio(
            "Menu",
            ["Dashboard", "Create Bill", "Contractors", "Works", "Reports", "Settings"],
            key="main_nav"
        )
        
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()
    
    # Page routing
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
    main()
