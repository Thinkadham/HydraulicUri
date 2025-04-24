import streamlit as st
from utils.auth import check_auth, login
import os

# App Configuration - NO SIDEBAR
st.set_page_config(
    page_title="Auto Payment System",
    page_icon="💰",
    layout="centered",  # Changed from "wide" to minimize space
    initial_sidebar_state="collapsed"  # Force sidebar closed
)

def main():
    # Force-hide the sidebar completely before login
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

    if not check_auth():
        login()
        st.stop()  # Stop execution here until logged in
    
    # Only show sidebar AFTER login
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] {
                display: block !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Now build the sidebar
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
