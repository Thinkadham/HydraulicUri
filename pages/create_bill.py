import streamlit as st
import datetime
from utils.db import (
    get_contractors, get_works, insert_bill, update_work_expenditure,
    get_budget_np, get_budget_plan # Import new functions
)
from utils.helpers import amount_in_words, calculate_deductions

def create_new_bill():
    st.header("📝 Create New Bill")
    
    # Load data with error handling
    try:
        contractors = get_contractors()
        works = get_works()
        budget_np = get_budget_np()
        budget_plan = get_budget_plan()

        # Check if essential data loaded
        if not contractors:
            st.error("Failed to load Contractors data from database.")
            return
        if not works:
            st.error("Failed to load Works data from database.")
            # Allow proceeding if budget data is available, maybe works are not needed for all steps
            # return # Or decide if works are absolutely essential upfront

        # Check budget data (optional, depending on workflow)
        if not budget_np:
            st.warning("Could not load Non-Plan Budget data.")
            budget_np = [] # Ensure it's an empty list if loading failed
        if not budget_plan:
            st.warning("Could not load Plan Budget data.")
            budget_plan = [] # Ensure it's an empty list if loading failed

    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return

    # Callbacks are no longer needed as widgets are outside the form
    # def reset_major_head_scheme_work(): ...
    # def reset_scheme_work(): ...

    # --- Define Dependent Selectboxes OUTSIDE the form ---
    st.subheader("📄 Bill Details")
    bill_type = st.selectbox(
        "Bill Type*",
        options=["Plan", "Non Plan"],
        index=0,
        key="bill_type_select" # Use a unique key
        # Removed on_change callback
    )

    # --- Determine budget source and populate dependent dropdowns OUTSIDE form ---

    # 1. Determine Source Budget Table based on Bill Type
    source_budget_table = []
    major_head_column = 'Major Head' # Assuming same name in both tables
    scheme_column = None
    scheme_label = "Scheme/Detailed Head*"

    if bill_type == "Plan":
        source_budget_table = budget_plan
        scheme_column = 'Scheme'
        scheme_label = "Scheme*"
    elif bill_type == "Non Plan":
        source_budget_table = budget_np
        scheme_column = 'Detailed Head'
        scheme_label = "Detailed Head*"

    # 2. Populate Major Heads based on the determined source table
    major_heads_options = []
    if source_budget_table:
        major_heads_options = sorted(list(set(item.get(major_head_column) for item in source_budget_table if item.get(major_head_column))))

    major_head = st.selectbox(
        "Major Head*",
        options=major_heads_options, # Options filtered by Bill Type
        key="major_head_select", # Unique key
        # Removed on_change callback
        help="Select the Major Head corresponding to the budget source."
    )

    # 3. Populate Scheme/Detailed Head based on selected Major Head
    scheme_options = []
    if major_head and source_budget_table and scheme_column:
        scheme_options = sorted(list(set(item.get(scheme_column) for item in source_budget_table if item.get(major_head_column) == major_head and item.get(scheme_column))))

    scheme = st.selectbox(
        scheme_label, # Dynamic label
        options=scheme_options, # Options filtered by Major Head
        key="scheme_select", # Unique key
        help=f"Select the {scheme_label.replace('*','')} under the chosen Major Head."
    )

    # 4. Populate Work/Particulars based on Bill Type, Major Head, and Scheme/Detailed Head
    work_options = []
    work_disabled = False
    work_selected_value = None # Store the actual selected value

    if bill_type == "Plan":
        work_disabled = False # Enable for Plan
        if major_head and scheme and budget_plan:
            # Filter budget_plan for matching MH and Scheme, then get unique 'work' values
            # Filter budget_plan for matching MH and Scheme, then get unique 'work' values
            # Filter budget_plan for matching MH and Scheme, then get unique 'work' values
            # Filter budget_plan for matching MH and Scheme, then get unique 'work' values
            plan_works = set()

            for item in budget_plan:
                item_major_head = item.get(major_head_column)
                item_scheme = item.get(scheme_column)
                # Corrected: Use 'Work' with a capital 'W' to match the dictionary key
                item_work = item.get('Work')

                # Perform case-insensitive comparison and strip spaces
                major_head_match = (item_major_head and major_head and
                                    str(item_major_head).strip().lower() == str(major_head).strip().lower())
                scheme_match = (item_scheme and scheme and
                                str(item_scheme).strip().lower() == str(scheme).strip().lower())

                # Updated condition to use the variable with the correct work value
                if (major_head_match and scheme_match and
                    item_work and isinstance(item_work, str) and item_work.strip()): # Check if 'work' key exists, is a string, and has a non-empty value after stripping
                    plan_works.add(item_work.strip()) # Add stripped work value

            work_options = sorted(list(plan_works))

        # If no options found, provide a placeholder maybe?
        if not work_options:
            work_options = ["No works found in Budget Plan"]

            # Consider disabling if no options? Or let user see the message.
            # work_disabled = True

    elif bill_type == "Non Plan":
        # Disable work selection for Non Plan
        work_options = ["N/A"]
        work_disabled = True
        work_selected_value = "N/A" # Default value when disabled


    # Use a temporary variable for the selectbox selection
    temp_work_selection = st.selectbox(
        "Work/Particulars*",
        options=work_options,
        # Set index=0 to default to "N/A" or the first work if available
        index=0 if work_options else 0, # Handle empty options list
        key="work_select", # Unique key
        disabled=work_disabled # Disable based on bill_type
    )

    # Assign the selected value based on whether it's disabled
    work = work_selected_value if work_disabled else temp_work_selection

    # Find and display the budget amount from budget_plan or budget_np
    selected_budget_entry = None
    if major_head and scheme and source_budget_table:
        for item in source_budget_table:
            item_major_head = item.get(major_head_column)
            item_scheme = item.get(scheme_column)

            major_head_match = (item_major_head and major_head and
                                str(item_major_head).strip().lower() == str(major_head).strip().lower())
            scheme_match = (item_scheme and scheme and
                            str(item_scheme).strip().lower() == str(scheme).strip().lower())

            if bill_type == "Plan":
                # For Plan, also match the 'Work'
                item_work = item.get('Work')
                work_match = (item_work and work and
                              str(item_work).strip().lower() == str(work).strip().lower())
                if major_head_match and scheme_match and work_match:
                    selected_budget_entry = item
                    break # Found the matching entry
            elif bill_type == "Non Plan":
                # For Non Plan, only match Major Head and Detailed Head
                if major_head_match and scheme_match:
                    selected_budget_entry = item
                    break # Found the matching entry


    # Display Total Budget from the selected budget entry
    if selected_budget_entry and selected_budget_entry.get("Amount") is not None:
        st.subheader("📊 Budget Details")
        st.metric(label="Total Budget", value=f"₹{selected_budget_entry['Amount']:,.2f}")
    elif major_head and scheme: # Only show warning if MH and Scheme are selected but no budget found
         # Refine warning based on bill type and work selection
         if bill_type == "Plan" and work and work != "No works found in Budget Plan":
             st.warning(f"Budget details not found for the selected Major Head, Scheme, and Work: '{work}'.")
         elif bill_type == "Non Plan":
             st.warning("Budget details not found for the selected Major Head and Detailed Head.")
         else: # Generic warning if MH/Scheme selected but no specific work selected or found
             st.warning("Budget details not found for the selected Major Head and Scheme/Detailed Head.")


    # 5. Get Work Data based on final selection (LOOKUP IN MAIN 'works' TABLE)
    # Only lookup if it's a Plan bill and a valid work was selected
    work_data = None
    if bill_type == "Plan" and not work_disabled and work and work != "No works found in Budget Plan" and works:
        # Find matching work in the main 'works' table by name, mh, and scheme
        # This assumes the 'work' value from budget_plan matches 'work_name' in the 'works' table
        matching_works = [
            w for w in works
            if w.get("mh") == major_head and \
               w.get("scheme") == scheme and \
               w.get("work_name") == work
        ]
        if matching_works:
            work_data = matching_works[0] # Assume first match

    # Display warnings/info outside form if needed
    if bill_type == "Plan" and work and work != "No works found in Budget Plan" and not work_data:
         st.warning(f"Details for selected work '{work}' not found in the main Works table for the current Major Head/Scheme. Bill generation might fail or skip expenditure update.")
    elif bill_type == "Plan" and work == "No works found in Budget Plan":
         st.info("No specific works found in Budget Plan for the selected Major Head and Scheme.")
    # No specific message needed for Non Plan here, handled by disabling


    # --- Main form for Payee, Financials, and Submission ---


    # --- Main form for Payee, Financials, and Submission ---
    # Removed stray key and parenthesis from previous edit here

    with st.form(key="create_bill_form", clear_on_submit=True):
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
                        key="payee_so",
                        disabled=True)
            st.text_input("Class", 
                        value=payee_data.get("class", ""),
                        key="payee_class",
                        disabled=True)
            
        with col2:
            st.text_input("PAN",
                        value=payee_data.get("pan", ""),
                        key="payee_pan",
                        disabled=True)
            st.text_input("Account No*",
                        value=payee_data.get("account_no", ""),
                        key="payee_account",
            disabled=True)

        # Bill Details selectboxes are now OUTSIDE the form.

        # --- Financial Section (INSIDE form) ---
        st.subheader("💰 Financial Details")
        col3, col4 = st.columns(2)
        
        with col3:
            billed_amount = st.number_input(
                "Billed Amount (₹)*", 
                min_value=0.0,
                step=0.01,
                format="%.2f",
                key="billed_amount"
            )
            deduct_payments = st.number_input(
                "Deductions (₹)", 
                min_value=0.0,
                value=0.0,
                step=0.01,
                format="%.2f",
                key="deductions"
            )
            payable = billed_amount - deduct_payments
            st.text_input(
                "Net Payable (₹)", 
                value=f"{payable:,.2f}",
                key="net_payable",
                disabled=True
            )
            
        with col4:
            income_tax_percent = st.number_input(
                "Income Tax (%)*", 
                min_value=0.0, 
                max_value=100.0, 
                value=2.24,
                step=0.01,
                key="income_tax"
            )
            deposit_percent = st.number_input(
                "Deposit (%)*", 
                min_value=0.0, 
                max_value=100.0, 
                value=10.0,
                step=0.01,
                key="deposit"
            )
            cess_percent = st.number_input(
                "Cess (%)", 
                min_value=0.0, 
                max_value=100.0, 
                value=1.0,
                step=0.01,
                key="cess"
            )

        # ========== Additional Details ==========
        st.subheader("📝 Additional Information")
        # Handle potential None for work_data
        nomenclature_value = work_data.get("nomenclature", "") if work_data else ""
        st.text_area(
            "Nomenclature",
            value=nomenclature_value,
            height=100,
            key="nomenclature",
            # Optionally disable if no work is selected/found
            disabled=not work_data
        )

        # ========== Form Submission ==========
        submitted = st.form_submit_button("💾 Generate Bill")

        if submitted:
            # Validate required fields using values from widgets outside and inside the form
            # bill_type, major_head, scheme, work are defined outside the form
            # payee, billed_amount etc are defined inside the form
            required_fields = {
                "Payee": payee, # From form
                "Account No": payee_data.get("account_no"), # From form data lookup
                "Bill Type": bill_type, # From outside form
                "Major Head": major_head, # From outside form
                "Scheme/Detailed Head": scheme, # From outside form
                "Work/Particulars": work, # Check if a work was selected
                "Billed Amount": billed_amount
            }

            missing_fields = [field for field, value in required_fields.items() if not value]

            # Add specific check for work_data consistency using the data derived outside the form
            if work and not work_data:
                 missing_fields.append("Valid Work/Particulars (selection mismatch or not found)")

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
                    # Ensure work_data exists before accessing id
                    "work_id": work_data.get("id") if work_data else None,
                    "bill_type": bill_type,
                    "major_head": major_head,
                    "scheme": scheme, # This stores the selected Scheme or Detailed Head value
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
                    # Ensure work_data exists before accessing nomenclature
                    "nomenclature": work_data.get("nomenclature", "") if work_data else ""
                }

                # Save to database (ensure work_id is handled if None by the DB/API)
                result = insert_bill(bill_data)
                if result and work_data: # Only update expenditure if bill saved and work_data exists
                    # Update work expenditure
                    # Ensure expenditure exists and is a number, default to 0
                    current_expenditure = work_data.get("expenditure", 0)
                    if not isinstance(current_expenditure, (int, float)):
                        current_expenditure = 0 # Default if invalid type

                    new_expenditure = current_expenditure + billed_amount
                    update_work_expenditure(work_data["id"], new_expenditure)

                    st.success("✅ Bill created successfully!")
                    st.balloons()
                elif result: # Bill saved but work_data was missing (shouldn't happen with validation)
                     st.warning("✅ Bill created, but could not update work expenditure (work details missing).")
                     st.balloons()
                else: # insert_bill failed
                     st.error("❌ Failed to save bill to database.")
                     st.rerun() # Correctly indented under else

            except Exception as e:
                st.error(f"❌ Error processing bill: {str(e)}")

if __name__ == "__main__":
    create_new_bill()
