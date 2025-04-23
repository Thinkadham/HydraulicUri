import streamlit as st
import pandas as pd
import datetime
from num2words import num2words

# App Configuration
st.set_page_config(
    page_title="Auto Payment System",
    page_icon="💰",
    layout="wide"
)

# Load data (in a real app, this would connect to a database)
@st.cache_data
def load_data():
    # Load data from Excel sheets
    try:
        works_df = pd.read_excel("AutoPaySystem.xlsx", sheet_name="Works")
        contractor_df = pd.read_excel("AutoPaySystem.xlsx", sheet_name="Contractor")
        return works_df, contractor_df
    except:
        # Return empty DataFrames if file not found
        return pd.DataFrame(), pd.DataFrame()

works_df, contractor_df = load_data()

# Main App
def main():
    st.title("Auto Payment System")
    st.caption("Version 2.0.1 | Designed & Developed by Mohammad Adham Wani")
    
    # Sidebar navigation
    menu = st.sidebar.selectbox("Navigation", 
                               ["Dashboard", "Create New Bill", "Contractor Management", 
                                "Works Management", "Reports", "Settings"])
    
    if menu == "Dashboard":
        show_dashboard()
    elif menu == "Create New Bill":
        create_new_bill()
    elif menu == "Contractor Management":
        contractor_management()
    elif menu == "Works Management":
        works_management()
    elif menu == "Reports":
        show_reports()
    elif menu == "Settings":
        show_settings()

# Dashboard Page
def show_dashboard():
    st.header("Dashboard")
    
    # Stats columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Contractors", len(contractor_df))
    with col2:
        st.metric("Active Works", len(works_df))
    with col3:
        st.metric("Pending Bills", "15")  # Example value
        
    # Recent bills table (example data)
    st.subheader("Recent Bills")
    recent_bills = pd.DataFrame({
        "Bill No": ["B-001", "B-002", "B-003"],
        "Payee": ["Mumtaz Ahmad Khan", "Reyaz Ahmad Khan", "Abdul Aziz Malik"],
        "Work": ["Lachipora B", "Maintenance & Repairs", "Limber Tethmulla Khul"],
        "Amount": [1018483, 134573, 921577],
        "Status": ["Paid", "Pending", "Approved"]
    })
    st.dataframe(recent_bills, use_container_width=True)
    
    # Budget utilization chart (placeholder)
    st.subheader("Budget Utilization")
    budget_data = pd.DataFrame({
        "Scheme": ["BADP", "DDC BDC Funds", "NABARD", "IRR UT CAPEX"],
        "Allocated": [1373000, 24988000, 30306000, 33787000],
        "Utilized": [921577, 15000000, 20000000, 12000000]
    })
    st.bar_chart(budget_data.set_index("Scheme"))

