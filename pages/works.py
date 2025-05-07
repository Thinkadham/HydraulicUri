import streamlit as st
import pandas as pd
from utils.db import get_works, insert_work
# Removed: from utils.helpers import current_date - as created_at is removed

def works_management():
    st.header("Works Plan Management") # Changed header
    
    tab1, tab2 = st.tabs(["View Works Plan", "Add New Work to Plan"]) # Changed tab names
    
    with tab1:
        try:
            works_plan_data = get_works() # Function now gets from works_plan
            if works_plan_data:
                df = pd.DataFrame(works_plan_data)
                # Dynamically create column_config for all columns in works_plan
                column_config = {}
                if not df.empty:
                    for col in df.columns:
                        if "id" == col.lower() : # hide id column
                             column_config[col] = st.column_config.Column(disabled=True)
                        elif "dt" in col.lower() or "dos" in col.lower() or "doc" in col.lower(): # Date columns
                            column_config[col] = st.column_config.DateColumn(
                                col.replace("_", " ").title(), # Prettify column name
                                format="DD/MM/YYYY"
                            )
                        elif "amt" in col.lower(): # Amount columns
                            column_config[col] = st.column_config.NumberColumn(
                                col.replace("_", " ").title(),
                                format="₹%.2f"
                            )
                        elif "toc" == col.lower(): # TOC as number
                             column_config[col] = st.column_config.NumberColumn(
                                col.replace("_", " ").title(),
                                format="%d" # Integer format
                            )
                        else: # Default for other text columns
                            column_config[col] = st.column_config.TextColumn(
                                col.replace("_", " ").title()
                            )
                
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config=column_config
                )
            else:
                st.info("No works found in the works_plan table.")
        except Exception as e:
            st.error(f"Error loading works plan: {str(e)}")
        
    with tab2:
        with st.form(key="works_plan_form", clear_on_submit=True): # Changed form key
            st.subheader("New Work Plan Details")
            
            # Create columns for the form based on works_plan schema
            # Grouping them logically
            
            c1, c2 = st.columns(2)
            with c1:
                workcode = st.text_input("Workcode*", key="wp_workcode")
                aaa_no = st.text_input("AAA No*", key="wp_aaa_no")
                aaa_dt = st.date_input("AAA Date*", key="wp_aaa_dt")
                aaa_amt = st.number_input("AAA Amount*", min_value=0.0, format="%.2f", key="wp_aaa_amt")
                ts_no = st.text_input("TS No", key="wp_ts_no")
                ts_dt = st.date_input("TS Date", key="wp_ts_dt")
                ts_amt = st.number_input("TS Amount", min_value=0.0, format="%.2f", key="wp_ts_amt")
                
            with c2:
                allot_no = st.text_input("Allot No*", key="wp_allot_no")
                allot_dt = st.date_input("Allot Date", key="wp_allot_dt")
                allot_amt = st.number_input("Allot Amount", min_value=0.0, format="%.2f", key="wp_allot_amt")
                agr_no = st.text_input("Agr No", key="wp_agr_no")
                loi_no = st.text_input("LOI No", key="wp_loi_no")
                loi_dt = st.date_input("LOI Date", key="wp_loi_dt")
                toc = st.number_input("TOC (Time of Completion in days)", min_value=0, step=1, key="wp_toc") # Assuming TOC is duration
                dos = st.date_input("Date of Start (DOS)", key="wp_dos")
                doc = st.date_input("Date of Completion (DOC)", key="wp_doc")

            nomenclature = st.text_area("Nomenclature*", height=100, key="wp_nomenclature")

            if st.form_submit_button("Add Work to Plan"):
                # Validate required fields based on schema and common sense
                # Marked with * in input labels
                required_fields = {
                    "Workcode": workcode,
                    "Nomenclature": nomenclature,
                    "Allot No": allot_no,
                    "AAA No": aaa_no,
                    "AAA Date": aaa_dt, # aaa_dt is a date object, will be converted to isoformat
                    "AAA Amount": aaa_amt
                }
                
                missing = [field for field, value in required_fields.items() if not value and not isinstance(value, (int, float))]
                
                if missing:
                    st.error(f"Missing required fields: {', '.join(missing)}")
                else:
                    work_plan_data = {
                        "Workcode": workcode,
                        "Nomenclature": nomenclature,
                        "Allot No": allot_no,
                        "Allot Dt": allot_dt.isoformat() if allot_dt else None,
                        "Allot Amt": allot_amt if allot_amt is not None else 0.0,
                        "AAA No": aaa_no,
                        "AAA Dt": aaa_dt.isoformat() if aaa_dt else None, # Ensure date is in isoformat
                        "AAA Amt": aaa_amt if aaa_amt is not None else 0.0,
                        "TS No": ts_no,
                        "TS Dt": ts_dt.isoformat() if ts_dt else None,
                        "TS Amt": ts_amt if ts_amt is not None else 0.0,
                        "Agr No": agr_no,
                        "LOI No": loi_no,
                        "LOI Dt": loi_dt.isoformat() if loi_dt else None,
                        "TOC": toc if toc is not None else 0,
                        "DOS": dos.isoformat() if dos else None,
                        "DOC": doc.isoformat() if doc else None
                        # expenditure and created_at are removed as per user instruction
                    }
                    
                    try:
                        result = insert_work(work_plan_data) # insert_work now points to works_plan
                        if result: # Check if result indicates success (Supabase typically returns data on success)
                            st.success("Work plan added successfully!")
                            st.balloons()
                            st.rerun() # Rerun to refresh the view tab
                        else:
                            st.error("Failed to add work plan. The operation returned no result or an error.")
                    except Exception as e:
                        st.error(f"Error adding work plan: {str(e)}")
