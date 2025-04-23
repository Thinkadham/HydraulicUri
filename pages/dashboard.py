import streamlit as st
import pandas as pd
from services import get_contractors, get_works, get_recent_bills

def show():
    st.header("Dashboard")
    
    try:
        # Fetch data
        contractors = get_contractors()
        works = get_works()
        bills = get_recent_bills()
        
        # Display metrics
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
        if bills:
            recent_bills = pd.DataFrame(bills)[:5]
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
                st.bar_chart(budget_data.set_index("scheme"))
                
    except Exception as e:
        st.error(f"Error loading dashboard data: {e}")
