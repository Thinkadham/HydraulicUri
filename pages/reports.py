import streamlit as st
import pandas as pd
import datetime
from utils.db import get_bills, get_works
from utils.auth import check_auth

# Only show content if authenticated
if not check_auth():
    st.warning("Please log in to access this page")
    st.stop()

def show_reports():
    st.header("Reports")
    
    report_type = st.selectbox("Select Report Type", 
                              ["Payment Register", "Contractor Wise Payments", 
                               "Scheme Wise Expenditure", "Deduction Register"])
    
    date_range = st.date_input("Select Date Range", 
                              [datetime.date.today() - datetime.timedelta(days=30), 
                               datetime.date.today()])
    
    if st.button("Generate Report"):
        # Fetch data from Supabase with date filtering
        start_date, end_date = date_range
        bills = get_bills(start_date, end_date)
        works = get_works()
        
        if report_type == "Payment Register":
            data = pd.DataFrame(bills)
            if not data.empty:
                data = data[["bill_no", "created_at", "payee", "work", "payable", "status"]]
        elif report_type == "Contractor Wise Payments":
            if bills:
                df = pd.DataFrame(bills)
                data = df.groupby("payee").agg({
                    "payable": ["count", "sum"],
                    "created_at": "max"
                }).reset_index()
                data.columns = ["Contractor", "Total Bills", "Total Amount", "Last Payment Date"]
            else:
                data = pd.DataFrame()
        elif report_type == "Scheme Wise Expenditure":
            if works:
                data = pd.DataFrame(works)
                data = data.groupby("scheme").agg({
                    "allotment_amount": "sum",
                    "expenditure": "sum"
                }).reset_index()
                data["balance"] = data["allotment_amount"] - data["expenditure"]
                data["utilization_percent"] = (data["expenditure"] / data["allotment_amount"]) * 100
                data.columns = ["Scheme", "Allocated", "Utilized", "Balance", "Utilization %"]
            else:
                data = pd.DataFrame()
        else:  # Deduction Register
            if bills:
                data = pd.DataFrame(bills)
                data = data[["bill_no", "created_at", "payee", "income_tax_amount", "deposit_amount", "cess_amount"]]
                data["total_deduction"] = data["income_tax_amount"] + data["deposit_amount"] + data["cess_amount"]
                data.columns = ["Bill No", "Date", "Payee", "Income Tax", "Deposit", "Cess", "Total Deduction"]
            else:
                data = pd.DataFrame()
        
        if not data.empty:
            st.dataframe(data, use_container_width=True)
            
            # Export options
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button("Download CSV", data.to_csv(index=False), "report.csv", "text/csv")
            with col2:
                st.download_button("Download Excel", data.to_excel("report.xlsx", index=False), "report.xlsx")
            with col3:
                st.button("Print Report")
        else:
            st.warning("No data found for the selected criteria")

show_reports()
