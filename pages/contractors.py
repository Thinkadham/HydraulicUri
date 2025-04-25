import streamlit as st
import pandas as pd
from utils.db import get_contractors, insert_contractor
from utils.helpers import current_date

def contractor_management():
    st.header("Contractor Management")
    
    tab1, tab2 = st.tabs(["View Contractors", "Add New Contractor"])
    
    with tab1:
        try:
            contractors = get_contractors()
            if contractors:
                df = pd.DataFrame(contractors)
                columns_to_show = ["name", "parentage", "resident", "registration", "class", "pan", "account_no"]
                st.dataframe(df[columns_to_show], use_container_width=True)
            else:
                st.info("No contractors found in the database")
        except Exception as e:
            st.error(f"Error loading contractors: {str(e)}")
        
    with tab2:
        with st.form("contractor_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name*", key="contractor_name")
                parentage = st.text_input("Parentage/S/O", key="contractor_parentage")
                resident = st.text_input("Resident/R/O", key="contractor_resident")
                registration = st.text_input("Registration No", key="contractor_registration")
                
            with col2:
                contractor_class = st.selectbox(
                    "Class*", 
                    options=["A", "B", "C", "D", "E"],
                    key="contractor_class"
                )
                pan = st.text_input("PAN", key="contractor_pan")
                gstin = st.text_input("GSTIN", key="contractor_gstin")
                account_no = st.text_input("Account No*", key="contractor_account")
                
            st.markdown("**Required fields*")
            
            if st.form_submit_button("Add Contractor"):
                if not name or not contractor_class or not account_no:
                    st.error("Please fill in all required fields")
                else:
                    contractor_data = {
                        "name": name,
                        "parentage": parentage,
                        "resident": resident,
                        "registration": registration,
                        "class": contractor_class,
                        "pan": pan,
                        "gstin": gstin,
                        "account_no": account_no,
                        "created_at": current_date()
                    }
                    
                    try:
                        result = insert_contractor(contractor_data)
                        if result.data:
                            st.success("Contractor added successfully!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error adding contractor: {str(e)}")

contractor_management()
