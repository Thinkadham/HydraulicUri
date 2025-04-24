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
    # Force-hide sidebar before login
    if not check_auth():
        st.markdown("""
            <style>
                section[data-testid="stSidebar"] {
                    display: none !important;
                }
            </style>
        """, unsafe_allow_html=True)
        login()
        st.stop()
    
    # Show styled sidebar after login
    with st.sidebar:
        st.title("Auto Payment System")
        st.markdown("---")
        
        # Proper navigation using radio buttons
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
        if st.button("🚪 Logout"):
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
