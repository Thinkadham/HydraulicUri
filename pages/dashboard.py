import streamlit as st
import pandas as pd
from utils.db import get_contractors, get_works, get_bills

def show_dashboard():
    st.header("Dashboard")
    
    # Fetch data from Supabase
    contractors = get_contractors()
    works = get_works()
    bills = get_bills()
    
    # Stats columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Contractors", len(contractors))
    with col2:
        st.metric("Active Works", len(works))
    with col3:
        pending_bills = len([b for b in bills if b.get("status") == "Pending"])
        st.metric("Pending Bills", pending_bills)
        
    # Recent bills table
    st.subheader("Recent Bills")
    recent_bills = pd.DataFrame(bills)[:5]  # Show last 5 bills
    st.dataframe(recent_bills[["bill_no", "payee", "work", "amount", "status"]], 
                use_container_width=True)
    
    # Budget utilization chart
    st.subheader("Budget Utilization")
    if works:
        budget_data = pd.DataFrame(works)
        if not budget_data.empty:
            budget_data = budget_data.groupby("scheme").agg({
                "allotment_amount": "sum",
                "expenditure": "sum"
            }).reset_index()
            budget_data.columns = ["Scheme", "Allocated", "Utilized"]
            st.bar_chart(budget_data.set_index("Scheme"))

show_dashboard()
