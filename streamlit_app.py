import streamlit as st
import pandas as pd
import datetime
from num2words import num2words
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from fpdf import FPDF

# Load environment variables
load_dotenv()

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

supabase = init_supabase()

# App Configuration
st.set_page_config(
    page_title="Auto Payment System",
    page_icon="💰",
    layout="wide"
)

# PDF Generation Function
def generate_payorder_pdf(bill_data):
    """Generate PDF in JJM template format"""
    
    pdf = FPDF()
    pdf.add_page()
    
   # Add the DejaVu fonts
    pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf', uni=True)
    
    # Set the font
    pdf.set_font('DejaVu', '', 10)
    
    # Header with timestamp
    pdf.cell(0, 5, f"Time Stamp {datetime.datetime.now().strftime('%d-%m-%Y %I:%M:%S %p')}", ln=1, align='R')
    pdf.ln(5)
    
    # Payment Order title
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "PAYMENT ORDER", ln=1, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, "*"*80, ln=1, align='C')
    pdf.ln(5)
    
    # Payee information
    pdf.cell(0, 5, f"Payment in favour of M/s {bill_data['payee_name']} S/O {bill_data['parentage']}", ln=1)
    pdf.cell(0, 5, f"R/O {bill_data['resident']} bearing Registration No: {bill_data['registration']},", ln=1)
    pdf.cell(0, 5, f"PAN: {bill_data['pan']}, GSTIN: {bill_data['gstin']} and Account No: {bill_data['account_no']}", ln=1)
    pdf.ln(5)
    
    # Work details
    pdf.cell(0, 5, f"on account of {bill_data['cc_bill']} for {bill_data['work_description']}", ln=1)
    pdf.cell(0, 5, f"AAA No: {bill_data['aaa_no']} Dated: {bill_data['aaa_date']} for RS {bill_data['aaa_amount']:,}", ln=1)
    pdf.cell(0, 5, f"TS No: {bill_data['ts_no']} Dated: {bill_data['ts_date']} for RS {bill_data['ts_amount']:,}", ln=1)
    pdf.cell(0, 5, f"Allotment No: {bill_data['allotment_no']} Dated: {bill_data['allotment_date']} for RS {bill_data['allotment_amount']:,}", ln=1)
    pdf.ln(5)
    
    # Financial details
    pdf.cell(0, 5, f"Billed Amount = RS {bill_data['billed_amount']:,}", ln=1)
    pdf.cell(0, 5, f"Deduct Last Payments = RS {bill_data['deduct_payments']:,}", ln=1)
    pdf.cell(0, 5, f"Payable Amount = RS {bill_data['payable']:,}", ln=1)
    pdf.cell(0, 5, f"Restricted to = RS {bill_data['restricted_to']:,}", ln=1)
    pdf.ln(5)
    
    # Payment details
    pdf.cell(0, 5, f"Passed for an amount of RS {bill_data['net_amount']:,} (Rupees {bill_data['amount_in_words']} Only)", ln=1)
    pdf.cell(0, 5, f"but debit RS {bill_data['payable']:,} to Major Head {bill_data['major_head']}-JJM, Scheme {bill_data['scheme_name']}", ln=1)
    pdf.cell(0, 5, f"having IMIS Code {bill_data['imis_code']} crediting RS {bill_data['income_tax_amount']:,} to Income Tax,", ln=1)
    pdf.cell(0, 5, f"RS {bill_data['deposit_amount']:,} to Deposit, RS 0 to GST and RS {bill_data['cess_amount']:,} to Labour Cess.", ln=1)
    pdf.ln(5)
    
    # Deductions section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "DEDUCTIONS", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, f"Cess @ {bill_data['cess_percent']}% = RS {bill_data['cess_amount']:,}", ln=1)
    pdf.cell(0, 5, f"I/Tax @ {bill_data['income_tax_percent']}% = RS {bill_data['income_tax_amount']:,}", ln=1)
    pdf.cell(0, 5, f"Deposit @ {bill_data['deposit_percent']}% = RS {bill_data['deposit_amount']:,}", ln=1)
    pdf.cell(0, 5, f"TOTAL Deduction = RS {bill_data['total_deduction']:,}", ln=1)
    pdf.ln(5)
    
    # Signature blocks
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(90, 10, "Executive Engineer", align='C')
    pdf.cell(90, 10, "Superintending Engineer", align='C')
    pdf.ln(15)
    
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, f"JSD (PHE) Hydraulic Division {bill_data['division']}", ln=1, align='C')
    pdf.cell(0, 5, f"Jal Shakti Hyd. Circle {bill_data['circle']}", ln=1, align='C')
    pdf.ln(10)
    
    # Budget information
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "BUDGET CONTROL", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, f"BUDGET = RS {bill_data['budget']:,}", ln=1)
    pdf.cell(0, 5, f"EXPENDITURE = RS {bill_data['expenditure']:,}", ln=1)
    pdf.cell(0, 5, f"BALANCE = RS {bill_data['balance']:,}", ln=1)
    pdf.ln(10)
    
    # Certification section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "CERTIFICATE", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 5, f"This is to certify that an amount of RS {bill_data['gross_amount']:,} (Rupees {bill_data['amount_in_words']} Only) is to be debited from SNA amount of {bill_data['scheme_name']} under JJM code in IMIS {bill_data['imis_code']} for which PPA has been generated after observing all codal formalities/guidelines of the programme. The payment should be made as per the following breakup:")
    pdf.ln(5)
    
    # Payment breakdown table
    col_widths = [60, 40, 40, 50]
    pdf.cell(col_widths[0], 10, "Gross Amount", border=1)
    pdf.cell(col_widths[1], 10, "Central Share", border=1)
    pdf.cell(col_widths[2], 10, "UT Share", border=1)
    pdf.cell(col_widths[3], 10, "Total", border=1, ln=1)
    
    pdf.cell(col_widths[0], 10, "", border=1)
    pdf.cell(col_widths[1], 10, f"RS {bill_data['central_share']:,}", border=1)
    pdf.cell(col_widths[2], 10, f"RS {bill_data['ut_share']:,}", border=1)
    pdf.cell(col_widths[3], 10, f"RS {bill_data['gross_amount']:,}", border=1, ln=1)
    
    pdf.cell(sum(col_widths[:3]), 10, "Income Tax", border=1)
    pdf.cell(col_widths[3], 10, f"RS {bill_data['income_tax_amount']:,}", border=1, ln=1)
    
    pdf.cell(sum(col_widths[:3]), 10, "Labour Cess", border=1)
    pdf.cell(col_widths[3], 10, f"RS {bill_data['cess_amount']:,}", border=1, ln=1)
    
    pdf.cell(sum(col_widths[:3]), 10, "GST", border=1)
    pdf.cell(col_widths[3], 10, "RS 0", border=1, ln=1)
    
    pdf.cell(sum(col_widths[:3]), 10, "Deposit", border=1)
    pdf.cell(col_widths[3], 10, f"RS {bill_data['deposit_amount']:,}", border=1, ln=1)
    
    pdf.cell(sum(col_widths[:3]), 10, "Additional Deposit", border=1)
    pdf.cell(col_widths[3], 10, "", border=1, ln=1)
    
    pdf.cell(sum(col_widths[:3]), 10, "Net payable to Agency", border=1)
    pdf.cell(col_widths[3], 10, f"RS {bill_data['net_amount']:,}", border=1, ln=1)
    
    pdf.ln(15)
    
    # Final signatures
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(90, 10, "Executive Engineer", align='C')
    pdf.cell(90, 10, "Superintending Engineer", align='C')
    pdf.ln(15)
    
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, f"JSD (PHE) Hydraulic Division {bill_data['division']}", ln=1, align='C')
    pdf.cell(0, 5, f"Jal Shakti Hyd. Circle {bill_data['circle']}", ln=1, align='C')
    
    # Save the PDF
    filename = f"PayOrder_{bill_data['bill_no']}.pdf"
    pdf.output(filename)
    return filename

