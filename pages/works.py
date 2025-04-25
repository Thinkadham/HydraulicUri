import streamlit as st
import pandas as pd
from utils.db import get_works, insert_work
from utils.helpers import current_date

def works_management():
    st.header("Works Management")
    
    tab1, tab2 = st.tabs(["View Works", "Add New Work"])
    
    with tab1:
        try:
            works = get_works()
            if works:
                df = pd.DataFrame(works)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "aaa_amount": st.column_config.NumberColumn(
                            "AAA Amount",
                            format="₹%.2f"
                        ),
                        "allotment_amount": st.column_config.NumberColumn(
                            "Allotment",
                            format="₹%.2f"
                        ),
                        "expenditure": st.column_config.NumberColumn(
                            "Expenditure",
                            format="₹%.2f"
                        ),
                        "aaa_date": st.column_config.DateColumn(
                            "AAA Date",
                            format="DD/MM/YYYY"
                        )
                    }
                )
            else:
                st.info("No works found in the database")
        except Exception as e:
            st.error(f"Error loading works: {str(e)}")
        
    with tab2:
        with st.form("work_form", clear_on_submit=True):
            st.subheader("New Work Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                mh = st.number_input(
                    "Major Head (MH)*",
                    min_value=0,
                    step=1,
                    key="work_mh"
                )
                scheme = st.text_input(
                    "Scheme*",
                    key="work_scheme"
                )
                work_name = st.text_input(
                    "Work Name*",
                    key="work_name"
                )
                work_code = st.text_input(
                    "Work Code*",
                    key="work_code"
                )
                
            with col2:
                classification = st.text_input(
                    "Classification",
                    key="work_classification"
                )
                aaa_no = st.text_input(
                    "AAA Number*",
                    key="work_aaa_no"
                )
                aaa_date = st.date_input(
                    "AAA Date*",
                    key="work_aaa_date"
                )
                aaa_amount = st.number_input(
                    "AAA Amount*",
                    min_value=0.0,
                    value=0.0,
                    step=1000.0,
                    format="%.2f",
                    key="work_aaa_amount"
                )
                
            nomenclature = st.text_area(
                "Nomenclature",
                height=100,
                key="work_nomenclature"
            )
            
            if st.form_submit_button("Add Work"):
                # Validate required fields
                required_fields = {
                    "Major Head": mh,
                    "Scheme": scheme,
                    "Work Name": work_name,
                    "Work Code": work_code,
                    "AAA Number": aaa_no,
                    "AAA Amount": aaa_amount
                }
                
                missing = [field for field, value in required_fields.items() if not value]
                
                if missing:
                    st.error(f"Missing required fields: {', '.join(missing)}")
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
                        "expenditure": 0.0,
                        "created_at": current_date()
                    }
                    
                    try:
                        result = insert_work(work_data)
                        if result:
                            st.success("Work added successfully!")
                            st.balloons()
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error adding work: {str(e)}")

works_management()
