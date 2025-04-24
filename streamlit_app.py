import streamlit as st
from utils.auth import check_auth, login
import os

# Must be first command
st.set_page_config(
    page_title="Auto Payment System",
    page_icon="💰",
    layout="wide"
)

def main():
    # Authentication check
    if not check_auth():
        login()
        st.stop()
    
    # Custom sidebar - won't conflict with default nav
    with st.sidebar:
        st.title("Auto Payment System")
        selected = st.radio(
            "Menu",
            ["Dashboard", "Create Bill", "Contractors", "Works", "Reports", "Settings"],
            key="main_nav"
        )
        
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
