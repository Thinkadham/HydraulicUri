import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from services import (
    get_recent_bills,
    get_contractors,
    get_works
)

def show():
    """Reports Generation Page"""
    st.header("Reports")
    
    # Report type selection
    report_type = st.selectbox(
        "Select Report Type",
        ["Payment Register", "Contractor Wise Payments", 
         "Scheme Wise Expenditure", "Deduction Register"]
    )
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            datetime.now() - timedelta(days=30)
    with col2:
        end_date = st.date_input(
            "End Date",
            datetime.now())
    
    # Generate report button
    if st.button("Generate Report"):
        with st.spinner("Generating report..."):
            try:
                # Fetch data based on date range
                bills = get_recent_bills(start_date, end_date)
                contractors = get_contractors()
                works = get_works()
                
                # Generate different report types
                if report_type == "Payment Register":
                    data = generate_payment_register(bills)
                elif report_type == "Contractor Wise Payments":
                    data = generate_contractor_report(bills)
                elif report_type == "Scheme Wise Expenditure":
                    data = generate_scheme_report(works)
                else:  # Deduction Register
                    data = generate_deduction_report(bills)
                
                # Display results
                if not data.empty:
                    st.dataframe(data, use_container_width=True)
                    
                    # Export options
                    export_col1, export_col2 = st.columns(2)
                    with export_col1:
                        st.download_button(
                            "Download as CSV",
                            data.to_csv(index=False),
                            f"{report_type.replace(' ', '_')}_{start_date}_to_{end_date}.csv",
                            "text/csv"
                        )
                    with export_col2:
                        st.download_button(
                            "Download as Excel",
                            data.to_excel(excel_writer="report.xlsx", index=False),
                            f"{report_type.replace(' ', '_')}_{start_date}_to_{end_date}.xlsx",
                            "application/vnd.ms-excel"
                        )
                else:
                    st.warning("No data found for selected criteria")
                    
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")

def generate_payment_register(bills):
    """Generate payment register report"""
    if not bills:
        return pd.DataFrame()
    
    df = pd.DataFrame(bills)
    return df[[
        "bill_no", "created_at", "payee", 
        "work", "payable", "status"
    ]]

def generate_contractor_report(bills):
    """Generate contractor-wise payment summary"""
    if not bills:
        return pd.DataFrame()
    
    df = pd.DataFrame(bills)
    report = df.groupby("payee").agg({
        "payable": ["count", "sum"],
        "created_at": "max"
    }).reset_index()
    
    report.columns = [
        "Contractor", "Total Bills", 
        "Total Amount", "Last Payment Date"
    ]
    return report

def generate_scheme_report(works):
    """Generate scheme-wise expenditure report"""
    if not works:
        return pd.DataFrame()
    
    df = pd.DataFrame(works)
    report = df.groupby("scheme").agg({
        "allotment_amount": "sum",
        "expenditure": "sum"
    }).reset_index()
    
    report["balance"] = report["allotment_amount"] - report["expenditure"]
    report["utilization_percent"] = (
        report["expenditure"] / report["allotment_amount"] * 100
    ).round(2)
    
    report.columns = [
        "Scheme", "Allocated", "Utilized", 
        "Balance", "Utilization %"
    ]
    return report

def generate_deduction_report(bills):
    """Generate deduction register report"""
    if not bills:
        return pd.DataFrame()
    
    df = pd.DataFrame(bills)
    report = df[[
        "bill_no", "created_at", "payee",
        "income_tax_amount", "deposit_amount", 
        "cess_amount"
    ]]
    
    report["total_deduction"] = (
        report["income_tax_amount"] + 
        report["deposit_amount"] + 
        report["cess_amount"]
    )
    
    report.columns = [
        "Bill No", "Date", "Payee",
        "Income Tax", "Deposit", 
        "Cess", "Total Deduction"
    ]
    return report
