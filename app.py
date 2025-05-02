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

        # Navigation menu - dynamically build based on role
        base_page_options = ["Dashboard", "Create Bill", "Contractors", "Works", "Reports"]
        admin_page_options = ["User Management"] # Pages only admins can see

        page_options = base_page_options
        # Check if user_role exists and is 'admin' before adding admin pages
        if st.session_state.get('user_role') == 'admin':
            # Insert User Management before Settings, for example
            # settings_index = page_options.index("Settings")
            # page_options.insert(settings_index, "User Management")
            page_options.extend(admin_page_options)

        # Ensure current_page is valid if role changes or page is restricted
        if st.session_state.current_page not in page_options:
             st.session_state.current_page = "Dashboard" # Default to Dashboard

        selected = st.radio(
            "Menu",
            options=page_options, # Use dynamically generated options
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

    # --- Page Routing with Role-Based Access Control ---
    current_page = st.session_state.current_page
    user_role = st.session_state.get('user_role', 'restricted') # Default to restricted if role not set
    allowed_pages = st.session_state.get('allowed_pages', []) # Get allowed pages from session state

    # Check access based on role and allowed_pages
    is_allowed = True
    if user_role == 'restricted':
        # Restricted users can only access pages in their allowed_pages list
        if current_page not in allowed_pages:
            is_allowed = False
            # Do NOT change current_page or rerun here. Just display the error.
            st.error(f"⛔ Access Denied: Your role ('{user_role}') does not permit access to the '{current_page}' page.")

    # Render the selected page ONLY if allowed
    if is_allowed:
        if current_page == "Dashboard":
            from pages.dashboard import show_dashboard
            show_dashboard()
        elif current_page == "Create Bill":
            from pages.create_bill import create_new_bill
            create_new_bill()
        elif current_page == "Contractors":
            from pages.contractors import contractor_management
            contractor_management()
        elif current_page == "Works":
            from pages.works import works_management
            works_management()
        elif current_page == "Reports":
            from pages.reports import show_reports
            show_reports()
        elif current_page == "User Management":
            # This page is only accessible to admins (controlled by sidebar and this check)
            if user_role == 'admin':
                from pages.user_management import show_user_management
                show_user_management()
            else:
                # This case should technically not be reachable if sidebar logic is correct,
                # but keeping the check is safer.
                st.error("⛔ Access Denied.")
    # Add other pages here if necessary
    # If not allowed, the error message is already displayed above, and no page content is rendered.

if __name__ == "__main__":
    # Clear any residual session state issues
    if 'init' not in st.session_state:
        st.session_state.clear()
        st.session_state.init = True
    main()
