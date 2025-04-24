import streamlit as st
import pandas as pd
from utils.db import get_contractors, get_works, get_bills

def show_dashboard():
    st.header("Dashboard Overview")
    
    # Stats columns
    col1, col2, col3 = st.columns(3)
    with col1:
        contractors = get_contractors() or []
        st.metric("Total Contractors", len(contractors))
    
    with col2:
        works = get_works() or []
        st.metric("Active Works", len(works))
    
    with col3:
        bills = get_bills() or []
        pending = len([b for b in bills if b.get("status") == "Pending"])
        st.metric("Pending Bills", pending)
    
    st.markdown("---")
    
    # Recent bills table
    st.subheader("Recent Bills")
    if bills:
        df = pd.DataFrame(bills)[:5]  # Show last 5 bills
        columns_to_show = ["bill_no", "payee", "work", "amount", "status"]
        # Only show columns that exist in the data
        available_columns = [col for col in columns_to_show if col in df.columns]
        st.dataframe(df[available_columns], use_container_width=True)
    else:
        st.info("No bills found")
    
    st.markdown("---")
    st.caption("Auto Payment System v2.0.1")
