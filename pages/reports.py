import streamlit as st
import pandas as pd
import datetime
import io  # Import io for BytesIO
from fpdf import FPDF
from utils.db import get_bills, get_works
# Remove comp_key import and FormManager instantiation

def show_reports():
    st.header("Reports")
    
    # Remove explicit key from st.form
    with st.form(key="reports_form", clear_on_submit=True): # Use a simple string key or let Streamlit manage
        report_type = st.selectbox(
            "Select Report Type", 
            options=["Payment Register", "Contractor Wise Payments", 
                    "Scheme Wise Expenditure", "Deduction Register"]
            # Removed key argument
        )
        
        date_range = st.date_input(
            "Select Date Range", 
            value=[datetime.date.today() - datetime.timedelta(days=30), 
                  datetime.date.today()]
            # Removed key argument
        )
        # The submit button is the *last* element in the form definition
        submitted = st.form_submit_button("Generate Report")

    # --- Form definition ends here ---

    # Process and display results *outside* the form, only if submitted
    if submitted:
        start_date, end_date = date_range
        all_bills = get_bills() 
        works = get_works() 

        bills_df = pd.DataFrame(all_bills)
        data = pd.DataFrame() # Initialize data as an empty DataFrame

        # Ensure 'created_at' is datetime for comparison and filter
        if not bills_df.empty and 'created_at' in bills_df.columns:
            try:
                bills_df['created_at'] = pd.to_datetime(bills_df['created_at']).dt.date
                # Filter by date range
                bills_df = bills_df[
                    (bills_df['created_at'] >= start_date) & 
                    (bills_df['created_at'] <= end_date)
                ]
            except Exception as e:
                st.error(f"Error converting/filtering 'created_at' column: {e}")
                bills_df = pd.DataFrame() # Reset df on error
        
        # Process based on report type using the filtered bills_df
        if not bills_df.empty:
            if report_type == "Payment Register":
                data = bills_df[["bill_no", "created_at", "payee", "work", "payable", "status"]]
                data.columns = ["Bill No", "Date", "Payee", "Work", "Amount", "Status"]
            elif report_type == "Contractor Wise Payments":
                data = bills_df.groupby("payee").agg(
                    total_bills=pd.NamedAgg(column="payable", aggfunc="count"),
                    total_amount=pd.NamedAgg(column="payable", aggfunc="sum"),
                    last_payment_date=pd.NamedAgg(column="created_at", aggfunc="max")
                ).reset_index()
                data.columns = ["Contractor", "Total Bills", "Total Amount", "Last Payment Date"]
            elif report_type == "Deduction Register":
                 temp_data = bills_df[["bill_no", "created_at", "payee", "income_tax_amount", 
                                "deposit_amount", "cess_amount"]].copy()
                 temp_data["total_deduction"] = (temp_data.get("income_tax_amount", 0).fillna(0) + 
                                                temp_data.get("deposit_amount", 0).fillna(0) + 
                                                temp_data.get("cess_amount", 0).fillna(0))
                 data = temp_data[["bill_no", "created_at", "payee", "income_tax_amount", 
                                "deposit_amount", "cess_amount", "total_deduction"]]
                 data.columns = ["Bill No", "Date", "Payee", "Income Tax", 
                               "Deposit", "Cess", "Total Deduction"]
        
        # Scheme Wise Expenditure uses 'works' data, handle separately
        if report_type == "Scheme Wise Expenditure":
            if works:
                works_df = pd.DataFrame(works)
                # Ensure required columns exist before grouping
                if all(col in works_df.columns for col in ["scheme", "allotment_amount", "expenditure"]):
                    data = works_df.groupby("scheme").agg(
                        allocated=pd.NamedAgg(column="allotment_amount", aggfunc="sum"),
                        utilized=pd.NamedAgg(column="expenditure", aggfunc="sum")
                    ).reset_index()
                    data["balance"] = data["allocated"] - data["utilized"]
                    # Avoid division by zero
                    data["utilization_percent"] = (data["utilized"] / data["allocated"].replace(0, pd.NA) * 100).fillna(0) 
                    data.columns = ["Scheme", "Allocated", "Utilized", "Balance", "Utilization %"]
                else:
                    st.error("Works data is missing required columns (scheme, allotment_amount, expenditure).")
                    data = pd.DataFrame() # Ensure data is empty df on error
            else:
                data = pd.DataFrame() # No works data

        # Display results and export options
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

            # Format date columns for PDF export if they exist
            if 'Date' in data.columns:
                data['Date'] = pd.to_datetime(data['Date']).dt.strftime('%d/%m/%Y')
            if 'Last Payment Date' in data.columns:
                data['Last Payment Date'] = pd.to_datetime(data['Last Payment Date']).dt.strftime('%d/%m/%Y')

            # Export options - Removed CSV, now 2 columns
            export_col1, export_col2 = st.columns(2)
            with export_col1: # Was export_col2
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                     data.to_excel(writer, index=False, sheet_name='Report')
                excel_data = output.getvalue()
                st.download_button(
                    label="Download Excel",
                    data=excel_data,
                    file_name=f"{report_type.lower().replace(' ', '_')}_report.xlsx", # Use keyword arg
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" # Use keyword arg
                )
            with export_col2: # Was export_col3
                # Generate PDF data
                pdf_title = f"{report_type} Report ({start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')})"
                # Pass original data (before date formatting) to PDF function if needed,
                # or handle formatting within PDF function. Here we pass the potentially modified 'data'.
                pdf_data = create_pdf_report(data.copy(), pdf_title) # Pass a copy to avoid modifying original df further
                st.download_button(
                    label="Download PDF",
                    data=pdf_data,
                    file_name=f"{report_type.lower().replace(' ', '_')}_report.pdf",
                    mime="application/pdf"
                )
        else:
            # Display warning only if no data was generated for the selected report type
            # Avoid showing warning if bills_df was empty but works_df might have data (for Scheme Wise)
            if report_type != "Scheme Wise Expenditure" or not works:
                 st.warning("No data found for the selected criteria")

