import streamlit as st
import datetime
from utils.db import get_contractors, get_works, insert_bill, update_work_expenditure
from utils.helpers import amount_in_words, calculate_deductions
from utils.form_manager import FormManager  # Assuming you've saved the FormManager in this module

def create_new_bill():
    # Initialize FormManager
    form_manager = FormManager("create_bill")
    
    st.header("Create New Bill")
    
    # Fetch data from Supabase
    contractors = get_contractors()
    works = get_works()
    
    with form_manager.form("bill_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Payee information
            payee = form_manager.selectbox(
                "Select Payee", 
                "bill_form", 
                "payee", 
                options=[c["name"] for c in contractors]
            )
            payee_data = next((c for c in contractors if c["name"] == payee), {})
            
            form_manager.text_input("S/O", "bill_form", "so", value=payee_data.get("parentage", ""))
            form_manager.text_input("R/O", "bill_form", "ro", value=payee_data.get("resident", ""))
            form_manager.text_input("Registration", "bill_form", "registration", value=payee_data.get("registration", ""))
            form_manager.text_input("Class", "bill_form", "class", value=payee_data.get("class", ""))
            
        with col2:
            form_manager.text_input("PAN", "bill_form", "pan", value=payee_data.get("pan", ""))
            form_manager.text_input("GSTIN", "bill_form", "gstin", value=payee_data.get("gstin", ""))
            form_manager.text_input("Account No", "bill_form", "account_no", value=payee_data.get("account_no", ""))
            
        # Bill details
        bill_type = form_manager.selectbox(
            "Bill Type", 
            "bill_form", 
            "bill_type", 
            options=["Plan", "Non Plan"]
        )
        
        major_heads = list(set(w["mh"] for w in works))
        major_head = form_manager.selectbox(
            "Major Head", 
            "bill_form", 
            "major_head", 
            options=major_heads
        )
        
        # Filter schemes based on selected major head
        schemes = list(set(w["scheme"] for w in works if w["mh"] == major_head))
        scheme = form_manager.selectbox(
            "Scheme", 
            "bill_form", 
            "scheme", 
            options=schemes
        )
        
        # Filter works based on selected scheme
        filtered_works = [w for w in works if w["mh"] == major_head and w["scheme"] == scheme]
        work = form_manager.selectbox(
            "Name of Work/Particulars", 
            "bill_form", 
            "work", 
            options=[w["work_name"] for w in filtered_works]
        )
        
        # Get work details
        work_data = next((w for w in filtered_works if w["work_name"] == work), {})
        
        form_manager.text_area(
            "Nomenclature", 
            "bill_form", 
            "nomenclature", 
            value=work_data.get("nomenclature", "")
        )
        
        # Bill amounts
        col3, col4 = st.columns(2)
        with col3:
            billed_amount = form_manager.number_input(
                "Billed Amount", 
                "bill_form", 
                "billed_amount", 
                min_value=0
            )
            deduct_payments = form_manager.number_input(
                "Deduct Payments", 
                "bill_form", 
                "deduct_payments", 
                min_value=0
            )
            payable = billed_amount - deduct_payments
            form_manager.text_input(
                "Payable", 
                "bill_form", 
                "payable", 
                value=payable, 
                disabled=True
            )
            
        with col4:
            funds_available = form_manager.number_input(
                "Funds Available", 
                "bill_form", 
                "funds_available", 
                min_value=0
            )
            
            # Deductions
            income_tax_percent = form_manager.number_input(
                "Income Tax %age", 
                "bill_form", 
                "income_tax_percent", 
                min_value=0.0, 
                max_value=100.0, 
                value=2.24
            )
            deposit_percent = form_manager.number_input(
                "Deposit %age", 
                "bill_form", 
                "deposit_percent", 
                min_value=0.0, 
                max_value=100.0, 
                value=10.0
            )
            cess_percent = form_manager.number_input(
                "Cess", 
                "bill_form", 
                "cess_percent", 
                min_value=0.0, 
                max_value=100.0, 
                value=1.0
            )
            
        # Bill classification
        cc_bill = form_manager.selectbox(
            "CC of Bill", 
            "bill_form", 
            "cc_bill", 
            options=["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"]
        )
        final_bill = form_manager.radio(
            "Final Bill", 
            "bill_form", 
            "final_bill", 
            options=["Yes", "No"]
        )
        
        # Allotment details
        st.subheader("Allotment Details")
        col5, col6 = st.columns(2)
        with col5:
            allotment_no = form_manager.text_input(
                "Allotment No", 
                "bill_form", 
                "allotment_no"
            )
            allotment_date = form_manager.date_input(
                "Allotment Date", 
                "bill_form", 
                "allotment_date"
            )
            allotment_amount = form_manager.number_input(
                "Allotment Amount", 
                "bill_form", 
                "allotment_amount", 
                min_value=0
            )
            
        with col6:
            ts_no = form_manager.text_input(
                "TS No", 
                "bill_form", 
                "ts_no"
            )
            ts_date = form_manager.date_input(
                "TS Date", 
                "bill_form", 
                "ts_date"
            )
            ts_amount = form_manager.number_input(
                "TS Amount", 
                "bill_form", 
                "ts_amount", 
                min_value=0
            )
            
        # Submit button
        if form_manager.form_submit_button("bill_form", "Generate Bill"):
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
                "created_at": datetime.datetime.now().isoformat()
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
