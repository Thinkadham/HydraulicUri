import streamlit as st

# MUST be first command
st.set_page_config(
    page_title="Auto Payment System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.auth import check_auth, login
import os

# Remove default Streamlit elements
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
    </style>
""", unsafe_allow_html=True)

def show_login_page():
    """Full-page login with hidden sidebar"""
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Centered login form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        login()
    st.stop()

def build_sidebar():
    """Builds sidebar navigation exactly once"""
    # Clear previous content
    st.sidebar.empty()
    
    with st.sidebar:
        # Apply custom styling
        st.markdown("""
            <style>
                [data-testid="stSidebar"] {
                    background: linear-gradient(180deg, #4a6bff 0%, #2541b2 100%);
                }
                [data-testid="stSidebar"] .stRadio div {
                    color: white !important;
                }
                [data-testid="stSidebar"] .stRadio label {
                    color: white !important;
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
        
        # Single source of truth for navigation
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "Dashboard"
            
        selected = st.radio(
            "Menu",
            options=list(nav_options.keys()),
            format_func=lambda x: f"{nav_options[x]} {x}",
            label_visibility="collapsed",
            key="main_nav_radio",
            index=list(nav_options.keys()).index(st.session_state.current_page)
        )
        
        st.session_state.current_page = selected
        st.markdown("---")
        
        if st.session_state.get('username'):
            st.markdown(f"Logged in as: **{st.session_state.username}**")
            
        if st.button("🚪 Logout", key="unique_logout_button"):
            from utils.auth import logout
            logout()
    
    return selected

def main():
    if not check_auth():
        show_login_page()
    
    selected = build_sidebar()
    
    # Page routing
    page_mapping = {
        "Dashboard": "dashboard",
        "Create Bill": "create_bill",
        "Contractors": "contractors",
        "Works": "works",
        "Reports": "reports",
        "Settings": "settings"
    }
    
    try:
        module = __import__(f"pages.{page_mapping[selected]}", fromlist=[f"show_{page_mapping[selected]}"])
        getattr(module, f"show_{page_mapping[selected]}")()
    except Exception as e:
        st.error(f"Error loading page: {str(e)}")

if __name__ == "__main__":
    # Force fresh sidebar initialization
    if 'sidebar_built' not in st.session_state:
        st.session_state.sidebar_built = False
    
    if not st.session_state.sidebar_built:
        st.sidebar.empty()
        st.session_state.sidebar_built = True
    
    main()
