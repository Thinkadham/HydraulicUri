import streamlit as st
from utils.auth import check_auth, login, logout
from PIL import Image
import os

# App Configuration
st.set_page_config(
    page_title="Auto Payment System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load logo (create a 'assets' folder in your project root)
def load_logo():
    try:
        return Image.open("assets/logo.png")  # Add your logo.png to assets folder
    except:
        return None

# Custom sidebar with logo and navigation
def show_sidebar():
    logo = load_logo()
    if logo:
        st.sidebar.image(logo, width=200)
    
    st.sidebar.title("Auto Payment System")
    st.sidebar.markdown("---")
    
    if check_auth():
        # Navigation menu
        menu_options = {
            "Dashboard": "🏠",
            "Create New Bill": "🧾",
            "Contractor Management": "👷",
            "Works Management": "🏗️",
            "Reports": "📊",
            "Settings": "⚙️"
        }
        
        selected = st.sidebar.radio(
            "Navigation",
            list(menu_options.keys()),
            format_func=lambda x: f"{menu_options[x]} {x}"
        )
        
        # Logout button at bottom
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout"):
            logout()
        
        return selected
    return None

# Main App
def main():
    selected_page = show_sidebar()
    
    if selected_page:
        st.title(f"{selected_page}")
        st.caption(f"Version 2.0.1 | Logged in as: {st.session_state.get('username', 'admin')}")
        
        # Page routing
        if selected_page == "Dashboard":
            from pages.dashboard import show_dashboard
            show_dashboard()
        elif selected_page == "Create New Bill":
            from pages.create_bill import create_new_bill
            create_new_bill()
        elif selected_page == "Contractor Management":
            from pages.contractors import contractor_management
            contractor_management()
        elif selected_page == "Works Management":
            from pages.works import works_management
            works_management()
        elif selected_page == "Reports":
            from pages.reports import show_reports
            show_reports()
        elif selected_page == "Settings":
            from pages.settings import show_settings
            show_settings()

# Run the app
if __name__ == "__main__":
    if check_auth():
        main()
    else:
        login()
