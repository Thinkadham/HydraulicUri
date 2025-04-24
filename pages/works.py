import streamlit as st
import pandas as pd
from utils.db import get_works, insert_work
from utils.helpers import current_date
from utils.form_manager import FormManager

def works_management():
    # Initialize FormManager
    form_manager = FormManager("works_management")
    
    st.header("Works Management")
    
    tab1, tab2 = st.tabs(["View Works", "Add New Work"])
    
    with tab1:
        try:
            works = get_works()
            if works:
                df = pd.DataFrame(works)
                # Configure columns for better display
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "aaa_amount": st.column_config.NumberColumn(format="₹%.2f"),
                        "allotment_amount": st.column_config.NumberColumn(format="₹%.2f"),
                        "expenditure": st.column_config.NumberColumn(format="₹%.2f"),
                        "aaa_date": st.column_config.DateColumn(format="DD/MM/YYYY"),
                        "created_at": st.column_config.DateColumn(format="DD/MM/YYYY")
                    }
                )
            else:
                st.info("No works found in the database")
        except Exception as e:
            st.error(f"Error loading works: {str(e)}")
        
    with tab2:
        with form_manager.form("work_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                mh = form_manager.number_input(
                    "Major Head (MH)", 
                    "work_form", 
                    "mh", 
                    min_value=0
                )
                scheme = form_manager.text_input(
                    "Scheme", 
                    "work_form", 
                    "scheme"
                )
                work_name = form_manager.text_input(
                    "Work Name", 
                    "work_form", 
                    "work_name"
                )
                work_code = form_manager.text_input(
                    "Work Code", 
                    "work_form", 
                    "work_code"
                )
                
            with col2:
                classification = form_manager.text_input(
                    "Classification", 
                    "work_form", 
                    "classification"
                )
                aaa_no = form_manager.text_input(
                    "AAA No", 
                    "work_form", 
                    "aaa_no"
                )
                aaa_date = form_manager.date_input(
                    "AAA Date", 
                    "work_form", 
                    "aaa_date"
                )
                aaa_amount = form_manager.number_input(
                    "AAA Amount", 
                    "work_form", 
                    "aaa_amount", 
                    min_value=0
                )
                
            nomenclature = form_manager.text_area(
                "Nomenclature", 
                "work_form", 
                "nomenclature"
            )
            expenditure = form_manager.number_input(
                "Initial Expenditure", 
                "work_form", 
                "expenditure", 
                min_value=0, 
                value=0
            )
            
            if form_manager.form_submit_button("work_form", "Add Work"):
                # Validate required fields
                if not all([mh, scheme, work_name, work_code, aaa_no, aaa_amount]):
                    st.error("Please fill in all required fields (MH, Scheme, Work Name, Work Code, AAA No, AAA Amount)")
                else:
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
