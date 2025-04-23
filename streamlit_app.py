# main.py
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Database setup
def init_db():
    conn = sqlite3.connect('billing.db', check_same_thread=False)
    # ... (table creation code from above)
    return conn

def main():
    st.set_page_config(page_title="Billing App", layout="wide")
    conn = init_db()
    
    st.title("Invoice Billing System")
    
    menu = ["Dashboard", "Create Invoice", "Customers", "Reports"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Dashboard":
        show_dashboard(conn)
    elif choice == "Create Invoice":
        create_invoice(conn)
    elif choice == "Customers":
        manage_customers(conn)
    elif choice == "Reports":
        monthly_reports(conn)
    
    conn.close()

if __name__ == "__main__":
    main()