# --- PDF Generation Helper ---
class PDF(FPDF):
    def header(self):
        # Add DejaVu font (assuming it's in the fonts/ directory relative to script execution)
        try:
            self.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
            self.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf', uni=True)
            self.set_font('DejaVu', 'B', 12)
        except RuntimeError:
            # Fallback if font file not found
            self.set_font('Arial', 'B', 12)
            st.warning("DejaVu font not found. Using Arial for PDF header (may affect special characters).")

        # Title - Get title from instance variable
        self.cell(0, 10, self.report_title, 0, 1, 'C')
        self.ln(5) # Add a little space after the header

    def footer(self):
        self.set_y(-15)
        try:
            self.set_font('DejaVu', '', 8)
        except RuntimeError:
            self.set_font('Arial', '', 8) # Fallback
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        try:
            self.set_font('DejaVu', 'B', 12)
        except RuntimeError:
            self.set_font('Arial', 'B', 12) # Fallback
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, df):
        try:
            self.set_font('DejaVu', '', 10)
            # Determine column widths dynamically (simple equal distribution)
            col_width = self.w / (len(df.columns) * 1.1) # Adjust multiplier as needed
            line_height = self.font_size * 1.5

            # Define currency columns
            currency_columns = ["Amount", "Total Amount", "Allocated", "Utilized", "Balance",
                                "Income Tax", "Deposit", "Cess", "Total Deduction"] # Added deduction columns

            # Table Header
            self.set_font('DejaVu', 'B', 10)
            col_names = df.columns.tolist() # Get column names
            for col_name in col_names:
                self.cell(col_width, line_height, str(col_name), border=1)
            self.ln(line_height)
            self.set_font('DejaVu', '', 10)

            # Table Body
            for index, row in df.iterrows():
                for i, item in enumerate(row):
                    col_name = col_names[i] # Get current column name
                    # Handle potential None values and convert to string
                    cell_text = str(item) if item is not None else ''
                    # Prepend Rupee symbol if it's a currency column and not empty
                    if col_name in currency_columns and cell_text:
                        try:
                            # Attempt to format as currency, handle potential errors
                            # Check if it's already formatted (e.g., from dataframe config - unlikely here)
                            if not cell_text.startswith('₹'):
                                # Basic check if it looks like a number before formatting
                                float(cell_text) # Raises ValueError if not convertible
                                cell_text = f"₹{float(cell_text):,.2f}"
                        except ValueError:
                            pass # Keep original text if it's not a number
                        except Exception as e:
                            st.warning(f"Could not format currency value '{item}' in column '{col_name}': {e}") # Log other errors
                            pass # Keep original text on other errors
                    self.cell(col_width, line_height, cell_text, border=1)
                self.ln(line_height)
        except RuntimeError:
            st.error("DejaVu font not found. PDF generation failed.")
            return # Stop processing if font is missing

def create_pdf_report(data, title):
    pdf = PDF(orientation='L', unit='mm', format='A4') # Landscape for wider tables
    pdf.report_title = title # Pass title to the PDF class instance
    pdf.add_page()
    pdf.chapter_body(data)
    # Ensure the output is explicitly bytes for Streamlit
    return bytes(pdf.output(dest='S'))

# --- End PDF Generation Helper ---


