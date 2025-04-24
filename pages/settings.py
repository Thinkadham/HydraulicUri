import streamlit as st
from utils.db import get_contractors, get_works, get_bills


def show_settings():
    st.header("Settings")
    
    with st.expander("User Management"):
        st.write("User management functionality would go here")
        
    with st.expander("System Configuration"):
        st.write("System configuration options would go here")
        
    with st.expander("Backup & Restore"):
        if st.button("Create Backup"):
            try:
                # Export all tables to CSV
                tables = {
                    "contractors": get_contractors(),
                    "works": get_works(),
                    "bills": get_bills()
                }
                
                for table_name, data in tables.items():
                    pd.DataFrame(data).to_csv(f"{table_name}_backup.csv", index=False)
                
                st.success("Backup created successfully! Check your local files.")
            except Exception as e:
                st.error(f"Error creating backup: {str(e)}")

show_settings()
