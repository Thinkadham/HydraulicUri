import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

# Database setup and initialization
def init_db():
    conn = sqlite3.connect('billing.db', check_same_thread=False)
    c = conn.cursor()
    
    # Create tables if they don't exist
    c.execute('''CREATE TABLE IF NOT EXISTS customers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 name TEXT NOT NULL, 
                 email TEXT, 
                 phone TEXT, 
                 address TEXT,
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 description TEXT,
                 price REAL NOT NULL,
                 tax_rate REAL DEFAULT 0.0,
                 active INTEGER DEFAULT 1)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS invoices
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 customer_id INTEGER NOT NULL,
                 invoice_number TEXT UNIQUE,
                 date TEXT NOT NULL,
                 due_date TEXT NOT NULL,
                 total REAL NOT NULL,
                 tax_amount REAL DEFAULT 0.0,
                 status TEXT DEFAULT 'Pending',
                 notes TEXT,
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY (customer_id) REFERENCES customers (id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS invoice_items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 invoice_id INTEGER NOT NULL,
                 product_id INTEGER,
                 description TEXT NOT NULL,
                 quantity REAL NOT NULL,
                 unit_price REAL NOT NULL,
                 tax_rate REAL DEFAULT 0.0,
                 FOREIGN KEY (invoice_id) REFERENCES invoices (id),
                 FOREIGN KEY (product_id) REFERENCES products (id))''')
    
    conn.commit()
    return conn

# Customer management functions
def manage_customers(conn):
    st.header("Customer Management")
    
    action = st.radio("Action", ["View Customers", "Add New Customer", "Edit Customer"], horizontal=True)
    
    if action == "View Customers":
        customers = pd.read_sql("SELECT * FROM customers ORDER BY name", conn)
        st.dataframe(customers, use_container_width=True)
        
    elif action == "Add New Customer":
        with st.form("add_customer"):
            name = st.text_input("Full Name*", max_chars=100)
            email = st.text_input("Email", max_chars=100)
            phone = st.text_input("Phone", max_chars=20)
            address = st.text_area("Address")
            
            if st.form_submit_button("Add Customer"):
                if name:
                    conn.execute("INSERT INTO customers (name, email, phone, address) VALUES (?, ?, ?, ?)",
                               (name, email, phone, address))
                    conn.commit()
                    st.success("Customer added successfully!")
                else:
                    st.error("Name is required")
                    
    elif action == "Edit Customer":
        customers = conn.execute("SELECT id, name FROM customers ORDER BY name").fetchall()
        if customers:
            customer_options = {f"{name} (ID: {id})": id for id, name in customers}
            selected = st.selectbox("Select Customer", options=list(customer_options.keys()))
            customer_id = customer_options[selected]
            
            customer_data = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
            if customer_data:
                with st.form("edit_customer"):
                    name = st.text_input("Full Name*", value=customer_data[1], max_chars=100)
                    email = st.text_input("Email", value=customer_data[2] or "", max_chars=100)
                    phone = st.text_input("Phone", value=customer_data[3] or "", max_chars=20)
                    address = st.text_area("Address", value=customer_data[4] or "")
                    
                    if st.form_submit_button("Update Customer"):
                        if name:
                            conn.execute("UPDATE customers SET name = ?, email = ?, phone = ?, address = ? WHERE id = ?",
                                        (name, email, phone, address, customer_id))
                            conn.commit()
                            st.success("Customer updated successfully!")
                        else:
                            st.error("Name is required")
        else:
            st.warning("No customers found")

