import streamlit as st
from utils.auth import check_auth, login
import os
from PIL import Image
import hashlib


# Must be first command
st.set_page_config(
    page_title="Auto Payment System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

if st.secrets.get("DEV_MODE", False):  # development mode
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state.clear()

def get_form_key(page_name, form_name):
    """Generate unique form keys to prevent collisions"""
    base_key = f"{page_name}_{form_name}"
    return hashlib.md5(base_key.encode()).hexdigest()[:10]

def load_logo():
    """Load logo with dark theme support"""
    try:
        return Image.open("assets/logo-dark.png")  # Dark theme version
    except:
        try:
            return Image.open("assets/logo.png")  # Fallback to regular logo
        except:
            return None

def main():
    # Initialize critical session variables
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"
    
    # Authentication check
    if not st.session_state.authenticated:
        # Hide sidebar during login
        st.markdown("""
            <style>
                section[data-testid="stSidebar"] {
                    display: none !important;
                }
                .stApp {
                    background-color: #0e1117;
                }
            </style>
        """, unsafe_allow_html=True)
        login()
        st.stop()
    
    # Build sidebar navigation
    with st.sidebar:
        # Clear previous content safely
        st.empty()
        
        # Logo and title
        logo = load_logo()
        if logo:
            st.image(logo, width=200)
        else:
            st.title("Auto Payment System")
        
        st.markdown("---")
        
        # Navigation menu - using session state to preserve selection
        page_options = ["Dashboard", "Create Bill", "Contractors", "Works", "Reports", "Settings"]
        selected = st.radio(
            "Menu",
            options=page_options,
            index=page_options.index(st.session_state.current_page),
            key="main_nav",
            label_visibility="collapsed"
        )
        
        # Update current page in session state
        if selected != st.session_state.current_page:
            st.session_state.current_page = selected
            st.rerun()
        
        st.markdown("---")
        
        # User info and logout
        if st.session_state.get('username'):
            st.markdown(f"**Logged in as:** {st.session_state.username}")
        if st.button("🚪 Logout", key="logout_btn"):
            from utils.auth import logout
            logout()
        
        # Dark theme sidebar styling
        st.markdown("""
            <style>
                [data-testid="stSidebar"] {
                    background-color: #1a1a1a !important;
                    border-right: 1px solid #333;
                }
                .stRadio [role="radiogroup"] {
                    gap: 0.5rem;
                }
                .stRadio [data-testid="stMarkdownContainer"] {
                    color: #f0f2f6 !important;
                    padding: 0.5rem;
                    border-radius: 0.5rem;
                }
                .stRadio [data-testid="stMarkdownContainer"]:hover {
                    background: rgba(255,255,255,0.1);
                }
                [data-testid="stSidebar"] button {
                    background: #ff4b4b;
                    color: white;
                    border: 1px solid #333;
                }
                hr {
                    border-color: #333 !important;
                }
            </style>
        """, unsafe_allow_html=True)
    
    # Dark theme main content styling
    st.markdown("""
        <style>
            .stApp {
                background-color: #0e1117;
            }
            h1, h2, h3, h4, h5, h6, p, div, span {
                color: #f0f2f6 !important;
            }
            .stDataFrame, .stTable {
                background-color: #1a1a1a !important;
                color: #f0f2f6 !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Page routing - using session state
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
    # Clear any residual session state issues
    if 'init' not in st.session_state:
        st.session_state.clear()
        st.session_state.init = True
    main()