def show_reports():
    st.header("Reports")

    # Remove explicit key from st.form
    with st.form("reports_form"): # Use a simple string key or let Streamlit manage
        report_type = st.selectbox(
            "Select Report Type",
            options=["Payment Register", "Contractor Wise Payments",
                    "Scheme Wise Expenditure", "Deduction Register"]
            # Removed key argument
        )

        date_range = st.date_input(
            "Select Date Range",
            value=[datetime.date.today() - datetime.timedelta(days=30),
                  datetime.date.today()]
            # Removed key argument
        )
        # The submit button is the *last* element in the form definition
        submitted = st.form_submit_button("Generate Report")

    # --- Form definition ends here ---

    # Process and display results *outside* the form, only if submitted
    if submitted:
        start_date, end_date = date_range
        all_bills = get_bills()
        works = get_works()

        bills_df = pd.DataFrame(all_bills)
        data = pd.DataFrame() # Initialize data as an empty DataFrame

        # Ensure 'created_at' is datetime for comparison and filter
        if not bills_df.empty and 'created_at' in bills_df.columns:
            try:
                bills_df['created_at'] = pd.to_datetime(bills_df['created_at']).dt.date
                # Filter by date range
                bills_df = bills_df[
                    (bills_df['created_at'] >= start_date) &
                    (bills_df['created_at'] <= end_date)
                ]
            except Exception as e:
                st.error(f"Error converting/filtering 'created_at' column: {e}")
                bills_df = pd.DataFrame() # Reset df on error

        # Process based on report type using the filtered bills_df
        if not bills_df.empty:
            if report_type == "Payment Register":
                data = bills_df[["bill_no", "created_at", "payee", "work", "payable", "status"]]
                data.columns = ["Bill No", "Date", "Payee", "Work", "Amount", "Status"]
            elif report_type == "Contractor Wise Payments":
                data = bills_df.groupby("payee").agg(
                    total_bills=pd.NamedAgg(column="payable", aggfunc="count"),
                    total_amount=pd.NamedAgg(column="payable", aggfunc="sum"),
                    last_payment_date=pd.NamedAgg(column="created_at", aggfunc="max")
                ).reset_index()
                data.columns = ["Contractor", "Total Bills", "Total Amount", "Last Payment Date"]
            elif report_type == "Deduction Register":
                 temp_data = bills_df[["bill_no", "created_at", "payee", "income_tax_amount",
                                "deposit_amount", "cess_amount"]].copy()
                 temp_data["total_deduction"] = (temp_data.get("income_tax_amount", 0).fillna(0) +
                                                temp_data.get("deposit_amount", 0).fillna(0) +
                                                temp_data.get("cess_amount", 0).fillna(0))
                 data = temp_data[["bill_no", "created_at", "payee", "income_tax_amount",
                                "deposit_amount", "cess_amount", "total_deduction"]]
                 data.columns = ["Bill No", "Date", "Payee", "Income Tax",
                               "Deposit", "Cess", "Total Deduction"]

        # Scheme Wise Expenditure uses 'works' data, handle separately
        if report_type == "Scheme Wise Expenditure":
            if works:
                works_df = pd.DataFrame(works)
                # Ensure required columns exist before grouping
                if all(col in works_df.columns for col in ["scheme", "allotment_amount", "expenditure"]):
                    data = works_df.groupby("scheme").agg(
                        allocated=pd.NamedAgg(column="allotment_amount", aggfunc="sum"),
                        utilized=pd.NamedAgg(column="expenditure", aggfunc="sum")
                    ).reset_index()
                    data["balance"] = data["allocated"] - data["utilized"]
                    # Avoid division by zero
                    data["utilization_percent"] = (data["utilized"] / data["allocated"].replace(0, pd.NA) * 100).fillna(0)
                    data.columns = ["Scheme", "Allocated", "Utilized", "Balance", "Utilization %"]
                else:
                    st.error("Works data is missing required columns (scheme, allotment_amount, expenditure).")
                    data = pd.DataFrame() # Ensure data is empty df on error
            else:
                data = pd.DataFrame() # No works data

        # Display results and export options
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

            # Format date columns for PDF export if they exist
            if 'Date' in data.columns:
                data['Date'] = pd.to_datetime(data['Date']).dt.strftime('%d/%m/%Y')
            if 'Last Payment Date' in data.columns:
                data['Last Payment Date'] = pd.to_datetime(data['Last Payment Date']).dt.strftime('%d/%m/%Y')

            # Export options
            export_col2, export_col3 = st.columns(2)
            # with export_col1:
            #    st.download_button(
            #        label="Download CSV",
            #        data=data.to_csv(index=False).encode('utf-8'),
            #        file_name=f"{report_type.lower().replace(' ', '_')}_report.csv", # Use keyword arg
            #        mime="text/csv" # Use keyword arg
            #    )
            with export_col2:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                     data.to_excel(writer, index=False, sheet_name='Report')
                excel_data = output.getvalue()
                st.download_button(
                    label="Download Excel",
                    data=excel_data,
                    file_name=f"{report_type.lower().replace(' ', '_')}_report.xlsx", # Use keyword arg
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" # Use keyword arg
                )
            with export_col3:
                # Generate PDF data
                pdf_title = f"{report_type} Report ({start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')})"
                pdf_data = create_pdf_report(data, pdf_title)
                st.download_button(
                    label="Download PDF",
                    data=pdf_data,
                    file_name=f"{report_type.lower().replace(' ', '_')}_report.pdf",
                    mime="application/pdf"
                )
        else:
            # Display warning only if no data was generated for the selected report type
            # Avoid showing warning if bills_df was empty but works_df might have data (for Scheme Wise)
            # Check if 'data' is empty AND (it wasn't Scheme Wise OR works data was also empty)
            if data.empty and (report_type != "Scheme Wise Expenditure" or not works):
                 st.warning("No data found for the selected criteria")

# Remove the direct call to show_reports()
# Assuming app.py handles calling the page function
# show_reports()
