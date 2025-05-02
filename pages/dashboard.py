import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import inspect
import os
import time
from utils.db import get_contractors, get_works, get_bills
from utils.comp_key import generate_component_key

# Cache data fetches
@st.cache_data(ttl=300)
def fetch_contractors():
    return get_contractors() or []

@st.cache_data(ttl=300)
def fetch_works():
    return get_works() or []

@st.cache_data(ttl=60)
def fetch_bills():
    return get_bills() or []

def show_dashboard():
    st.header("Dashboard Overview")
    
    # Generate unique refresh key
    refresh_key = generate_component_key(
        component_type="button",
        component_name="dashboard_refresh",
        extra_context=f"exec_{time.time_ns()}"
    )
    
      
    # Refresh button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.subheader("Key Metrics")
    with col2:
        if st.button(
            "🔄 Refresh Data",
            help="Reload all dashboard data",
            key=refresh_key,
            type="primary"
        ):
            st.cache_data.clear()
            st.rerun()
    
    # Metrics display
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        try:
            contractors = fetch_contractors()
            st.metric("Total Contractors", len(contractors))
        except Exception as e:
            st.error(f"Contractor data unavailable")
            st.metric("Total Contractors", "N/A")

    with metric_col2:
        try:
            works = fetch_works()
            st.metric("Active Works", len(works))
        except Exception as e:
            st.error(f"Works data unavailable")
            st.metric("Active Works", "N/A")

    with metric_col3:
        try:
            bills = fetch_bills()
            pending = len([b for b in bills if b.get("status") == "Pending"])
            st.metric("Pending Bills", pending)
        except Exception as e:
            st.error(f"Bills data unavailable")
            st.metric("Pending Bills", "N/A")

    st.markdown("---")
    
    # Date range filter
    st.subheader("Recent Bills")
    default_end = datetime.now()
    default_start = default_end - timedelta(days=30)
    
    date_col1, date_col2 = st.columns(2)
    with date_col1:
        start_date = st.date_input("From date", value=default_start)
    with date_col2:
        end_date = st.date_input("To date", value=default_end)
    
    # Visualization tabs
    tab1, tab2 = st.tabs(["Bills Table", "Expenditure Trends"])
    
    with tab1:
        try:
            bills = fetch_bills()
            if bills:
                filtered_bills = [
                    b for b in bills 
                    if start_date <= datetime.strptime(b.get('created_at', default_end.isoformat())[:10], "%Y-%m-%d").date() <= end_date
                ]
                
                if filtered_bills:
                    df = pd.DataFrame(filtered_bills).sort_values('created_at', ascending=False)
                    columns_to_show = ["bill_no", "payee", "work", "billed_amount", "status", "created_at"]
                    available_columns = [col for col in columns_to_show if col in df.columns]
                    
                    st.dataframe(
                        df[available_columns],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "billed_amount": st.column_config.NumberColumn(
                                "Amount",
                                format="₹%.2f"
                            ),
                            "created_at": st.column_config.DateColumn(
                                "Date",
                                format="DD-MM-YYYY"
                            )
                        }
                    )
                else:
                    st.info("No bills found in selected date range")
            else:
                st.info("No bills found in database")
        except Exception as e:
            st.error(f"Error displaying bills: {str(e)}")

    with tab2:
        try:
            bills = fetch_bills()
            if bills:
                df = pd.DataFrame(bills)
                df['created_at'] = pd.to_datetime(df['created_at']).dt.date
                df = df[df['created_at'].between(start_date, end_date)]
                
                if not df.empty:
                    daily_totals = df.groupby('created_at')['billed_amount'].sum().reset_index()
                    st.area_chart(
                        daily_totals.set_index('created_at'),
                        use_container_width=True,
                        color="#4CAF50"
                    )
                    monthly_total = daily_totals['billed_amount'].sum()
                    st.metric("Total Expenditure in Period", f"₹{monthly_total:,.2f}")
                else:
                    st.info("No expenditure data in selected date range")
            else:
                st.info("No bills data available for visualization")
        except Exception as e:
            st.error(f"Error generating expenditure trends: {str(e)}")

    
    st.markdown("---")
    st.caption(f"Auto Payment System v2.0.1 | Last refresh: {datetime.now().strftime('%d %b %Y %H:%M:%S')}")