# Invoice creation functions
def create_invoice(conn):
    st.header("Create New Invoice")
    
    # Generate invoice number (YYYYMMDD-001 format)
    today = datetime.now().strftime("%Y%m%d")
    last_invoice = conn.execute("SELECT invoice_number FROM invoices WHERE invoice_number LIKE ? ORDER BY id DESC LIMIT 1",
                               (f"{today}%",)).fetchone()
    if last_invoice:
        last_num = int(last_invoice[0][-3:])
        new_num = f"{today}-{last_num + 1:03d}"
    else:
        new_num = f"{today}-001"
    
    # Customer selection
    customers = conn.execute("SELECT id, name FROM customers ORDER BY name").fetchall()
    if not customers:
        st.warning("No customers found. Please add customers first.")
        return
    
    customer_options = {f"{name} (ID: {id})": id for id, name in customers}
    customer = st.selectbox("Customer*", options=list(customer_options.keys()))
    customer_id = customer_options[customer]
    
    # Date selection
    col1, col2 = st.columns(2)
    with col1:
        invoice_date = st.date_input("Invoice Date*", datetime.now())
    with col2:
        due_date = st.date_input("Due Date*", datetime.now() + timedelta(days=30))
    
    # Product selection
    st.subheader("Invoice Items")
    products = conn.execute("SELECT id, name, price FROM products WHERE active = 1").fetchall()
    product_options = {f"{name} (${price:.2f})": (id, price) for id, name, price in products}
    
    items = []
    for i in range(1, 6):  # Allow up to 5 items by default
        with st.expander(f"Item {i}", expanded=i==1):
            cols = st.columns([4, 2, 2, 2])
            
            with cols[0]:
                product_choice = st.selectbox(
                    "Product/Service", 
                    options=["Custom Item"] + list(product_options.keys()),
                    key=f"product_{i}"
                )
                
                if product_choice == "Custom Item":
                    description = st.text_input("Description*", key=f"desc_{i}")
                    product_id = None
                    unit_price = st.number_input("Unit Price*", min_value=0.0, value=0.0, key=f"price_{i}")
                else:
                    product_id, unit_price = product_options[product_choice]
                    description = product_choice.split(" (")[0]
                    st.text_input("Description", value=description, key=f"desc_{i}", disabled=True)
            
            with cols[1]:
                quantity = st.number_input("Qty*", min_value=1, value=1, key=f"qty_{i}")
            
            with cols[2]:
                tax_rate = st.number_input("Tax Rate %", min_value=0.0, value=0.0, key=f"tax_{i}") / 100
            
            with cols[3]:
                st.write("##")  # Vertical alignment
                if st.button("Add Item", key=f"add_{i}"):
                    if description:
                        items.append({
                            "product_id": product_id,
                            "description": description,
                            "quantity": quantity,
                            "unit_price": unit_price,
                            "tax_rate": tax_rate
                        })
                        st.success("Item added!")
                    else:
                        st.error("Description is required")
    
    # Display added items
    if items:
        st.subheader("Current Items")
        item_df = pd.DataFrame(items)
        item_df["subtotal"] = item_df["quantity"] * item_df["unit_price"]
        item_df["tax_amount"] = item_df["subtotal"] * item_df["tax_rate"]
        item_df["total"] = item_df["subtotal"] + item_df["tax_amount"]
        st.dataframe(item_df, use_container_width=True)
        
        # Calculate totals
        subtotal = item_df["subtotal"].sum()
        total_tax = item_df["tax_amount"].sum()
        grand_total = item_df["total"].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Subtotal", f"${subtotal:,.2f}")
        col2.metric("Tax", f"${total_tax:,.2f}")
        col3.metric("Total", f"${grand_total:,.2f}", delta_color="off")
        
        # Notes and submission
        notes = st.text_area("Notes")
        
        if st.button("Create Invoice", type="primary"):
            try:
                # Save invoice
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO invoices 
                    (customer_id, invoice_number, date, due_date, total, tax_amount, status, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    customer_id, new_num, invoice_date.isoformat(), due_date.isoformat(),
                    grand_total, total_tax, "Pending", notes
                ))
                invoice_id = cur.lastrowid
                
                # Save items
                for item in items:
                    cur.execute("""
                        INSERT INTO invoice_items 
                        (invoice_id, product_id, description, quantity, unit_price, tax_rate)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        invoice_id, item["product_id"], item["description"], 
                        item["quantity"], item["unit_price"], item["tax_rate"]
                    ))
                
                conn.commit()
                st.success(f"Invoice #{new_num} created successfully!")
                st.balloons()
                
                # Show printable version
                st.subheader(f"Invoice #{new_num}")
                st.write(f"**Customer:** {customer}")
                st.write(f"**Date:** {invoice_date.strftime('%b %d, %Y')}")
                st.write(f"**Due Date:** {due_date.strftime('%b %d, %Y')}")
                st.dataframe(item_df, hide_index=True, use_container_width=True)
                st.write(f"**Notes:** {notes}")
                
            except Exception as e:
                conn.rollback()
                st.error(f"Error creating invoice: {e}")
    else:
        st.warning("Add at least one item to create an invoice")

# Dashboard functions
def show_dashboard(conn):
    st.header("Dashboard")
    
    # Summary cards
    col1, col2, col3 = st.columns(3)
    
    total_invoices = conn.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]
    col1.metric("Total Invoices", total_invoices)
    
    total_revenue = conn.execute("SELECT COALESCE(SUM(total), 0) FROM invoices").fetchone()[0]
    col2.metric("Total Revenue", f"${total_revenue:,.2f}")
    
    outstanding = conn.execute("""
        SELECT COALESCE(SUM(total), 0) 
        FROM invoices 
        WHERE status != 'Paid'
    """).fetchone()[0]
    col3.metric("Outstanding", f"${outstanding:,.2f}", delta=f"-{outstanding/total_revenue*100:.1f}%" if total_revenue else "0%")
    
    # Recent invoices
    st.subheader("Recent Invoices")
    recent_invoices = pd.read_sql("""
        SELECT i.invoice_number, c.name as customer, i.date, i.total, i.status
        FROM invoices i
        JOIN customers c ON i.customer_id = c.id
        ORDER BY i.date DESC
        LIMIT 10
    """, conn)
    st.dataframe(recent_invoices, use_container_width=True)
    
    # Monthly revenue chart
    st.subheader("Monthly Revenue")
    monthly_data = pd.read_sql("""
        SELECT strftime('%Y-%m', date) as month, 
               SUM(total) as revenue,
               SUM(tax_amount) as tax
        FROM invoices
        GROUP BY month
        ORDER BY month
    """, conn)
    
    if not monthly_data.empty:
        monthly_data["month"] = pd.to_datetime(monthly_data["month"])
        st.line_chart(monthly_data.set_index("month"))

# Reporting functions
def monthly_reports(conn):
    st.header("Monthly Reports")
    
    # Date selection
    col1, col2 = st.columns(2)
    with col1:
        year = st.selectbox("Year", options=range(2020, datetime.now().year + 1), index=datetime.now().year - 2020)
    with col2:
        month = st.selectbox("Month", options=range(1, 13), index=datetime.now().month - 1)
    
    report_date = datetime(year, month, 1)
    start_date = report_date.strftime("%Y-%m-%d")
    end_date = (report_date.replace(month=report_date.month + 1) if report_date.month < 12 else report_date.replace(year=report_date.year + 1, month=1))
    end_date = end_date.strftime("%Y-%m-%d")
    
    if st.button("Generate Report"):
        # Invoice summary
        st.subheader(f"Report for {report_date.strftime('%B %Y')}")
        
        # Summary stats
        summary = conn.execute("""
            SELECT 
                COUNT(*) as invoice_count,
                SUM(total) as total_revenue,
                SUM(tax_amount) as total_tax,
                SUM(CASE WHEN status = 'Paid' THEN total ELSE 0 END) as paid_amount
            FROM invoices
            WHERE date BETWEEN ? AND ?
        """, (start_date, end_date)).fetchone()
        
        if summary and summary[0] > 0:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Invoices", summary[0])
            col2.metric("Total Revenue", f"${summary[1]:,.2f}")
            col3.metric("Total Tax", f"${summary[2]:,.2f}")
            
            # Detailed invoices
            st.subheader("Invoice Details")
            invoices = pd.read_sql("""
                SELECT i.invoice_number, i.date, c.name as customer, 
                       i.total, i.tax_amount, i.status
                FROM invoices i
                JOIN customers c ON i.customer_id = c.id
                WHERE i.date BETWEEN ? AND ?
                ORDER BY i.date
            """, conn, params=(start_date, end_date))
            st.dataframe(invoices, use_container_width=True)
            
            # Export options
            csv = invoices.to_csv(index=False)
            st.download_button(
                "Export as CSV",
                data=csv,
                file_name=f"invoice_report_{start_date[:7]}.csv",
                mime="text/csv"
            )
        else:
            st.warning(f"No invoices found for {report_date.strftime('%B %Y')}")

# Main application
def main():
    st.set_page_config(
        page_title="Invoice Billing System",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize database
    if not os.path.exists('billing.db'):
        st.toast("Creating new database...")
    
    conn = init_db()
    
    # Add some sample data if empty
    if conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",
            [("John Doe", "john@example.com", "555-0101"),
             ("Jane Smith", "jane@example.com", "555-0102")]
        )
        conn.executemany(
            "INSERT INTO products (name, price) VALUES (?, ?)",
            [("Web Design", 500), ("Hosting", 50), ("Consulting", 150)]
        )
        conn.commit()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Billing App")
        st.image("https://via.placeholder.com/150", width=100)
        
        menu = ["Dashboard", "Create Invoice", "Customer Management", "Reports"]
        choice = st.radio("Navigation", menu)
        
        st.divider()
        st.write(f"Database: {os.path.abspath('billing.db')}")
        if st.button("Backup Database"):
            backup_file = f"billing_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            with open(backup_file, 'wb') as f:
                f.write(open('billing.db', 'rb').read())
            st.toast(f"Backup saved as {backup_file}")
    
    # Page routing
    if choice == "Dashboard":
        show_dashboard(conn)
    elif choice == "Create Invoice":
        create_invoice(conn)
    elif choice == "Customer Management":
        manage_customers(conn)
    elif choice == "Reports":
        monthly_reports(conn)
    
    conn.close()

if __name__ == "__main__":
    main()
