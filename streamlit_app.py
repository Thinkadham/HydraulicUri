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
    """Load logo with dark/light variants"""
    logo_paths = [
        "assets/logo-dark.png",  # Dark version first
        "assets/logo.png",
        "images/logo-dark.png",
        "images/logo.png",
        "logo-dark.png",
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
        # Hide sidebar during login with dark background
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
    
    # Build sidebar (only once)
    if not st.session_state.nav_initialized:
        with st.sidebar:
            st.sidebar.empty()  # Clear any existing content
            
            # Logo and title - dark theme compatible
            logo = load_logo()
            if logo:
                st.image(logo, width=200)
            else:
                st.title("Auto Payment System")
            
            st.markdown("---")
            
            # Navigation with dark theme styling
            st.session_state.current_page = st.radio(
                "Menu",
                ["Dashboard", "Create Bill", "Contractors", "Works", "Reports", "Settings"],
                key="main_navigation",
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # User info with dark theme text
            if st.session_state.get('username'):
                st.markdown(f"<span style='color:#f0f2f6'>**Logged in as:** {st.session_state.username}</span>", 
                           unsafe_allow_html=True)
            
            # Logout button with dark theme styling
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
                    [data-testid="stSidebar"] button:hover {
                        background: #ff3333 !important;
                        border: 1px solid #444;
                    }
                    hr {
                        border-color: #333 !important;
                    }
                </style>
            """, unsafe_allow_html=True)
            
        st.session_state.nav_initialized = True
    
    # Dark theme main content area
    st.markdown("""
        <style>
            .stApp {
                background-color: #0e1117;
            }
            .stMarkdown, .stText, .stNumberInput label, 
            .stTextInput label, .stSelectbox label, 
            .stDateInput label, .stTimeInput label {
                color: #f0f2f6 !important;
            }
            .stDataFrame, .stTable {
                background-color: #1a1a1a !important;
                color: #f0f2f6 !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Page routing (same as before)
    if st.session_state.current_page == "Dashboard":
        from pages.dashboard import show_dashboard
        show_dashboard()
    # ... (rest of your routing)

if __name__ == "__main__":
    main()
