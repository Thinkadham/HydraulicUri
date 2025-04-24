import streamlit as st
import pandas as pd
from utils.db import get_contractors, insert_contractor
from utils.helpers import current_date
from utils.form_manager import FormManager  # Import the FormManager class

def contractor_management():
    # Initialize FormManager
    form_manager = FormManager("contractor_management")
    
    st.header("Contractor Management")
    
    tab1, tab2 = st.tabs(["View Contractors", "Add New Contractor"])
    
    with tab1:
        try:
            contractors = get_contractors()
            if contractors:
                df = pd.DataFrame(contractors)
                # Select which columns to display
                columns_to_show = ["name", "parentage", "resident", "registration", "class", "pan", "account_no"]
                st.dataframe(df[columns_to_show], use_container_width=True)
            else:
                st.info("No contractors found in the database")
        except Exception as e:
            st.error(f"Error loading contractors: {str(e)}")
        
    with tab2:
        with form_manager.form("contractor_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = form_manager.text_input("Name*", "contractor_form", "name")
                parentage = form_manager.text_input("Parentage/S/O", "contractor_form", "parentage")
                resident = form_manager.text_input("Resident/R/O", "contractor_form", "resident")
                registration = form_manager.text_input("Registration No", "contractor_form", "registration")
                
            with col2:
                contractor_class = form_manager.selectbox(
                    "Class*", 
                    "contractor_form", 
                    "class", 
                    options=["A", "B", "C", "D", "E"]
                )
                pan = form_manager.text_input("PAN", "contractor_form", "pan")
                gstin = form_manager.text_input("GSTIN", "contractor_form", "gstin")
                account_no = form_manager.text_input("Account No*", "contractor_form", "account_no")
                
            st.markdown("**Required fields*")
            
            if form_manager.form_submit_button("contractor_form", "Add Contractor"):
                # Validate required fields
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

# Run the function
contractor_management()
