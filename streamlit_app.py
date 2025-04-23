import streamlit as st
from hydraulicuri.auth import check_auth, login
from hydraulicuri.pages import (
    show_dashboard,
    show_create_bill,
    show_contractors,
    show_works,
    show_reports,
    show_settings
)

def main():
    st.title("Auto Payment System")
    st.caption("Version 2.0.1 | Designed & Developed by Mohammad Adham Wani")
    
    if not check_auth():
        login()
        return
    
    menu = st.sidebar.selectbox("Navigation", [
        "Dashboard", 
        "Create New Bill", 
        "Contractor Management", 
        "Works Management", 
        "Reports", 
        "Settings"
    ])
    
    if menu == "Dashboard":
        show_dashboard()
    elif menu == "Create New Bill":
        show_create_bill()
    elif menu == "Contractor Management":
        show_contractors()
    elif menu == "Works Management":
        show_works()
    elif menu == "Reports":
        show_reports()
    elif menu == "Settings":
        show_settings()

if __name__ == "__main__":
    main()
