import streamlit as st
import pandas as pd
from utils.db import get_contractors, get_works, get_bills
from utils.form_manager import FormManager

def show_settings():
    # Initialize FormManager
    form_manager = FormManager("settings")
    
    st.header("Settings")
    
    with st.expander("User Management"):
        with form_manager.form("user_management_form"):
            st.write("User management functionality would go here")
            # Example user management controls
            form_manager.text_input("Add New User", "user_management_form", "new_username")
            if form_manager.form_submit_button("user_management_form", "Add User"):
                st.success("User added (simulated)")
    
    with st.expander("System Configuration"):
        with form_manager.form("system_config_form"):
            st.write("System configuration options would go here")
            # Example configuration controls
            theme = form_manager.selectbox(
                "Select Theme", 
                "system_config_form", 
                "theme", 
                options=["Light", "Dark", "System"]
            )
            if form_manager.form_submit_button("system_config_form", "Save Configuration"):
                st.success(f"Configuration saved: {theme} theme selected")
    
    with st.expander("Backup & Restore"):
        with form_manager.form("backup_form"):
            if form_manager.form_submit_button("backup_form", "Create Backup"):
                try:
                    # Export all tables to CSV
                    tables = {
                        "contractors": get_contractors(),
                        "works": get_works(),
                        "bills": get_bills()
                    }
                    
                    backup_files = {}
                    for table_name, data in tables.items():
                        df = pd.DataFrame(data)
                        if not df.empty:
                            csv = df.to_csv(index=False)
                            backup_files[f"{table_name}_backup.csv"] = csv
                    
                    if backup_files:
                        for filename, content in backup_files.items():
                            st.download_button(
                                f"Download {filename}",
                                data=content,
                                file_name=filename,
                                mime="text/csv",
                                key=form_manager.get_form_key("backup_form") + f"_{filename}"
                            )
                        st.success("Backup files ready for download")
                    else:
                        st.warning("No data available to backup")
                except Exception as e:
                    st.error(f"Error creating backup: {str(e)}")

            # Restore functionality (placeholder)
            uploaded_file = form_manager.file_uploader(
                "Upload Backup File", 
                "backup_form", 
                "restore_upload",
                type=["csv"]
            )
            if uploaded_file:
                st.warning("Restore functionality would be implemented here")

show_settings()
