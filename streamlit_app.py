import streamlit as st
from utils.auth import check_auth, login
import os

# MUST be the VERY FIRST command
st.set_page_config(
    page_title="Auto Payment System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Initialize critical session variables
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'sidebar_built' not in st.session_state:
        st.session_state.sidebar_built = False
    
    # Authentication check
    if not st.session_state.authenticated:
        # Force-hide sidebar during login
        st.markdown("""
            <style>
                section[data-testid="stSidebar"] {
                    display: none !important;
                }
            </style>
        """, unsafe_allow_html=True)
        login()
        st.stop()
    
    # Build sidebar ONCE
    if not st.session_state.sidebar_built:
        st.sidebar.empty()  # Completely clear sidebar
        with st.sidebar:
            st.title("Auto Payment System")
            st.session_state.selected = st.radio(
                "Menu",
                ["Dashboard", "Create Bill", "Contractors", "Works", "Reports", "Settings"],
                key="permanent_navigation"
            )
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.sidebar_built = False
                st.rerun()
        st.session_state.sidebar_built = True
    
    # Page routing
    if st.session_state.selected == "Dashboard":
        from pages.dashboard import show_dashboard
        show_dashboard()
    elif st.session_state.selected == "Create Bill":
        from pages.create_bill import create_new_bill
        create_new_bill()
    # ... (add other pages)

if __name__ == "__main__":
    main()
