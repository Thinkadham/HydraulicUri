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
    
    # Clear sidebar completely before rebuilding
    st.sidebar.empty()
    
    # Build fresh sidebar
    with st.sidebar:
        # Navigation - Only ONE instance
        selected = st.radio(
            "Menu",
            ["Dashboard", "Create Bill", "Contractors", "Works", "Reports", "Settings"],
            key="unique_nav_key"  # This prevents duplicates
        )
        
        if st.button("Logout"):
            from utils.auth import logout
            logout()
    
    # Simple routing - No auth checks needed in pages
    if selected == "Dashboard":
        from pages.dashboard import show_dashboard
        show_dashboard()
    elif selected == "Create Bill":
        from pages.create_bill import create_new_bill  # Keep your existing function name
        create_new_bill()
    # ... (add other pages with their EXACT function names)

if __name__ == "__main__":
    # Force fresh start
    if 'nav_init' not in st.session_state:
        st.sidebar.empty()
        st.session_state.nav_init = True
    main()
