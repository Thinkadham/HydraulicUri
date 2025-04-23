import streamlit as st
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

# Import local modules
from auth import check_auth, login
from pages import (
    show_dashboard,
    show_create_bill,
    show_contractors,
    show_works,
    show_reports,
    show_settings
)

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="Auto Payment System",
        page_icon="💰",
        layout="wide"
    )
    
    st.title("Auto Payment System")
    st.caption("Version 2.0.1 | Designed & Developed by Mohammad Adham Wani")
    
    # Check authentication
    if not check_auth():
        login()
        return
    
    # Sidebar navigation
    menu = st.sidebar.selectbox("Navigation", [
        "Dashboard", 
        "Create New Bill", 
        "Contractor Management", 
        "Works Management", 
        "Reports", 
        "Settings"
    ])
    
    # Route to the selected page
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