# Authentication
def check_auth():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    return st.session_state.authenticated

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # In a real app, verify credentials against Supabase auth
        if username == "admin" and password == "admin123":  # Example credentials
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid credentials")

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
    
    # Fetch data from Supabase
    contractors = supabase.table("contractors").select("*").execute().data
    works = supabase.table("works").select("*").execute().data
    bills = supabase.table("bills").select("*").execute().data
    
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

# Create New Bill Page
def create_new_bill():
    st.header("Create New Bill")
    
    # Fetch data from Supabase
    contractors = supabase.table("contractors").select("*").execute().data
    works = supabase.table("works").select("*").execute().data
    
    with st.form("bill_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Payee information
            payee = st.selectbox("Select Payee", [c["name"] for c in contractors])
            payee_data = next((c for c in contractors if c["name"] == payee), {})
            
            parentage = st.text_input("S/O", payee_data.get("parentage", ""))
            resident = st.text_input("R/O", payee_data.get("resident", ""))
            registration = st.text_input("Registration", payee_data.get("registration", ""))
            contractor_class = st.text_input("Class", payee_data.get("class", ""))
            
        with col2:
            pan = st.text_input("PAN", payee_data.get("pan", ""))
            gstin = st.text_input("GSTIN", payee_data.get("gstin", ""))
            account_no = st.text_input("Account No", payee_data.get("account_no", ""))
            
        # Bill details
        bill_type = st.selectbox("Bill Type", ["Plan", "Non Plan"])
        major_heads = list(set(w["mh"] for w in works))
        major_head = st.selectbox("Major Head", major_heads)
        
        # Filter schemes based on selected major head
        schemes = list(set(w["scheme"] for w in works if w["mh"] == major_head))
        scheme = st.selectbox("Scheme", schemes)
        
        # Filter works based on selected scheme
        filtered_works = [w for w in works if w["mh"] == major_head and w["scheme"] == scheme]
        work = st.selectbox("Name of Work/Particulars", [w["work_name"] for w in filtered_works])
        
        # Get work details
        work_data = next((w for w in filtered_works if w["work_name"] == work), {})
        
        nomenclature = st.text_area("Nomenclature", work_data.get("nomenclature", ""))
        imis_code = st.text_input("IMIS Code", work_data.get("imis_code", ""))
        
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
            
        # Budget details
        st.subheader("Budget Details")
        col7, col8 = st.columns(2)
        with col7:
            budget = st.number_input("Total Budget", min_value=0, value=work_data.get("allotment_amount", 0))
            central_share = st.number_input("Central Share", min_value=0)
            
        with col8:
            ut_share = st.number_input("UT Share", min_value=0)
            division = st.text_input("Division", "Uri")
            circle = st.text_input("Circle", "Bla/Bpr HQ Sopore")
            
        # Submit button
        if st.form_submit_button("Generate Bill"):
            # Calculate deductions
            income_tax = round(payable * (income_tax_percent / 100), 0)
            deposit = round(payable * (deposit_percent / 100), 0)
            cess = round(payable * (cess_percent / 100), 0)
            total_deduction = income_tax + deposit + cess
            
            # Calculate net amount
            net_amount = payable - total_deduction
            
            # Generate bill data
            bill_data = {
                "payee": payee,
                "payee_id": payee_data.get("id"),
                "work": work,
                "work_id": work_data.get("id"),
                "bill_type": bill_type,
                "major_head": major_head,
                "scheme": scheme,
                "nomenclature": nomenclature,
                "billed_amount": billed_amount,
                "deduct_payments": deduct_payments,
                "payable": payable,
                "funds_available": funds_available,
                "income_tax_percent": income_tax_percent,
                "income_tax_amount": income_tax,
                "deposit_percent": deposit_percent,
                "deposit_amount": deposit,
                "cess_percent": cess_percent,
                "cess_amount": cess,
                "total_deduction": total_deduction,
                "net_amount": net_amount,
                "amount_in_words": num2words(net_amount, lang='en_IN').title(),
                "cc_bill": cc_bill,
                "final_bill": final_bill == "Yes",
                "allotment_no": allotment_no,
                "allotment_date": allotment_date.isoformat(),
                "allotment_amount": allotment_amount,
                "ts_no": ts_no,
                "ts_date": ts_date.isoformat(),
                "ts_amount": ts_amount,
                "status": "Pending",
                "created_at": datetime.datetime.now().isoformat()
            }
            
            # Insert into Supabase
            try:
                result = supabase.table("bills").insert(bill_data).execute()
                if result.data:
                    st.success("Bill saved successfully!")
                    
                    # Update work expenditure in Supabase
                    current_expenditure = work_data.get("expenditure", 0)
                    new_expenditure = current_expenditure + billed_amount
                    supabase.table("works").update({"expenditure": new_expenditure}).eq("id", work_data["id"]).execute()
                    
                    # Prepare data for PDF generation
                    pdf_data = {
                        "bill_no": result.data[0].get("id"),
                        "payee_name": payee,
                        "parentage": parentage,
                        "resident": resident,
                        "registration": registration,
                        "pan": pan,
                        "gstin": gstin,
                        "account_no": account_no,
                        "cc_bill": cc_bill,
                        "work_description": work,
                        "aaa_no": allotment_no,
                        "aaa_date": allotment_date.strftime("%d-%m-%Y"),
                        "aaa_amount": allotment_amount,
                        "ts_no": ts_no,
                        "ts_date": ts_date.strftime("%d-%m-%Y"),
                        "ts_amount": ts_amount,
                        "allotment_no": allotment_no,
                        "allotment_date": allotment_date.strftime("%d-%m-%Y"),
                        "allotment_amount": allotment_amount,
                        "billed_amount": billed_amount,
                        "deduct_payments": deduct_payments,
                        "payable": payable,
                        "restricted_to": payable,
                        "cess_percent": cess_percent,
                        "cess_amount": cess,
                        "income_tax_percent": income_tax_percent,
                        "income_tax_amount": income_tax,
                        "deposit_percent": deposit_percent,
                        "deposit_amount": deposit,
                        "total_deduction": total_deduction,
                        "net_amount": net_amount,
                        "gross_amount": payable,
                        "amount_in_words": num2words(net_amount, lang='en_IN').title(),
                        "scheme_name": scheme,
                        "major_head": major_head,
                        "imis_code": imis_code,
                        "budget": budget,
                        "expenditure": new_expenditure,
                        "balance": budget - new_expenditure,
                        "central_share": central_share,
                        "ut_share": ut_share,
                        "division": division,
                        "circle": circle
                    }
                    
                    # Generate and offer PDF download
                    pdf_filename = generate_payorder_pdf(pdf_data)
                    with open(pdf_filename, "rb") as f:
                        st.download_button(
                            label="Download PayOrder PDF",
                            data=f,
                            file_name=pdf_filename,
                            mime="application/pdf"
                        )
            except Exception as e:
                st.error(f"Error saving bill: {str(e)}")

# Contractor Management Page
def contractor_management():
    st.header("Contractor Management")
    
    tab1, tab2 = st.tabs(["View Contractors", "Add New Contractor"])
    
    with tab1:
        contractors = supabase.table("contractors").select("*").execute().data
        st.dataframe(pd.DataFrame(contractors), use_container_width=True)
        
    with tab2:
        with st.form("contractor_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name", key="contractor_name")
                parentage = st.text_input("Parentage")
                resident = st.text_input("Resident")
                registration = st.text_input("Registration")
                
            with col2:
                contractor_class = st.selectbox("Class", ["A", "B", "C", "D", "E"])
                pan = st.text_input("PAN")
                gstin = st.text_input("GSTIN")
                account_no = st.text_input("Account No")
                
            if st.form_submit_button("Add Contractor"):
                contractor_data = {
                    "name": name,
                    "parentage": parentage,
                    "resident": resident,
                    "registration": registration,
                    "class": contractor_class,
                    "pan": pan,
                    "gstin": gstin,
                    "account_no": account_no,
                    "created_at": datetime.datetime.now().isoformat()
                }
                
                try:
                    result = supabase.table("contractors").insert(contractor_data).execute()
                    if result.data:
                        st.success("Contractor added successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error adding contractor: {str(e)}")

# Works Management Page
def works_management():
    st.header("Works Management")
    
    tab1, tab2 = st.tabs(["View Works", "Add New Work"])
    
    with tab1:
        works = supabase.table("works").select("*").execute().data
        st.dataframe(pd.DataFrame(works), use_container_width=True)
        
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
            imis_code = st.text_input("IMIS Code")
            expenditure = st.number_input("Initial Expenditure", min_value=0, value=0)
            
            if st.form_submit_button("Add Work"):
                work_data = {
                    "mh": mh,
                    "scheme": scheme,
                    "work_name": work_name,
                    "work_code": work_code,
                    "classification": classification,
                    "aaa_no": aaa_no,
                    "aaa_date": aaa_date.isoformat(),
                    "aaa_amount": aaa_amount,
                    "nomenclature": nomenclature,
                    "imis_code": imis_code,
                    "allotment_amount": aaa_amount,
                    "expenditure": expenditure,
                    "created_at": datetime.datetime.now().isoformat()
                }
                
                try:
                    result = supabase.table("works").insert(work_data).execute()
                    if result.data:
                        st.success("Work added successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error adding work: {str(e)}")

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
        # Fetch data from Supabase with date filtering
        start_date, end_date = date_range
        bills = supabase.table("bills").select("*").gte("created_at", start_date.isoformat()).lte("created_at", end_date.isoformat()).execute().data
        works = supabase.table("works").select("*").execute().data
        contractors = supabase.table("contractors").select("*").execute().data
        
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

# Settings Page
def show_settings():
    st.header("Settings")
    
    with st.expander("User Management"):
        st.write("User management functionality would go here")
        
    with st.expander("System Configuration"):
        st.write("System configuration options would go here")
        
    with st.expander("Backup & Restore"):
        if st.button("Create Backup"):
            try:
                # Export all tables to CSV
                tables = ["contractors", "works", "bills"]
                for table in tables:
                    data = supabase.table(table).select("*").execute().data
                    pd.DataFrame(data).to_csv(f"{table}_backup.csv", index=False)
                
                st.success("Backup created successfully! Check your local files.")
            except Exception as e:
                st.error(f"Error creating backup: {str(e)}")

# Run the app
if __name__ == "__main__":
    if check_auth():
        main()
    else:
        login()
