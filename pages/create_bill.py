import streamlit as st
import datetime
from utils.db import get_contractors, get_works, insert_bill, update_work_expenditure
from utils.helpers import amount_in_words, calculate_deductions
from utils.auth import check_auth

# Only show content if authenticated
if not check_auth():
    st.warning("Please log in to access this page")
    st.stop()

def create_new_bill():
    st.header("Create New Bill")
    
    # Fetch data from Supabase
    contractors = get_contractors()
    works = get_works()
    
    with st.form("bill_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Payee information
            payee = st.selectbox("Select Payee", [c["name"] for c in contractors])
            payee_data = next((c for c in contractors if c["name"] == payee), {})
            
            st.text_input("S/O", payee_data.get("parentage", ""))
            st.text_input("R/O", payee_data.get("resident", ""))
            st.text_input("Registration", payee_data.get("registration", ""))
            st.text_input("Class", payee_data.get("class", ""))
            
        with col2:
            st.text_input("PAN", payee_data.get("pan", ""))
            st.text_input("GSTIN", payee_data.get("gstin", ""))
            st.text_input("Account No", payee_data.get("account_no", ""))
            
        # Bill details
        bill_type = st.selectbox("Bill Type", ["Plan", "Non Plan"])
        major_heads = list(set(w["mh"] for w in works))
        major_head = st.selectbox("Major Head", major_heads)
        
        # Filter schemes based on selected major head
        schemes = list(set(w["scheme"] for w in works if w["mh"] == major_head))
        scheme = st.selectbox("Scheme", schemes)
        
        # Filter works based on selected scheme
        filtered_works = [w for w in works if w["mh"] == major_head and w["scheme"] == scheme]
        work = st.selectbox("Name of Work/Particulars", [w["work_name"] for w in filtered_works])
        
        # Get work details
        work_data = next((w for w in filtered_works if w["work_name"] == work), {})
        
        st.text_area("Nomenclature", work_data.get("nomenclature", ""))
        
        # Bill amounts
        col3, col4 = st.columns(2)
        with col3:
            billed_amount = st.number_input("Billed Amount", min_value=0)
            deduct_payments = st.number_input("Deduct Payments", min_value=0)
            payable = billed_amount - deduct_payments
            st.text_input("Payable", payable, disabled=True)
            
        with col4:
            funds_available = st.number_input("Funds Available", min_value=0)
            
            # Deductions
            income_tax_percent = st.number_input("Income Tax %age", min_value=0.0, max_value=100.0, value=2.24)
            deposit_percent = st.number_input("Deposit %age", min_value=0.0, max_value=100.0, value=10.0)
            cess_percent = st.number_input("Cess", min_value=0.0, max_value=100.0, value=1.0)
            
        # Bill classification
        cc_bill = st.selectbox("CC of Bill", ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"])
        final_bill = st.radio("Final Bill", ["Yes", "No"])
        
        # Allotment details
        st.subheader("Allotment Details")
        col5, col6 = st.columns(2)
        with col5:
            allotment_no = st.text_input("Allotment No")
            allotment_date = st.date_input("Allotment Date")
            allotment_amount = st.number_input("Allotment Amount", min_value=0)
            
        with col6:
            ts_no = st.text_input("TS No")
            ts_date = st.date_input("TS Date")
            ts_amount = st.number_input("TS Amount", min_value=0)
            
        # Submit button
        if st.form_submit_button("Generate Bill"):
            # Calculate deductions and net amount
            income_tax, deposit, cess, total_deduction, net_amount = calculate_deductions(
                payable, income_tax_percent, deposit_percent, cess_percent
            )
            
            # Generate bill data
            bill_data = {
                "payee": payee,
                "payee_id": payee_data.get("id"),
                "work": work,
                "work_id": work_data.get("id"),
                "bill_type": bill_type,
                "major_head": major_head,
                "scheme": scheme,
                "nomenclature": work_data.get("nomenclature", ""),
                "billed_amount": billed_amount,
                "deduct_payments": deduct_payments,
                "payable": payable,
                "funds_available": funds_available,
                "income_tax_percent": income_tax_percent,
                "income_tax_amount": income_tax,
                "deposit_percent": deposit_percent,
                "deposit_amount": deposit,
                "cess_percent": cess_percent,
                "cess_amount": cess,
                "total_deduction": total_deduction,
                "net_amount": net_amount,
                "amount_in_words": amount_in_words(net_amount),
                "cc_bill": cc_bill,
                "final_bill": final_bill == "Yes",
                "allotment_no": allotment_no,
                "allotment_date": allotment_date.isoformat(),
                "allotment_amount": allotment_amount,
                "ts_no": ts_no,
                "ts_date": ts_date.isoformat(),
                "ts_amount": ts_amount,
                "status": "Pending",
                "created_at": current_date()
            }
            
            # Insert into Supabase
            try:
                result = insert_bill(bill_data)
                if result.data:
                    st.success("Bill saved successfully!")
                    
                    # Update work expenditure in Supabase
                    current_expenditure = work_data.get("expenditure", 0)
                    new_expenditure = current_expenditure + billed_amount
                    update_work_expenditure(work_data["id"], new_expenditure)
            except Exception as e:
                st.error(f"Error saving bill: {str(e)}")

create_new_bill()
