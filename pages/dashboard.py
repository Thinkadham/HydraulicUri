import streamlit as st
import pandas as pd
from utils.db import get_contractors, get_works, get_bills


def show_dashboard():
    st.header("Dashboard")
    
    try:
        # Fetch data from Supabase
        contractors = get_contractors() or []
        works = get_works() or []
        bills = get_bills() or []
        
        # Stats columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Contractors", len(contractors))
        with col2:
            st.metric("Active Works", len(works))
        with col3:
            pending_bills = len([b for b in bills if isinstance(b, dict) and b.get("status") == "Pending"])
            st.metric("Pending Bills", pending_bills)
            
        # Recent bills table
        st.subheader("Recent Bills")
        if bills:
            recent_bills = pd.DataFrame(bills)[:5]  # Show last 5 bills
            
            # Define which columns we want to show and their fallbacks
            display_columns = []
            column_mapping = {
                'bill_no': 'Bill No',
                'payee': 'Payee',
                'work': 'Work',
                'amount': 'Amount',
                'payable': 'Amount',  # Fallback if 'amount' doesn't exist
                'status': 'Status'
            }
            
            # Find which columns actually exist in the data
            available_columns = [col for col in column_mapping.keys() if col in recent_bills.columns]
            
            if not available_columns:
                st.warning("No bill data available to display")
            else:
                # Create display dataframe with available columns
                display_df = recent_bills[available_columns]
                # Rename columns for display
                display_df = display_df.rename(columns=column_mapping)
                st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No bills found in the database")
        
        # Budget utilization chart
        st.subheader("Budget Utilization")
        if works:
            works_df = pd.DataFrame(works)
            if not works_df.empty and 'scheme' in works_df.columns:
                try:
                    budget_data = works_df.groupby("scheme").agg({
                        "allotment_amount": "sum",
                        "expenditure": "sum"
                    }).reset_index()
                    budget_data.columns = ["Scheme", "Allocated", "Utilized"]
                    st.bar_chart(budget_data.set_index("Scheme"))
                except Exception as e:
                    st.error(f"Could not generate budget chart: {str(e)}")
            else:
                st.warning("Incomplete work data for budget visualization")
        else:
            st.info("No works data available for budget visualization")

    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")

# Run the function
show_dashboard()
