import streamlit as st
import pandas as pd
import os
from services import get_contractors, get_works, get_recent_bills

def show():
    """System Settings Page"""
    st.header("Settings")
    
    tab1, tab2, tab3 = st.tabs(["User Management", "System Configuration", "Backup & Restore"])
    
    with tab1:
        st.subheader("User Accounts")
        users = [
            {"username": "admin", "role": "Administrator", "last_login": "2023-11-15"},
            {"username": "accountant", "role": "Accountant", "last_login": "2023-11-14"}
        ]
        df_users = pd.DataFrame(users)
        st.dataframe(df_users, use_container_width=True)
        
        with st.expander("Add New User"):
            with st.form("user_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                role = st.selectbox("Role", ["Administrator", "Accountant", "Viewer"])
                
                if st.form_submit_button("Create User"):
                    st.success(f"User {username} created successfully!")
    
    with tab2:
        st.subheader("System Preferences")
        
        with st.form("system_config"):
            col1, col2 = st.columns(2)
            
            with col1:
                default_currency = st.selectbox(
                    "Default Currency",
                    ["₹ Indian Rupee", "$ US Dollar", "€ Euro"]
                )
                date_format = st.selectbox(
                    "Date Format",
                    ["DD-MM-YYYY", "MM-DD-YYYY", "YYYY-MM-DD"]
                )
                
            with col2:
                tax_rate = st.number_input(
                    "Default Tax Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=2.24
                )
                cess_rate = st.number_input(
                    "Default Cess Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=1.0
                )
            
            if st.form_submit_button("Save Configuration"):
                st.success("System preferences saved!")
    
    with tab3:
        st.subheader("Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Database Backup**")
            if st.button("Export All Data to CSV"):
                try:
                    export_data()
                    st.success("Backup completed successfully!")
                except Exception as e:
                    st.error(f"Backup failed: {str(e)}")
            
        with col2:
            st.markdown("**System Information**")
            st.metric("Total Contractors", len(get_contractors() or []))
            st.metric("Active Works", len(get_works() or []))
            st.metric("Pending Bills", len([b for b in (get_recent_bills() or []) if b.get("status") == "Pending"]))

def export_data():
    """Export all data to CSV files"""
    tables = {
        "contractors": get_contractors(),
        "works": get_works(),
        "bills": get_recent_bills()
    }
    
    os.makedirs("backups", exist_ok=True)
    
    for table_name, data in tables.items():
        if data:
            df = pd.DataFrame(data)
            df.to_csv(f"backups/{table_name}_backup_{pd.Timestamp.now().strftime('%Y%m%d')}.csv", 
                     index=False)
