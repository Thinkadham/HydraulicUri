import streamlit as st
import pandas as pd
from services.bill_service import get_recent_bills
from services.contractor_service import get_contractors
from services.work_service import get_works

def show():
    st.header("Dashboard")
    
    contractors = get_contractors()
    works = get_works()
    bills = get_recent_bills()
    
    # Dashboard widgets implementation...
