import streamlit as st
from utils.auth import check_auth, login
from PIL import Image
import os

# App Configuration
st.set_page_config(
    page_title="Auto Payment System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def show_empty_sidebar():
    """Empty sidebar before login"""
    with st.sidebar:
        st.title("Auto Payment System")
        st.markdown("---")
        st.write("Please login to access the system")

def show_main_sidebar():
    """Full sidebar after login"""
    with st.sidebar:
        st.title("Auto Payment System")
        st.markdown("---")
        
        # Navigation menu
        selected = st.radio(
            "Navigation",
            options=["Dashboard", "Create Bill", "Contractors", "Works", "Reports", "Settings"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        if st.button("Logout"):
            from utils.auth import logout
            logout()
        
        return selected

def main():
    if not check_auth():
        show_empty_sidebar()
        login()
    else:
        selected_page = show_main_sidebar()
        
        # Page routing
        if selected_page == "Dashboard":
            from pages.dashboard import show_dashboard
            show_dashboard()
        elif selected_page == "Create Bill":
            from pages.create_bill import create_new_bill
            create_new_bill()
        elif selected_page == "Contractors":
            from pages.contractors import contractor_management
            contractor_management()
        elif selected_page == "Works":
            from pages.works import works_management
            works_management()
        elif selected_page == "Reports":
            from pages.reports import show_reports
            show_reports()
        elif selected_page == "Settings":
            from pages.settings import show_settings
            show_settings()

if __name__ == "__main__":
    main()
