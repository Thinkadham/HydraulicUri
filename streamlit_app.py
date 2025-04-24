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
    
    # Show only ONE navigation system
    with st.sidebar:
        # Remove any existing sidebar elements
        st.empty()
        
        # Only show this navigation
        st.title("Auto Payment System")
        st.markdown("---")
        
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
    # ... (rest of your routing logic)

if __name__ == "__main__":
    main()
