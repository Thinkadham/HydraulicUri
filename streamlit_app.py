import streamlit as st

# 1. MUST BE FIRST - Page configuration
st.set_page_config(
    page_title="Auto Payment System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Now safe to import other modules
from utils.auth import check_auth, login
import os

# 3. Remove default Streamlit elements
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
    </style>
""", unsafe_allow_html=True)

def show_login_page():
    """Handles pre-login state with hidden sidebar"""
    # Hide sidebar completely
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Centered login form
    with st.container():
        cols = st.columns([1, 2, 1])
        with cols[1]:
            login()
    st.stop()

def build_sidebar():
    """Builds custom styled sidebar navigation"""
    with st.sidebar:
        # Clear previous content
        st.empty()
        
        # Apply custom styling
        st.markdown("""
            <style>
                [data-testid="stSidebar"] {
                    background: linear-gradient(180deg, #4a6bff 0%, #2541b2 100%);
                    color: white;
                    padding: 1rem;
                }
                [data-testid="stSidebar"] .stRadio div {
                    color: white;
                    padding: 0.5rem;
                }
                [data-testid="stSidebar"] .stRadio label {
                    color: white;
                    margin-bottom: 0.5rem;
                }
                [data-testid="stSidebar"] button {
                    background-color: #ff4b4b;
                    color: white;
                    border: none;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Navigation elements
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
            label_visibility="collapsed",
            key="main_nav"  # Prevents duplicates
        )
        
        st.markdown("---")
        if st.session_state.get('username'):
            st.markdown(f"Logged in as: **{st.session_state.username}**")
        if st.button("🚪 Logout"):
            from utils.auth import logout
            logout()
    
    return selected

def main():
    # Authentication check
    if not check_auth():
        show_login_page()
    
    # Build navigation
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
    # Initialize session state
    if 'sidebar_initialized' not in st.session_state:
        st.session_state.sidebar_initialized = True
        st.sidebar.empty()  # Clear any residual content
    
    main()
