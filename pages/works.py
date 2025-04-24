import streamlit as st
import pandas as pd
from utils.db import get_works, insert_work
from utils.helpers import current_date

def works_management():
    st.header("Works Management")
    
    tab1, tab2 = st.tabs(["View Works", "Add New Work"])
    
    with tab1:
        works = get_works()
        st.dataframe(pd.DataFrame(works), use_container_width=True)
        
    with tab2:
        with st.form("work_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                mh = st.number_input("Major Head (MH)", min_value=0)
                scheme = st.text_input("Scheme")
                work_name = st.text_input("Work Name")
                work_code = st.text_input("Work Code")
                
            with col2:
                classification = st.text_input("Classification")
                aaa_no = st.text_input("AAA No")
                aaa_date = st.date_input("AAA Date")
                aaa_amount = st.number_input("AAA Amount", min_value=0)
                
            nomenclature = st.text_area("Nomenclature")
            expenditure = st.number_input("Initial Expenditure", min_value=0, value=0)
            
            if st.form_submit_button("Add Work"):
                work_data = {
                    "mh": mh,
                    "scheme": scheme,
                    "work_name": work_name,
                    "work_code": work_code,
                    "classification": classification,
                    "aaa_no": aaa_no,
                    "aaa_date": aaa_date.isoformat(),
                    "aaa_amount": aaa_amount,
                    "nomenclature": nomenclature,
                    "allotment_amount": aaa_amount,
                    "expenditure": expenditure,
                    "created_at": current_date()
                }
                
                try:
                    result = insert_work(work_data)
                    if result.data:
                        st.success("Work added successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error adding work: {str(e)}")

works_management()