# Create New Bill Page
def create_new_bill():
    st.header("Create New Bill")
    
    with st.form("bill_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Payee information
            payee = st.selectbox("Select Payee", contractor_df["Name"].unique())
            payee_data = contractor_df[contractor_df["Name"] == payee].iloc[0]
            
            st.text_input("S/O", payee_data.get("Parentage", ""))
            st.text_input("R/O", payee_data.get("Resident", ""))
            st.text_input("Registration", payee_data.get("Registration", ""))
            st.text_input("Class", payee_data.get("Class", ""))
            
        with col2:
            st.text_input("PAN", payee_data.get("PAN", ""))
            st.text_input("GSTIN", payee_data.get("GSTIN", ""))
            st.text_input("Account No", payee_data.get("AcNo", ""))
            
        # Bill details
        bill_type = st.selectbox("Bill Type", ["Plan", "Non Plan"])
        major_head = st.selectbox("Major Head", works_df["MH"].unique())
        
        # Filter schemes based on selected major head
        schemes = works_df[works_df["MH"] == major_head]["Scheme"].unique()
        scheme = st.selectbox("Scheme", schemes)
        
        # Filter works based on selected scheme
        works = works_df[(works_df["MH"] == major_head) & (works_df["Scheme"] == scheme)]["WorkName"].unique()
        work = st.selectbox("Name of Work/Particulars", works)
        
        # Get work details
        work_data = works_df[(works_df["MH"] == major_head) & 
                            (works_df["Scheme"] == scheme) & 
                            (works_df["WorkName"] == work)].iloc[0]
        
        st.text_area("Nomenclature", work_data.get("Nomenclature", ""))
        
        # Bill amounts
        col3, col4 = st.columns(2)
        with col3:
            billed_amount = st.number_input("Billed Amount", min_value=0)
            deduct_payments = st.number_input("Deduct Payments", min_value=0)
            payable = billed_amount - deduct_payments
            st.text_input("Payable", payable, disabled=True)
            
        with col4:
            funds_available = st.number_input("Funds Available", min_value=0)
            
            # Deductions
            income_tax_percent = st.number_input("Income Tax %age", min_value=0.0, max_value=100.0, value=2.24)
            deposit_percent = st.number_input("Deposit %age", min_value=0.0, max_value=100.0, value=10.0)
            cess_percent = st.number_input("Cess", min_value=0.0, max_value=100.0, value=1.0)
            
        # Bill classification
        cc_bill = st.selectbox("CC of Bill", ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"])
        final_bill = st.radio("Final Bill", ["Yes", "No"])
        
        # Allotment details
        st.subheader("Allotment Details")
        col5, col6 = st.columns(2)
        with col5:
            allotment_no = st.text_input("Allotment No")
            allotment_date = st.date_input("Allotment Date")
            allotment_amount = st.number_input("Allotment Amount", min_value=0)
            
        with col6:
            ts_no = st.text_input("TS No")
            ts_date = st.date_input("TS Date")
            ts_amount = st.number_input("TS Amount", min_value=0)
            
        # Submit button
        if st.form_submit_button("Generate Bill"):
            # Calculate deductions
            income_tax = round(payable * (income_tax_percent / 100), 0)
            deposit = round(payable * (deposit_percent / 100), 0)
            cess = round(payable * (cess_percent / 100), 0)
            total_deduction = income_tax + deposit + cess
            
            # Calculate net amount
            net_amount = payable - total_deduction
            
            # Generate bill summary
            bill_summary = {
                "Payee": payee,
                "Work": work,
                "Billed Amount": billed_amount,
                "Deduct Payments": deduct_payments,
                "Payable": payable,
                "Income Tax": income_tax,
                "Deposit": deposit,
                "Cess": cess,
                "Total Deduction": total_deduction,
                "Net Amount": net_amount,
                "Amount in Words": num2words(net_amount, lang='en_IN').title()
            }
            
            # Display bill summary
            st.success("Bill generated successfully!")
            st.subheader("Bill Summary")
            st.json(bill_summary)
            
            # Option to save or print
            col7, col8 = st.columns(2)
            with col7:
                if st.button("Save Bill"):
                    # In a real app, this would save to database
                    st.success("Bill saved successfully!")
            with col8:
                if st.button("Print Bill"):
                    # In a real app, this would generate a PDF
                    st.success("Bill printed successfully!")

# Contractor Management Page
def contractor_management():
    st.header("Contractor Management")
    
    tab1, tab2 = st.tabs(["View Contractors", "Add New Contractor"])
    
    with tab1:
        st.dataframe(contractor_df, use_container_width=True)
        
    with tab2:
        with st.form("contractor_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name")
                parentage = st.text_input("Parentage")
                resident = st.text_input("Resident")
                registration = st.text_input("Registration")
                
            with col2:
                contractor_class = st.selectbox("Class", ["A", "B", "C", "D", "E"])
                pan = st.text_input("PAN")
                gstin = st.text_input("GSTIN")
                account_no = st.text_input("Account No")
                
            if st.form_submit_button("Add Contractor"):
                # In a real app, this would save to database
                new_contractor = {
                    "Name": name,
                    "Parentage": parentage,
                    "Resident": resident,
                    "Registration": registration,
                    "Class": contractor_class,
                    "PAN": pan,
                    "GSTIN": gstin,
                    "AcNo": account_no
                }
                st.success("Contractor added successfully!")

# Works Management Page
def works_management():
    st.header("Works Management")
    
    tab1, tab2 = st.tabs(["View Works", "Add New Work"])
    
    with tab1:
        st.dataframe(works_df, use_container_width=True)
        
    with tab2:
        with st.form("work_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                mh = st.number_input("Major Head (MH)", min_value=0)
                scheme = st.text_input("Scheme")
                work_name = st.text_input("Work Name")
                work_code = st.text_input("Work Code")
                
            with col2:
                classification = st.text_input("Classification")
                aaa_no = st.text_input("AAA No")
                aaa_date = st.date_input("AAA Date")
                aaa_amount = st.number_input("AAA Amount", min_value=0)
                
            nomenclature = st.text_area("Nomenclature")
            
            if st.form_submit_button("Add Work"):
                # In a real app, this would save to database
                new_work = {
                    "MH": mh,
                    "Scheme": scheme,
                    "WorkName": work_name,
                    "WorkCode": work_code,
                    "Classification": classification,
                    "AAA No": aaa_no,
                    "AAA Dt": aaa_date,
                    "AAA Amt": aaa_amount,
                    "Nomenclature": nomenclature
                }
                st.success("Work added successfully!")

# Reports Page
def show_reports():
    st.header("Reports")
    
    report_type = st.selectbox("Select Report Type", 
                              ["Payment Register", "Contractor Wise Payments", 
                               "Scheme Wise Expenditure", "Deduction Register"])
    
    date_range = st.date_input("Select Date Range", 
                              [datetime.date.today() - datetime.timedelta(days=30), 
                               datetime.date.today()])
    
    if st.button("Generate Report"):
        # In a real app, this would query the database
        st.success(f"Generating {report_type} report for {date_range[0]} to {date_range[1]}")
        
        # Placeholder data for demonstration
        if report_type == "Payment Register":
            data = pd.DataFrame({
                "Bill No": ["B-001", "B-002", "B-003"],
                "Date": [datetime.date.today() - datetime.timedelta(days=2), 
                         datetime.date.today() - datetime.timedelta(days=1), 
                         datetime.date.today()],
                "Payee": ["Mumtaz Ahmad Khan", "Reyaz Ahmad Khan", "Abdul Aziz Malik"],
                "Work": ["Lachipora B", "Maintenance & Repairs", "Limber Tethmulla Khul"],
                "Amount": [1018483, 134573, 921577],
                "Status": ["Paid", "Pending", "Approved"]
            })
        elif report_type == "Contractor Wise Payments":
            data = pd.DataFrame({
                "Contractor": ["Mumtaz Ahmad Khan", "Reyaz Ahmad Khan", "Abdul Aziz Malik"],
                "Total Bills": [5, 3, 7],
                "Total Amount": [2500000, 1500000, 3500000],
                "Last Payment Date": [datetime.date.today() - datetime.timedelta(days=10), 
                                     datetime.date.today() - datetime.timedelta(days=15), 
                                     datetime.date.today() - datetime.timedelta(days=5)]
            })
        elif report_type == "Scheme Wise Expenditure":
            data = pd.DataFrame({
                "Scheme": ["BADP", "DDC BDC Funds", "NABARD", "IRR UT CAPEX"],
                "Allocated": [1373000, 24988000, 30306000, 33787000],
                "Utilized": [921577, 15000000, 20000000, 12000000],
                "Balance": [451423, 9988000, 10306000, 21787000],
                "Utilization %": [67, 60, 66, 36]
            })
        else:  # Deduction Register
            data = pd.DataFrame({
                "Bill No": ["B-001", "B-002", "B-003"],
                "Date": [datetime.date.today() - datetime.timedelta(days=2), 
                         datetime.date.today() - datetime.timedelta(days=1), 
                         datetime.date.today()],
                "Payee": ["Mumtaz Ahmad Khan", "Reyaz Ahmad Khan", "Abdul Aziz Malik"],
                "Income Tax": [22814, 3014, 20643],
                "Deposit": [101848, 13457, 92158],
                "Cess": [10185, 1346, 9216],
                "Total Deduction": [134847, 17817, 122017]
            })
        
        st.dataframe(data, use_container_width=True)
        
        # Export options
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button("Download CSV", data.to_csv(index=False), "report.csv", "text/csv")
        with col2:
            st.download_button("Download Excel", data.to_excel("report.xlsx", index=False), "report.xlsx")
        with col3:
            st.button("Print Report")

# Settings Page
def show_settings():
    st.header("Settings")
    
    with st.expander("User Management"):
        st.write("User management functionality would go here")
        
    with st.expander("System Configuration"):
        st.write("System configuration options would go here")
        
    with st.expander("Backup & Restore"):
        st.write("Backup and restore functionality would go here")

if __name__ == "__main__":
    main()
