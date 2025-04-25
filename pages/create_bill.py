import streamlit as st
import datetime
from utils.db import get_contractors, get_works, insert_bill, update_work_expenditure
from utils.helpers import amount_in_words, calculate_deductions
from utils.form_manager import FormManager

def create_new_bill():
    form_manager = FormManager("create_bill")
    
    st.header("📝 Create New Bill")
    
    try:
        contractors = get_contractors()
        works = get_works()
        
        if not contractors or not works:
            st.error("Failed to load required data from database")
            return
            
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return

    # Main form
    with form_manager.form("bill_form", clear_on_submit=True):
        # Payee Section
        st.subheader("🧑 Payee Information")
        payee = form_manager.selectbox(
            "Select Payee*", 
            "bill_form", 
            "payee", 
            options=[c["name"] for c in contractors]
        )
        
        payee_data = next((c for c in contractors if c["name"] == payee), None)
        if not payee_data:
            st.error("Selected payee data not found")
            st.stop()
            
        col1, col2 = st.columns(2)
        with col1:
            form_manager.text_input("S/O", "bill_form", "so", 
                                 value=payee_data.get("parentage", ""),
                                 disabled=True)
            form_manager.text_input("Class", "bill_form", "class",
                                 value=payee_data.get("class", ""),
                                 disabled=True)
            
        with col2:
            form_manager.text_input("PAN", "bill_form", "pan",
                                 value=payee_data.get("pan", ""),
                                 disabled=True)
            form_manager.text_input("Account No*", "bill_form", "account_no",
                                 value=payee_data.get("account_no", ""),
                                 disabled=True)

        # Bill Details
        st.subheader("📄 Bill Details")
        bill_type = form_manager.selectbox(
            "Bill Type*", 
            "bill_form", 
            "bill_type", 
            options=["Plan", "Non Plan"]
        )

        major_heads = sorted(list(set(w["mh"] for w in works)))
        major_head = form_manager.selectbox(
            "Major Head*", 
            "bill_form", 
            "major_head", 
            options=major_heads
        )
        
        schemes = sorted(list(set(w["scheme"] for w in works if w["mh"] == major_head)))
        scheme = form_manager.selectbox(
            "Scheme*", 
            "bill_form", 
            "scheme", 
            options=schemes
        )
        
        filtered_works = [w for w in works if w["mh"] == major_head and w["scheme"] == scheme]
        work = form_manager.selectbox(
            "Work/Particulars*", 
            "bill_form", 
            "work", 
            options=[w["work_name"] for w in filtered_works]
        )
        
        work_data = next((w for w in filtered_works if w["work_name"] == work), None)
        if not work_data:
            st.error("Selected work data not found")
            st.stop()

        # Financial Section
        st.subheader("💰 Financial Details")
        col3, col4 = st.columns(2)
        
        with col3:
            billed_amount = form_manager.number_input(
                "Billed Amount (₹)*", 
                "bill_form", 
                "billed_amount", 
                min_value=0.0,
                step=0.01
            )
            deduct_payments = form_manager.number_input(
                "Deductions (₹)", 
                "bill_form", 
                "deduct_payments", 
                min_value=0.0,
                value=0.0,
                step=0.01
            )
            payable = billed_amount - deduct_payments
            form_manager.text_input(
                "Net Payable (₹)", 
                "bill_form", 
                "payable", 
                value=f"{payable:,.2f}",
                disabled=True
            )
            
        with col4:
            income_tax_percent = form_manager.number_input(
                "Income Tax (%)*", 
                "bill_form", 
                "income_tax_percent", 
                min_value=0.0, 
                max_value=100.0, 
                value=2.24,
                step=0.01
            )
            deposit_percent = form_manager.number_input(
                "Deposit (%)*", 
                "bill_form", 
                "deposit_percent", 
                min_value=0.0, 
                max_value=100.0, 
                value=10.0,
                step=0.01
            )
            cess_percent = form_manager.number_input(
                "Cess (%)", 
                "bill_form", 
                "cess_percent", 
                min_value=0.0, 
                max_value=100.0, 
                value=1.0,
                step=0.01
            )

        # Additional Details
        st.subheader("📝 Additional Information")
        form_manager.text_area(
            "Nomenclature", 
            "bill_form", 
            "nomenclature", 
            value=work_data.get("nomenclature", ""),
            height=100
        )
        
        submitted = form_manager.form_submit_button("bill_form", "💾 Generate Bill")
        
        if submitted:
            # [Keep your existing submission logic here]
            pass

if __name__ == "__main__":
    create_new_bill()
