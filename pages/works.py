import streamlit as st
import pandas as pd
from datetime import datetime
from services import get_works, add_work

def show():
    """Works Management Page"""
    st.header("Works Management")
    
    tab1, tab2 = st.tabs(["View Works", "Add New Work"])
    
    with tab1:
        try:
            works = get_works()
            if works:
                df = pd.DataFrame(works)
                # Format dates for display
                df['aaa_date'] = pd.to_datetime(df['aaa_date']).dt.strftime('%Y-%m-%d')
                st.dataframe(df[[
                    "work_name", "scheme", "mh", 
                    "aaa_no", "aaa_date", "allotment_amount",
                    "expenditure", "work_code"
                ]], use_container_width=True)
                
                # Calculate and display summary stats
                total_allotted = df['allotment_amount'].sum()
                total_spent = df['expenditure'].sum()
                balance = total_allotted - total_spent
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Allotted", f"₹{total_allotted:,.2f}")
                col2.metric("Total Expenditure", f"₹{total_spent:,.2f}")
                col3.metric("Remaining Balance", f"₹{balance:,.2f}")
            else:
                st.warning("No works found")
        except Exception as e:
            st.error(f"Error loading works: {str(e)}")
    
    with tab2:
        with st.form("work_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                work_name = st.text_input("Work Name*")
                scheme = st.text_input("Scheme*")
                mh = st.number_input("Major Head (MH)*", min_value=0, step=1)
                work_code = st.text_input("Work Code")
                
            with col2:
                classification = st.text_input("Classification")
                aaa_no = st.text_input("AAA Number*")
                aaa_date = st.date_input("AAA Date*", datetime.now())
                aaa_amount = st.number_input("Allotment Amount (₹)*", min_value=0.0)
            
            nomenclature = st.text_area("Nomenclature")
            initial_expenditure = st.number_input("Initial Expenditure (₹)", min_value=0.0, value=0.0)
            
            if st.form_submit_button("Add Work"):
                if not all([work_name, scheme, mh, aaa_no, aaa_amount]):
                    st.error("Please fill all required fields (*)")
                else:
                    try:
                        work_data = {
                            "work_name": work_name,
                            "scheme": scheme,
                            "mh": mh,
                            "work_code": work_code,
                            "classification": classification,
                            "aaa_no": aaa_no,
                            "aaa_date": aaa_date.isoformat(),
                            "aaa_amount": aaa_amount,
                            "nomenclature": nomenclature,
                            "allotment_amount": aaa_amount,
                            "expenditure": initial_expenditure
                        }
                        
                        result = add_work(work_data)
                        if result:
                            st.success("Work added successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to add work")
                    except Exception as e:
                        st.error(f"Error adding work: {str(e)}")
