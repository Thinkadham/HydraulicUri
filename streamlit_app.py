import streamlit as st
import pandas as pd
import datetime
from num2words import num2words
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from fpdf import FPDF
import tempfile

# Load environment variables
load_dotenv()

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

supabase = init_supabase()

# Custom PDF Class with Unicode Support
class UnicodePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_unicode_font()
    
    def add_unicode_font(self):
        """Try multiple Unicode font options"""
        font_paths = [
            os.path.join('fonts', 'DejaVuSans.ttf'),
            os.path.join('fonts', 'NotoSans-Regular.ttf')
        ]
        
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    self.add_font('UnicodeFont', '', font_path, uni=True)
                    self.set_font('UnicodeFont', '', 10)
                    return True
            except:
                continue
        
        self.set_font('Arial', '', 10)
        return False

# PDF Generation Function
def generate_payorder_pdf(bill_data):
    """Generate PDF with guaranteed Unicode handling"""
    pdf = UnicodePDF()
    pdf.add_page()
    
    def safe_text(text):
        """Convert to ASCII-safe text"""
        if not isinstance(text, str):
            text = str(text)
        replacements = {
            '₹': 'Rs.',
            '’': "'",
            '‘': "'",
            '–': '-',
            '—': '-'
        }
        for uni, ascii in replacements.items():
            text = text.replace(uni, ascii)
        return text.encode('ascii', 'ignore').decode('ascii')
    
    # Header
    pdf.set_font('', 'B', 14)
    pdf.cell(0, 10, safe_text("PAYMENT ORDER"), ln=1, align='C')
    pdf.set_font('', '', 10)
    pdf.cell(0, 5, safe_text("*"*80), ln=1, align='C')
    pdf.ln(5)
    
    # Payee Information
    pdf.cell(0, 5, safe_text(f"Payment in favour of M/s {bill_data['payee_name']} S/O {bill_data['parentage']}"), ln=1)
    pdf.cell(0, 5, safe_text(f"R/O {bill_data['resident']} bearing Registration No: {bill_data['registration']},"), ln=1)
    pdf.cell(0, 5, safe_text(f"PAN: {bill_data['pan']}, GSTIN: {bill_data['gstin']} and Account No: {bill_data['account_no']}"), ln=1)
    pdf.ln(5)
    
    # Work Details
    pdf.cell(0, 5, safe_text(f"on account of {bill_data['cc_bill']} for {bill_data['work_description']}"), ln=1)
    pdf.cell(0, 5, safe_text(f"AAA No: {bill_data['aaa_no']} Dated: {bill_data['aaa_date']} for Rs. {bill_data['aaa_amount']:,}"), ln=1)
    pdf.cell(0, 5, safe_text(f"TS No: {bill_data['ts_no']} Dated: {bill_data['ts_date']} for Rs. {bill_data['ts_amount']:,}"), ln=1)
    pdf.ln(5)
    
    # Financial Details
    pdf.cell(0, 5, safe_text(f"Billed Amount = Rs. {bill_data['billed_amount']:,}"), ln=1)
    pdf.cell(0, 5, safe_text(f"Deduct Last Payments = Rs. {bill_data['deduct_payments']:,}"), ln=1)
    pdf.cell(0, 5, safe_text(f"Payable Amount = Rs. {bill_data['payable']:,}"), ln=1)
    pdf.ln(5)
    
    # Deductions
    pdf.set_font('', 'B', 12)
    pdf.cell(0, 10, safe_text("DEDUCTIONS"), ln=1)
    pdf.set_font('', '', 10)
    pdf.cell(0, 5, safe_text(f"Cess @ {bill_data['cess_percent']}% = Rs. {bill_data['cess_amount']:,}"), ln=1)
    pdf.cell(0, 5, safe_text(f"I/Tax @ {bill_data['income_tax_percent']}% = Rs. {bill_data['income_tax_amount']:,}"), ln=1)
    pdf.cell(0, 5, safe_text(f"Deposit @ {bill_data['deposit_percent']}% = Rs. {bill_data['deposit_amount']:,}"), ln=1)
    pdf.cell(0, 5, safe_text(f"TOTAL Deduction = Rs. {bill_data['total_deduction']:,}"), ln=1)
    pdf.ln(5)
    
    # Save to temporary file
    temp_dir = tempfile.gettempdir()
    filename = os.path.join(temp_dir, f"PayOrder_{bill_data['bill_no']}.pdf")
    pdf.output(filename, 'F')
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
        if username == "admin" and password == "admin123":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid credentials")

# Main App
def main():
    st.title("Auto Payment System")
    st.caption("Version 2.0.1 | Designed & Developed by Mohammad Adham Wani")
    
    # Initialize session state for PDF
    if 'pdf_data' not in st.session_state:
        st.session_state.pdf_data = None
        st.session_state.bill_info = {}
    
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
            try:
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
                    
                    # Generate PDF
                    pdf_path = generate_payorder_pdf(pdf_data)
                    if pdf_path and os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as f:
                            st.session_state.pdf_data = f.read()
                        st.session_state.bill_info = pdf_data
                        os.remove(pdf_path)
                    else:
                        st.error("Failed to generate PDF")
            except Exception as e:
                st.error(f"Error saving bill: {str(e)}")
    
    # Download section outside the form
    if st.session_state.pdf_data:
        st.subheader("Download Bill")
        st.download_button(
            label="Download PayOrder PDF",
            data=st.session_state.pdf_data,
            file_name=f"PayOrder_{st.session_state.bill_info.get('bill_no', 'new')}.pdf",
            mime="application/pdf"
        )
        
        if st.button("Create New Bill"):
            st.session_state.pdf_data = None
            st.session_state.bill_info = {}
            st.rerun()

# [Other functions (show_dashboard, contractor_management, works_management, show_reports, show_settings) remain the same as in your original code]

# Run the app
if __name__ == "__main__":
    if check_auth():
        main()
    else:
        login()
