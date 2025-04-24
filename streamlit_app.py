import streamlit as st
from utils.auth import check_auth, login
import os

# Remove default Streamlit menu and footer
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# App Configuration
st.set_page_config(
    page_title="Auto Payment System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def show_login_page():
    """Handles pre-login state with completely hidden sidebar"""
    # Hide sidebar using CSS
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Show centered login form
    login()
    st.stop()

def build_sidebar():
    """Builds our custom navigation sidebar"""
    with st.sidebar:
        # Clear any existing elements
        st.empty()
        
        # Custom title
        st.title("Auto Payment System")
        st.markdown("---")

        # Add the custom styling HERE (right before building navigation elements)
        custom_sidebar_style = """
            <style>
                [data-testid="stSidebar"] {
                    background: linear-gradient(180deg, #4a6bff 0%, #2541b2 100%);
                    color: white;
                }
                [data-testid="stSidebar"] .stRadio div {
                    color: white;
                }
                [data-testid="stSidebar"] .stRadio label {
                    color: white;
                }
            </style>
        """
        st.markdown(custom_sidebar_style, unsafe_allow_html=True)
        
        # Our custom navigation
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
            label_visibility="collapsed",
            key="unique_nav_key"  # Prevents duplicate rendering
        )
        
        st.markdown("---")
        if st.session_state.get('username'):
            st.markdown(f"Logged in as: **{st.session_state.username}**")
        if st.button("🚪 Logout"):
            from utils.auth import logout
            logout()
    
    return selected

def main():
    if not check_auth():
        show_login_page()
    
    selected = build_sidebar()
    
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
    # Force clear sidebar on startup
    st.sidebar.empty()
    main()
