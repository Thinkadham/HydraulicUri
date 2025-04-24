import streamlit as st
from utils.auth import check_auth, login

# App Configuration
st.set_page_config(
    page_title="Auto Payment System",
    page_icon="💰",
    layout="wide"
)

# Main App
def main():
    st.title("Auto Payment System")
    st.caption("Version 2.0.1 | Designed & Developed by Mohammad Adham Wani")
    st.warning("Please navigate using the sidebar menu")

# Run the app
if __name__ == "__main__":
    if check_auth():
        main()
    else:
        login()
