import streamlit as st
from utils.auth import check_auth, login
import os

# MUST be the absolute first command
st.set_page_config(
    page_title="Auto Payment System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide default Streamlit elements
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
    </style>
""", unsafe_allow_html=True)

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
    
    # COMPLETELY remove previous sidebar content
    st.sidebar.empty()
    
    # Build fresh navigation - ONLY ONCE
    with st.sidebar:
        # Navigation with UNIQUE KEY
        selected = st.radio(
            "Menu",
            options=["Dashboard", "Create Bill", "Contractors", "Works", "Reports", "Settings"],
            key="THE_ONE_AND_ONLY_NAVIGATION",  # Critical unique key
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        if st.button("🚪 Logout", key="unique_logout_button"):
            from utils.auth import logout
            logout()
    
    # Route to pages - using YOUR existing function names
    if selected == "Dashboard":
        from pages.dashboard import show_dashboard
        show_dashboard()
    elif selected == "Create Bill":
        from pages.create_bill import create_new_bill  # Keep your exact function name
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
    # Nuclear option - ensures clean start
    st.session_state.clear()
    st.sidebar.empty()
    main()
