import streamlit as st
from utils.db import get_contractors, insert_contractor
from utils.helpers import current_date

def contractor_management():
    st.header("Contractor Management")
    
    tab1, tab2 = st.tabs(["View Contractors", "Add New Contractor"])
    
    with tab1:
        contractors = get_contractors()
        st.dataframe(pd.DataFrame(contractors), use_container_width=True)
        
    with tab2:
        with st.form("contractor_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name", key="contractor_name")
                parentage = st.text_input("Parentage")
                resident = st.text_input("Resident")
                registration = st.text_input("Registration")
                
            with col2:
                contractor_class = st.selectbox("Class", ["A", "B", "C", "D", "E"])
                pan = st.text_input("PAN")
                gstin = st.text_input("GSTIN")
                account_no = st.text_input("Account No")
                
            if st.form_submit_button("Add Contractor"):
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
