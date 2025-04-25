import streamlit as st
import pandas as pd
import datetime
from utils.db import get_bills, get_works

def show_reports():
    st.header("Reports")
    
    with st.form("report_form"):
        report_type = st.selectbox(
            "Select Report Type", 
            options=["Payment Register", "Contractor Wise Payments", 
                    "Scheme Wise Expenditure", "Deduction Register"],
            key="report_type"
        )
        
        date_range = st.date_input(
            "Select Date Range", 
            value=[datetime.date.today() - datetime.timedelta(days=30), 
                  datetime.date.today()],
            key="date_range"
        )
        
        if st.form_submit_button("Generate Report"):
            start_date, end_date = date_range
            bills = get_bills(start_date, end_date)
            works = get_works()
            
            if report_type == "Payment Register":
                data = pd.DataFrame(bills)
                if not data.empty:
                    data = data[["bill_no", "created_at", "payee", "work", "payable", "status"]]
                    data.columns = ["Bill No", "Date", "Payee", "Work", "Amount", "Status"]
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
                    data = data[["bill_no", "created_at", "payee", "income_tax_amount", 
                                "deposit_amount", "cess_amount"]]
                    data["total_deduction"] = (data["income_tax_amount"] + 
                                             data["deposit_amount"] + 
                                             data["cess_amount"])
                    data.columns = ["Bill No", "Date", "Payee", "Income Tax", 
                                  "Deposit", "Cess", "Total Deduction"]
                else:
                    data = pd.DataFrame()
            
            if not data.empty:
                st.dataframe(
                    data, 
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Amount": st.column_config.NumberColumn(format="₹%.2f"),
                        "Total Amount": st.column_config.NumberColumn(format="₹%.2f"),
                        "Allocated": st.column_config.NumberColumn(format="₹%.2f"),
                        "Utilized": st.column_config.NumberColumn(format="₹%.2f"),
                        "Balance": st.column_config.NumberColumn(format="₹%.2f"),
                        "Utilization %": st.column_config.NumberColumn(format="%.2f%%"),
                        "Date": st.column_config.DateColumn(format="DD/MM/YYYY"),
                        "Last Payment Date": st.column_config.DateColumn(format="DD/MM/YYYY")
                    }
                )
                
                # Export options
                export_col1, export_col2, export_col3 = st.columns(3)
                with export_col1:
                    st.download_button(
                        "Download CSV", 
                        data.to_csv(index=False), 
                        "report.csv", 
                        "text/csv",
                        key=form_manager.get_form_key("report_form") + "_csv"
                    )
                with export_col2:
                    st.download_button(
                        "Download Excel", 
                        data.to_excel("report.xlsx", index=False), 
                        "report.xlsx",
                        key=form_manager.get_form_key("report_form") + "_excel"
                    )
                with export_col3:
                    st.button(
                        "Print Report",
                        key=form_manager.get_form_key("report_form") + "_print"
                    )
            else:
                st.warning("No data found for the selected criteria")

show_reports()
