import streamlit as st
import pandas as pd
from services import get_contractors, add_contractor

def show():
    """Contractor Management Page"""
    st.header("Contractor Management")
    
    tab1, tab2 = st.tabs(["View Contractors", "Add New Contractor"])
    
    with tab1:
        try:
            contractors = get_contractors()
            if contractors:
                df = pd.DataFrame(contractors)
                st.dataframe(df[["name", "registration", "class", "pan", "gstin"]], 
                           use_container_width=True)
            else:
                st.warning("No contractors found")
        except Exception as e:
            st.error(f"Error loading contractors: {str(e)}")
    
    with tab2:
        with st.form("contractor_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name*", key="contractor_name")
                parentage = st.text_input("Parentage")
                resident = st.text_input("Resident Address*")
                registration = st.text_input("Registration Number*")
                
            with col2:
                contractor_class = st.selectbox("Class*", ["A", "B", "C", "D", "E"])
                pan = st.text_input("PAN Number")
                gstin = st.text_input("GSTIN")
                account_no = st.text_input("Bank Account Number*")
                
            if st.form_submit_button("Add Contractor"):
                if not all([name, resident, registration, account_no]):
                    st.error("Please fill all required fields (*)")
                else:
                    try:
                        contractor_data = {
                            "name": name,
                            "parentage": parentage,
                            "resident": resident,
                            "registration": registration,
                            "class": contractor_class,
                            "pan": pan,
                            "gstin": gstin,
                            "account_no": account_no
                        }
                        
                        result = add_contractor(contractor_data)
                        if result:
                            st.success("Contractor added successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to add contractor")
                    except Exception as e:
                        st.error(f"Error adding contractor: {str(e)}")
