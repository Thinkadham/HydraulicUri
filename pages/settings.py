import streamlit as st
import pandas as pd
from utils.db import get_contractors, get_works, get_bills

def show_settings():
    st.header("Settings")
    
    # User Management Section
    with st.expander("User Management"):
        with st.form("user_management_form", clear_on_submit=True):
            st.subheader("Add New User")
            new_username = st.text_input("Username*", key="new_username")
            user_role = st.selectbox(
                "Role*",
                options=["Admin", "Editor", "Viewer"],
                key="user_role"
            )
            user_email = st.text_input("Email", key="user_email")
            
            if st.form_submit_button("Create User"):
                if not new_username or not user_role:
                    st.error("Please fill required fields (Username and Role)")
                else:
                    # Add your user creation logic here
                    st.success(f"User '{new_username}' created with {user_role} role")

    # System Configuration Section
    with st.expander("System Configuration"):
        with st.form("system_config_form"):
            st.subheader("Appearance Settings")
            theme = st.selectbox(
                "Select Theme*",
                options=["Light", "Dark", "System Default"],
                index=2,
                key="theme_select"
            )
            font_size = st.slider(
                "Base Font Size",
                min_value=12,
                max_value=24,
                value=16,
                key="font_size"
            )
            
            if st.form_submit_button("Save Configuration"):
                # Add your config save logic here
                st.success("Configuration saved successfully")

    # Backup & Restore Section
    with st.expander("Backup & Restore"):
        with st.form("backup_form"):
            st.subheader("Data Backup")
            backup_options = st.multiselect(
                "Select Data to Backup",
                options=["Contractors", "Works", "Bills"],
                default=["Contractors", "Works", "Bills"],
                key="backup_options"
            )
            
            if st.form_submit_button("Generate Backup"):
                try:
                    backup_data = {}
                    if "Contractors" in backup_options:
                        contractors = get_contractors()
                        if contractors:
                            backup_data["contractors"] = pd.DataFrame(contractors)
                    
                    if "Works" in backup_options:
                        works = get_works()
                        if works:
                            backup_data["works"] = pd.DataFrame(works)
                    
                    if "Bills" in backup_options:
                        bills = get_bills()
                        if bills:
                            backup_data["bills"] = pd.DataFrame(bills)

                    if backup_data:
                        for name, df in backup_data.items():
                            csv = df.to_csv(index=False)
                            st.download_button(
                                f"Download {name.capitalize()} Backup",
                                data=csv,
                                file_name=f"{name}_backup.csv",
                                mime="text/csv",
                                key=f"{name}_download"
                            )
                        st.success("Backup files ready for download")
                    else:
                        st.warning("No data available for selected options")
                except Exception as e:
                    st.error(f"Backup failed: {str(e)}")

            st.subheader("Data Restore")
            restore_file = st.file_uploader(
                "Upload Backup File",
                type=["csv"],
                key="restore_upload"
            )
            if restore_file:
                st.warning("Restore functionality would be implemented here")

show_settings()
