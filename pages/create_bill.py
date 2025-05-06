import streamlit as st
import datetime
from utils.db import (
    get_contractors, get_works, insert_bill, update_work_expenditure,
    get_budget_np, get_budget_plan, get_work_details_from_works_plan # Import new functions
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
    st.markdown("---") # Border above Bill Details
    st.subheader("📄 Bill Details")

    # Two columns for Bill Type, Major Head, Scheme/Detailed Head, Work/Particulars
    col_bill_details_1, col_bill_details_2 = st.columns(2)

    with col_bill_details_1:
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

    with col_bill_details_2:
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
                    # Corrected: Use 'Workcode' to match the new column name
                    item_work = item.get('Workcode')

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
            "Workcode*",
            options=work_options,
            # Set index=0 to default to "N/A" or the first work if available
            index=0 if work_options else 0, # Handle empty options list
            key="work_select", # Unique key
            disabled=work_disabled # Disable based on bill_type
        )

        # Assign the selected value based on whether it's disabled
        work = work_selected_value if work_disabled else temp_work_selection

    # 4.5. NEW: If Bill Type is Plan and a Workcode is selected, fetch details from works_plan
    # and let user select a specific nomenclature.
    works_plan_details_list = []
    selected_nomenclature_detail = None # This will hold the full dict for the chosen nomenclature
    nomenclature_options = ["No nomenclatures found"]
    nomenclature_disabled = True

    if bill_type == "Plan" and not work_disabled and work and work != "No works found in Budget Plan":
        works_plan_details_list = get_work_details_from_works_plan(work) # 'work' is the Workcode

        if works_plan_details_list:
            temp_nomenclature_options = sorted(list(set(
                item.get('Nomenclature').strip() for item in works_plan_details_list if item.get('Nomenclature') and isinstance(item.get('Nomenclature'), str) and item.get('Nomenclature').strip()
            )))
            if temp_nomenclature_options:
                nomenclature_options = temp_nomenclature_options
                nomenclature_disabled = False
            else:
                nomenclature_options = ["No nomenclatures found for this Workcode"]
        else:
            nomenclature_options = ["No details found in works_plan for this Workcode"]

    # Nomenclature selectbox across two columns
    selected_nomenclature_str = st.selectbox(
        "Select Nomenclature*",
        options=nomenclature_options,
        key="nomenclature_select",
        disabled=nomenclature_disabled or bill_type != "Plan" # Also disable if not Plan bill
    )

    # Find the full detail record for the selected nomenclature string
    if not nomenclature_disabled and selected_nomenclature_str not in ["No nomenclatures found", "No nomenclatures found for this Workcode", "No details found in works_plan for this Workcode"]:
        for detail in works_plan_details_list:
            if detail.get('Nomenclature') == selected_nomenclature_str: # Use 'Nomenclature' here too
                selected_nomenclature_detail = detail
                break

    # --- Display Works Plan Metrics (NEW SECTION) ---
    if bill_type == "Plan" and selected_nomenclature_detail:
        st.markdown("---") # Border above Work Details
        st.subheader("📋 Work Details") # Renamed subheader
        col_wp_1, col_wp_2, col_wp_3 = st.columns(3)

        with col_wp_1:
            st.markdown(f'<span style="color: blue;">Allot No: {selected_nomenclature_detail.get("Allot No", "N/A")}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="color: green;">AAA No: {selected_nomenclature_detail.get("AAA No", "N/A")}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="color: red;">TS No: {selected_nomenclature_detail.get("TS No", "N/A")}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="color: blue;">Agr No: {selected_nomenclature_detail.get("Agr No", "N/A")}</span>', unsafe_allow_html=True)

        with col_wp_2:
            st.markdown(f'<span style="color: green;">Allot Dt: {selected_nomenclature_detail.get("Allot Dt", "N/A")}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="color: red;">AAA Dt: {selected_nomenclature_detail.get("AAA Dt", "N/A")}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="color: blue;">TS Dt: {selected_nomenclature_detail.get("TS Dt", "N/A")}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="color: green;">LOI No: {selected_nomenclature_detail.get("LOI No", "N/A")}</span>', unsafe_allow_html=True)


        with col_wp_3:
            # Format amount with commas and two decimal places if it's a number
            allot_amt = selected_nomenclature_detail.get("Allot Amt")
            allot_amt_display = f"₹{allot_amt:,.2f}" if isinstance(allot_amt, (int, float)) else "N/A"
            st.markdown(f'<span style="color: red;">Allot Amt: {allot_amt_display}</span>', unsafe_allow_html=True)

            aaa_amt = selected_nomenclature_detail.get("AAA Amt")
            aaa_amt_display = f"₹{aaa_amt:,.2f}" if isinstance(aaa_amt, (int, float)) else "N/A"
            st.markdown(f'<span style="color: blue;">AAA Amt: {aaa_amt_display}</span>', unsafe_allow_html=True)

            ts_amt = selected_nomenclature_detail.get("TS Amt")
            ts_amt_display = f"₹{ts_amt:,.2f}" if isinstance(ts_amt, (int, float)) else "N/A"
            st.markdown(f'<span style="color: green;">TS Amt: {ts_amt_display}</span>', unsafe_allow_html=True)

            st.markdown(f'<span style="color: red;">TOC: {selected_nomenclature_detail.get("TOC", "N/A")}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="color: blue;">DOS: {selected_nomenclature_detail.get("DOS", "N/A")}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="color: green;">DOC: {selected_nomenclature_detail.get("DOC", "N/A")}</span>', unsafe_allow_html=True)

    # Determine the selected budget entry based on bill type, major head, and scheme
    selected_budget_entry = None
    if major_head and scheme:
        if bill_type == "Plan":
            # For Plan, match Major Head and Scheme
            selected_budget_entry = next((item for item in budget_plan if
                                           item.get(major_head_column) == major_head and
                                           item.get(scheme_column) == scheme), None)
        elif bill_type == "Non Plan":
            # For Non Plan, match Major Head and Detailed Head
             selected_budget_entry = next((item for item in budget_np if
                                           item.get(major_head_column) == major_head and
                                           item.get(scheme_column) == scheme), None)


    # Display Total Budget from the selected budget entry (Moved below Work Details)
    st.markdown("---") # Border above Budget Details
    st.subheader("📊 Budget Details")

    if selected_budget_entry and selected_budget_entry.get("Amount") is not None:
        st.metric(label="Total Budget", value=f"₹{selected_budget_entry['Amount']:,.2f}")

    # Separate check for warning message
    if not selected_budget_entry and major_head and scheme: # Only show warning if MH and Scheme are selected but no budget found
         # Refine warning based on bill type and work selection
         if bill_type == "Plan" and work and work != "No works found in Budget Plan":
             st.warning(f"Budget details not found for the selected Major Head, Scheme, and Work: '{work}'.")
         elif bill_type == "Non Plan":
             st.warning("Budget details not found for the selected Major Head and Detailed Head.")
         else: # Generic warning if MH/Scheme selected but no specific work selected or found
             st.warning("Budget details not found for the selected Major Head and Scheme/Detailed Head.")


    # 5. Get Work Data based on final selection
    # For "Plan" bills, work_data is now `selected_nomenclature_detail` from works_plan
    # For "Non Plan" bills, work_data remains None or is not used.
    work_data = None
    if bill_type == "Plan":
        work_data = selected_nomenclature_detail # This is the chosen item from works_plan
        if not work_data and work and work != "No works found in Budget Plan" and selected_nomenclature_str not in ["No nomenclatures found", "No nomenclatures found for this Workcode", "No details found in works_plan for this Workcode"]:
            st.warning(f"Details for selected nomenclature '{selected_nomenclature_str}' under Workcode '{work}' not found. Bill generation might fail.")
        elif work == "No works found in Budget Plan":
            st.info("No specific Workcodes found in Budget Plan for the selected Major Head and Scheme.")
        elif selected_nomenclature_str in ["No nomenclatures found", "No nomenclatures found for this Workcode", "No details found in works_plan for this Workcode"] and work and work != "No works found in Budget Plan":
             st.info(f"No nomenclatures available or found for Workcode '{work}'.")

    # If it's a Non-Plan bill, or if work_data couldn't be found for a Plan bill,
    # we might fall back to the old 'works' table logic if that's desired,
    # or simply proceed with work_data as None.
    # For now, the request is to use works_plan for Plan bills.

    # --- Payee Information (OUTSIDE form for dynamic update) ---
    st.markdown("---") # Border above Payee Information
    st.subheader("🧑 Payee Information")
    payee = st.selectbox(
        "Select Payee*",
        options=[c["name"] for c in contractors],
        help="Select contractor from the list",
        key="payee_select" # Added unique key
    )

    # Get payee details
    payee_data = next((c for c in contractors if c["name"] == payee), None)
    if not payee_data:
        st.error("Selected payee data not found")
        st.stop()

    # Display payee info in columns
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**S/O:** {payee_data.get('parentage', 'N/A')}")
        st.markdown(f"**R/o:** {payee_data.get('resident', 'N/A')}")
        st.markdown(f"**Class:** {payee_data.get('class', 'N/A')}")
        st.markdown(f"**Reg No:** {payee_data.get('registration', 'N/A')}")

    with col2:
        st.markdown(f"**PAN:** {payee_data.get('pan', 'N/A')}")
        st.markdown(f"**GSTIN:** {payee_data.get('gstin', 'N/A')}")
        st.markdown(f"**Account No:** {payee_data.get('account_no', 'N/A')}")


    # --- Main form for Financials and Submission ---
    with st.form(key="create_bill_form", clear_on_submit=True):
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

        # ========== Measurement Book Details ==========
        st.subheader("� Measurement Book")
        
        mbook_no = st.text_input(
            "M.Book No",
            key="mbook_no"
        )
        
        page_no = st.text_input(
            "Page No",
            key="page_no"
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
            if bill_type == "Plan" and work and work != "No works found in Budget Plan" and not work_data : # work_data is selected_nomenclature_detail
                 missing_fields.append("Valid Nomenclature selection from works_plan (selection mismatch or not found)")
            elif bill_type == "Plan" and (not work or work == "No works found in Budget Plan"):
                 missing_fields.append("Valid Work/Particulars (Workcode from budget_plan)")


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

                # Expenditure update logic is being deferred as per user request.
                # A new table for expenditure will be created later.
                if result:
                    if bill_type == "Plan" and work_data:
                        st.success("✅ Bill created successfully! (Expenditure update deferred)")
                        st.balloons()
                    elif bill_type == "Plan" and not work_data:
                        st.warning("✅ Bill created, but work details for expenditure were not fully resolved. (Expenditure update deferred)")
                        st.balloons()
                    elif bill_type == "Non Plan": # For Non Plan, work_data is typically not used for expenditure in this way
                        st.success("✅ Bill created successfully!")
                        st.balloons()
                    # Consider if work_data is relevant for Non Plan bills for expenditure
                    # else if result and work_data: # Original condition for other cases if any
                    #    st.success("✅ Bill created successfully! (Expenditure update deferred for this case too)")
                    #    st.balloons()

                else: # insert_bill failed
                    st.error("❌ Failed to save bill to database.")
                    st.rerun()
            
            except Exception as e:
                st.error(f"❌ Error processing bill: {str(e)}")

if __name__ == "__main__":
    create_new_bill()
