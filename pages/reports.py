import streamlit as st
import pandas as pd
import datetime
from utils.db import get_bills, get_works
from utils.form_manager import FormManager

def show_reports():
    # Initialize FormManager
    form_manager = FormManager("reports")
    
    st.header("Reports")
    
    with form_manager.form("report_form"):
        # Report type selection
        report_type = form_manager.selectbox(
            "Select Report Type", 
            "report_form", 
            "report_type",
            options=["Payment Register", "Contractor Wise Payments", 
                    "Scheme Wise Expenditure", "Deduction Register"]
        )
        
        # Date range selection
        date_range = form_manager.date_input(
            "Select Date Range", 
            "report_form", 
            "date_range",
            value=[datetime.date.today() - datetime.timedelta(days=30), 
                  datetime.date.today()]
        )
        
        # Generate report button
        if form_manager.form_submit_button("report_form", "Generate Report"):
            # Fetch data from Supabase with date filtering
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
