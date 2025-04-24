import streamlit as st
import os

# Must be first command
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

# Authentication functions
def check_auth():
    """Check session state for authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    return st.session_state.authenticated

def login():
    """Login form"""
    st.title("🔑 Login")
    st.markdown("---")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Login"):
            if (username == os.getenv("ADMIN_USER") and 
                password == os.getenv("ADMIN_PASS")):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    st.markdown("---")

def logout():
    """Clear session"""
    st.session_state.authenticated = False
    st.session_state.pop("username", None)
    st.rerun()

def show_login_page():
    """Full-page login experience"""
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)
    login()
    st.stop()

def build_sidebar():
    """Single navigation system"""
    with st.sidebar:
        st.empty()  # Clear previous content
        
        # Custom styling
        st.markdown("""
            <style>
                [data-testid="stSidebar"] {
                    background: linear-gradient(180deg, #4a6bff 0%, #2541b2 100%);
                }
                [data-testid="stSidebar"] .stRadio div, 
                [data-testid="stSidebar"] .stRadio label {
                    color: white !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        st.title("Auto Payment System")
        st.markdown("---")
        
        # Navigation options
        selected = st.radio(
            "Menu",
            options=["Dashboard", "Create Bill", "Contractors", "Works", "Reports", "Settings"],
            label_visibility="collapsed",
            key="main_nav"  # Unique key prevents duplicates
        )
        
        st.markdown("---")
        if st.session_state.get('username'):
            st.markdown(f"Logged in as: {st.session_state.username}")
        if st.button("🚪 Logout"):
            logout()
    
    return selected

def main():
    if not check_auth():
        show_login_page()
    
    selected = build_sidebar()
    
    # Page routing - no auth checks needed in pages
    if selected == "Dashboard":
        from pages.dashboard import show_dashboard
        show_dashboard()
    elif selected == "Create Bill":
        from pages.create_bill import show_create_bill
        show_create_bill()
    elif selected == "Contractors":
        from pages.contractors import show_contractors
        show_contractors()
    elif selected == "Works":
        from pages.works import show_works
        show_works()
    elif selected == "Reports":
        from pages.reports import show_reports
        show_reports()
    elif selected == "Settings":
        from pages.settings import show_settings
        show_settings()

if __name__ == "__main__":
    # Initialize fresh session state
    if 'init' not in st.session_state:
        st.session_state.init = True
        st.sidebar.empty()
    
    main()
