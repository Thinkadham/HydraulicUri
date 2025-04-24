import streamlit as st
from utils.auth import check_auth, login
from PIL import Image
import os

# App Configuration
st.set_page_config(
    page_title="Auto Payment System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load logo function
def load_logo():
    try:
        # Try different possible logo paths
        logo_paths = [
            "assets/logo.png",
            "logo.png",
            "images/logo.png"
        ]
        for path in logo_paths:
            if os.path.exists(path):
                return Image.open(path)
        return None
    except Exception as e:
        st.error(f"Error loading logo: {str(e)}")
        return None

# Custom sidebar
def create_sidebar():
    with st.sidebar:
        # Display logo
        logo = load_logo()
        if logo:
            st.image(logo, width=200)
        else:
            st.title("Auto Payment System")
        
        st.markdown("---")
        
        if check_auth():
            # Navigation menu with icons
            menu_options = {
                "Dashboard": "🏠",
                "Create New Bill": "🧾",
                "Contractor Management": "👷",
                "Works Management": "🏗️",
                "Reports": "📊",
                "Settings": "⚙️"
            }
            
            selected = st.radio(
                "Navigation",
                list(menu_options.keys()),
                format_func=lambda x: f"{menu_options[x]} {x}",
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            if st.button("🚪 Logout"):
                from utils.auth import logout
                logout()
            
            return selected
        return None

# Main App
def main():
    selected_page = create_sidebar()
    
    if selected_page:
        st.title(f"{selected_page}")
        
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
