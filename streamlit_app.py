import streamlit as st
from auth import check_auth, login
from pages import dashboard, create_bill, contractors, works, reports, settings

def main():
    st.title("Auto Payment System")
    st.caption("Version 2.0.1 | Designed & Developed by Mohammad Adham Wani")
    
    if not check_auth():
        login()
        return
    
    menu = st.sidebar.selectbox("Navigation", 
        ["Dashboard", "Create New Bill", "Contractor Management", 
         "Works Management", "Reports", "Settings"])
    
    if menu == "Dashboard":
        dashboard.show()
    elif menu == "Create New Bill":
        create_bill.show()
    elif menu == "Contractor Management":
        contractors.show()
    elif menu == "Works Management":
        works.show()
    elif menu == "Reports":
        reports.show()
    elif menu == "Settings":
        settings.show()

if __name__ == "__main__":
    main()
