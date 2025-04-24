import streamlit as st
from utils.auth import check_auth, login, logout

# App Configuration
st.set_page_config(
    page_title="Auto Payment System",
    page_icon="💰",
    layout="wide"
)

# Add logout button to sidebar if authenticated
if check_auth():
    st.sidebar.button("Logout", on_click=logout)

# Main App
def main():
    st.title("Auto Payment System")
    st.caption(f"Version 2.0.1 | Logged in as: {st.session_state.get('username', 'admin')}")
    st.caption("Designed & Developed by Mohammad Adham Wani")
    st.warning("Please navigate using the sidebar menu")

# Run the app
if __name__ == "__main__":
    if check_auth():
        main()
    else:
        login()
