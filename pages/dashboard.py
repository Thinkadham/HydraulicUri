import streamlit as st
import pandas as pd
from utils.db import get_contractors, get_works, get_bills

def show_dashboard():
    st.header("Dashboard Overview")
    
    # Stats columns
    col1, col2, col3 = st.columns(3)
    with col1:
        try:
            contractors = get_contractors() or []
            st.metric("Total Contractors", len(contractors))
        except Exception as e:
            st.error(f"Error loading contractors: {str(e)}")
            st.metric("Total Contractors", "N/A")
    
    with col2:
        try:
            works = get_works() or []
            st.metric("Active Works", len(works))
        except Exception as e:
            st.error(f"Error loading works: {str(e)}")
            st.metric("Active Works", "N/A")
    
    with col3:
        try:
            bills = get_bills() or []
            pending = len([b for b in bills if b.get("status") == "Pending"])
            st.metric("Pending Bills", pending)
        except Exception as e:
            st.error(f"Error loading bills: {str(e)}")
            st.metric("Pending Bills", "N/A")
    
    st.markdown("---")
    
    # Recent bills table
    st.subheader("Recent Bills")
    try:
        if bills:
            df = pd.DataFrame(bills)[:5]  # Show last 5 bills
            columns_to_show = ["bill_no", "payee", "work", "amount", "status"]
            # Only show columns that exist in the data
            available_columns = [col for col in columns_to_show if col in df.columns]
            st.dataframe(
                df[available_columns], 
                use_container_width=True,
                hide_index=True,
                column_config={
                    "amount": st.column_config.NumberColumn(format="₹%.2f")
                }
            )
        else:
            st.info("No bills found")
    except Exception as e:
        st.error(f"Error displaying bills: {str(e)}")
    
    st.markdown("---")
    st.caption("Auto Payment System v2.0.1")

# Run the function
show_dashboard()
