import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

supabase = init_supabase()

def get_contractors():
    return supabase.table("contractors").select("*").execute().data

def get_works():
    return supabase.table("works").select("*").execute().data

def get_bills():
    return supabase.table("bills").select("*").execute().data

def insert_bill(bill_data):
    return supabase.table("bills").insert(bill_data).execute()

def update_work_expenditure(work_id, new_expenditure):
    return supabase.table("works").update({"expenditure": new_expenditure}).eq("id", work_id).execute()

def insert_contractor(contractor_data):
    return supabase.table("contractors").insert(contractor_data).execute()

def insert_work(work_data):
    return supabase.table("works").insert(work_data).execute()
