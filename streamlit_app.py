import streamlit as st
from utils.auth import check_auth, login
import os
from PIL import Image

# Must be first command
st.set_page_config(
    page_title="Auto Payment System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_logo():
    """Load logo with multiple fallback paths"""
    logo_paths = [
        "assets/logo.png",
        "images/logo.png",
        "logo.png"
    ]
    for path in logo_paths:
        if os.path.exists(path):
            try:
                return Image.open(path)
            except:
                continue
    return None

def main():
    # Initialize session state
    if 'nav_initialized' not in st.session_state:
        st.session_state.nav_initialized = False
    
    # Authentication check
    if not check_auth():
        # Hide sidebar during login
        st.markdown("""
            <style>
                section[data-testid="stSidebar"] {
                    display: none !important;
                }
            </style>
        """, unsafe_allow_html=True)
        login()
        st.stop()
    
    # Build sidebar (only once)
    if not st.session_state.nav_initialized:
        with st.sidebar:
            st.sidebar.empty()  # Clear any existing content
            
            # Logo and title
            logo = load_logo()
            if logo:
                st.image(logo, width=200)
            else:
                st.title("Auto Payment System")
            
            st.markdown("---")
            
            # Navigation - with persistent state
            st.session_state.current_page = st.radio(
                "Menu",
                ["Dashboard", "Create Bill", "Contractors", "Works", "Reports", "Settings"],
                key="main_navigation",
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # User info and logout
            if st.session_state.get('username'):
                st.markdown(f"**Logged in as:** {st.session_state.username}")
            if st.button("🚪 Logout", key="logout_btn"):
                from utils.auth import logout
                logout()
            
            # Custom styling
            st.markdown("""
                <style>
                    [data-testid="stSidebar"] {
                        background: linear-gradient(180deg, #4a6bff 0%, #2541b2 100%) !important;
                    }
                    .stRadio [role="radiogroup"] {
                        gap: 0.5rem;
                    }
                    .stRadio [data-testid="stMarkdownContainer"] {
                        color: white !important;
                        padding: 0.5rem;
                        border-radius: 0.5rem;
                    }
                    .stRadio [data-testid="stMarkdownContainer"]:hover {
                        background: rgba(255,255,255,0.1);
                    }
                    [data-testid="stSidebar"] button {
                        background: #ff4b4b;
                        color: white;
                    }
                </style>
            """, unsafe_allow_html=True)
            
        st.session_state.nav_initialized = True
    
    # Page routing
    if st.session_state.current_page == "Dashboard":
        from pages.dashboard import show_dashboard
        show_dashboard()
    elif st.session_state.current_page == "Create Bill":
        from pages.create_bill import create_new_bill
        create_new_bill()
    elif st.session_state.current_page == "Contractors":
        from pages.contractors import contractor_management
        contractor_management()
    elif st.session_state.current_page == "Works":
        from pages.works import works_management
        works_management()
    elif st.session_state.current_page == "Reports":
        from pages.reports import show_reports
        show_reports()
    elif st.session_state.current_page == "Settings":
        from pages.settings import show_settings
        show_settings()

if __name__ == "__main__":
    main()
