import streamlit as st
import pandas as pd
from utils.db import get_contractors, insert_contractor
from utils.helpers import current_date

def contractor_management():
    st.header("Contractor Management")
    
    # Tab setup
    list_tab, add_tab = st.tabs(["Contractor List", "Add Contractor"])

    with list_tab:
        try:
            contractors = get_contractors()
            if contractors:
                df = pd.DataFrame(contractors)[["name", "class", "account_no", "pan"]]
                st.dataframe(
                    df.rename(columns={
                        "name": "Name",
                        "class": "Class",
                        "account_no": "Account Number",
                        "pan": "PAN"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No contractors found")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    with add_tab:
        with st.form(key="contractors_form", clear_on_submit=True):
            name = st.text_input("Full Name*", help="Legal name of contractor")
            parentage = st.text_input("Parentage", help="Father's/Husband's name")
            resident = st.text_input("Resident Address*", help="Current residential address")
            registration = st.text_input("Registration No", help="Business registration number")
            contractor_class = st.selectbox("Class*", ["A", "B", "C", "D", "E"])
            pan = st.text_input("PAN*", max_chars=10,help="Permanent Account Number (10 characters)")
            gstin = st.text_input("GSTIN", max_chars=15,help="15-character GST identification number")
            account_no = st.text_input("Account No*", help="Bank account number")

            submitted = st.form_submit_button("Add Contractor")

            if submitted:
                errors = []
                if not name.strip(): errors.append("Name is required")
                if not account_no.strip(): errors.append("Account number is required")
                if pan and len(pan) != 10: errors.append("PAN must be 10 characters")

                if not errors:
                    try:
                        insert_contractor({
                            "name": name.strip(),
                            "account_no": account_no.strip(),
                            "class": contractor_class,
                            "pan": pan.upper() if pan else None,
                            "gstin": gstin.upper() if gstin else None,
                            "registration": registration.strip() or None,                               
                            "parentage": parentage.strip() or None,
                            "resident": resident.strip() or None,
                            "created_at": current_date()
                        })
                        st.success("Contractor added successfully!")
                        st.balloons()
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Database error: {str(e)}")
                else:
                    for error in errors:
                        st.error(error)

if __name__ == "__main__":
    contractor_management()
