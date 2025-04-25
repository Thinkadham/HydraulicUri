import streamlit as st
import datetime
from utils.db import get_contractors, get_works, insert_bill, update_work_expenditure
from utils.helpers import amount_in_words, calculate_deductions
from utils.form_manager import FormManager

def create_new_bill():
    # Initialize FormManager
    form_manager = FormManager("create_bill")
    
    st.header("📝 Create New Bill")
    
    # Load data with error handling
    try:
        contractors = get_contractors()
        works = get_works()
        
        if not contractors or not works:
            st.error("Failed to load required data from database")
            return
            
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return

    # Main form - using consistent form key
    with form_manager.form("bill_form", clear_on_submit=True):
        # ========== Payee Section ==========
        st.subheader("🧑 Payee Information")
        payee = st.selectbox(
            "Select Payee*", 
            options=[c["name"] for c in contractors],
            help="Select contractor from the list"
        )
        
        # Get payee details
        payee_data = next((c for c in contractors if c["name"] == payee), None)
        if not payee_data:
            st.error("Selected payee data not found")
            st.stop()
            
        # Display payee info in columns
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("S/O", 
                         value=payee_data.get("parentage", ""),
                         disabled=True)
            st.text_input("Class", 
                         value=payee_data.get("class", ""),
                         disabled=True)
            
        with col2:
            st.text_input("PAN",
                         value=payee_data.get("pan", ""),
                         disabled=True)
            st.text_input("Account No*",
                         value=payee_data.get("account_no", ""),
                         disabled=True)

        # ========== Bill Details Section ==========
        st.subheader("📄 Bill Details")
        bill_type = st.selectbox(
            "Bill Type*", 
            options=["Plan", "Non Plan"],
            index=0
        )

        # Dynamic work filters
        major_heads = sorted(list(set(w["mh"] for w in works)))
        major_head = st.selectbox(
            "Major Head*", 
            options=major_heads
        )
        
        schemes = sorted(list(set(w["scheme"] for w in works if w["mh"] == major_head)))
        scheme = st.selectbox(
            "Scheme*", 
            options=schemes
        )
        
        filtered_works = [w for w in works if w["mh"] == major_head and w["scheme"] == scheme]
        work = st.selectbox(
            "Work/Particulars*", 
            options=[w["work_name"] for w in filtered_works]
        )
        
        work_data = next((w for w in filtered_works if w["work_name"] == work), None)
        if not work_data:
            st.error("Selected work data not found")
            st.stop()

        # ========== Financial Section ==========
        st.subheader("💰 Financial Details")
        col3, col4 = st.columns(2)
        
        with col3:
            billed_amount = st.number_input(
                "Billed Amount (₹)*", 
                min_value=0.0,
                step=0.01,
                format="%.2f"
            )
            deduct_payments = st.number_input(
                "Deductions (₹)", 
                min_value=0.0,
                value=0.0,
                step=0.01,
                format="%.2f"
            )
            payable = billed_amount - deduct_payments
            st.text_input(
                "Net Payable (₹)", 
                value=f"{payable:,.2f}",
                disabled=True
            )
            
        with col4:
            income_tax_percent = st.number_input(
                "Income Tax (%)*", 
                min_value=0.0, 
                max_value=100.0, 
                value=2.24,
                step=0.01
            )
            deposit_percent = st.number_input(
                "Deposit (%)*", 
                min_value=0.0, 
                max_value=100.0, 
                value=10.0,
                step=0.01
            )
            cess_percent = st.number_input(
                "Cess (%)", 
                min_value=0.0, 
                max_value=100.0, 
                value=1.0,
                step=0.01
            )

        # ========== Additional Details ==========
        st.subheader("📝 Additional Information")
        st.text_area(
            "Nomenclature", 
            value=work_data.get("nomenclature", ""),
            height=100
        )
        
        # ========== Form Submission ==========
        submitted = st.form_submit_button("💾 Generate Bill")
        
        if submitted:
            # Validate required fields
            required_fields = {
                "Payee": payee,
                "Account No": payee_data.get("account_no"),
                "Bill Type": bill_type,
                "Work": work,
                "Billed Amount": billed_amount
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value]
            if missing_fields:
                st.error(f"❌ Missing required fields: {', '.join(missing_fields)}")
                st.stop()

            # Process bill
            try:
                # Calculate deductions
                deductions = calculate_deductions(
                    payable, income_tax_percent, deposit_percent, cess_percent
                )
                
                # Prepare bill data
                bill_data = {
                    "payee": payee,
                    "payee_id": payee_data.get("id"),
                    "work": work,
                    "work_id": work_data.get("id"),
                    "bill_type": bill_type,
                    "major_head": major_head,
                    "scheme": scheme,
                    "billed_amount": billed_amount,
                    "deduct_payments": deduct_payments,
                    "payable": payable,
                    "income_tax_amount": deductions[0],
                    "deposit_amount": deductions[1],
                    "cess_amount": deductions[2],
                    "total_deduction": deductions[3],
                    "net_amount": deductions[4],
                    "amount_in_words": amount_in_words(deductions[4]),
                    "status": "Pending",
                    "created_at": datetime.datetime.now().isoformat(),
                    "nomenclature": work_data.get("nomenclature", "")
                }
                
                # Save to database
                result = insert_bill(bill_data)
                if result:
                    # Update work expenditure
                    new_expenditure = work_data.get("expenditure", 0) + billed_amount
                    update_work_expenditure(work_data["id"], new_expenditure)
                    
                    st.success("✅ Bill created successfully!")
                    st.balloons()
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Error processing bill: {str(e)}")

if __name__ == "__main__":
    create_new_bill()
