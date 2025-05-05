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
    if not url or not key:
        st.error("Supabase URL or Key not found. Please set SUPABASE_URL and SUPABASE_KEY environment variables.")
        return None
    return create_client(url, key)

# Removed: supabase = init_supabase() - Initialize inside functions instead

def get_contractors():
    supabase = init_supabase()
    if not supabase: return [] # Handle initialization failure
    return supabase.table("contractors").select("*").execute().data

def get_works():
    supabase = init_supabase()
    if not supabase: return []
    return supabase.table("works").select("*").execute().data

def get_bills():
    supabase = init_supabase()
    if not supabase: return []
    return supabase.table("bills").select("*").execute().data

def get_budget_np():
    supabase = init_supabase()
    if not supabase: return []
    return supabase.table("budget_np").select("*").execute().data

def get_budget_plan():
    supabase = init_supabase()
    supabase = init_supabase()
    if not supabase: return []
    return supabase.table("budget_plan").select("*").execute().data

def insert_bill(bill_data):
    supabase = init_supabase()
    if not supabase: return None # Indicate failure
    return supabase.table("bills").insert(bill_data).execute()

def update_work_expenditure(work_id, new_expenditure):
    supabase = init_supabase()
    if not supabase: return None
    return supabase.table("works").update({"expenditure": new_expenditure}).eq("id", work_id).execute()

def insert_contractor(contractor_data):
    supabase = init_supabase()
    if not supabase: return None
    return supabase.table("contractors").insert(contractor_data).execute()

def insert_work(work_data):
    supabase = init_supabase()
    if not supabase: return None
    return supabase.table("works").insert(work_data).execute()

# --- User Management Functions ---

def add_user(username, hashed_password, role, allowed_pages=None):
    """Adds a new user to the 'users_hydraulicuri' table."""
    supabase = init_supabase()
    if not supabase:
        return None # Indicate failure if client initialization fails

    # Ensure allowed_pages is None for admins, or an array for restricted
    if role == 'admin':
        allowed_pages_data = None
    elif allowed_pages is None: # Default for restricted if not provided
         allowed_pages_data = ['Dashboard'] # Default restricted users to Dashboard only
    else:
        allowed_pages_data = list(allowed_pages) # Ensure it's a list

    user_data = {
        "username": username,
        "hashed_password": hashed_password,
        "role": role,
        "allowed_pages": allowed_pages_data # Add the new field
    }
    try:
        # Consider adding more specific error handling for duplicate usernames etc.
        return supabase.table("users_hydraulicuri").insert(user_data).execute()
    except Exception as e:
        st.error(f"Database error adding user: {e}")
        return None # Indicate failure

def get_users():
    """Retrieves all users from the 'users_hydraulicuri' table, excluding passwords."""
    supabase = init_supabase()
    if not supabase: return []
    # Select only username and role for security
    return supabase.table("users_hydraulicuri").select("username, role").execute().data

# You might also need a function to get a specific user by username for login
def get_user_by_username(username):
    """Retrieves a single user by username, including hashed password and allowed pages."""
    supabase = init_supabase()
    if not supabase: return [] # Return empty list if client fails
    # Select all columns including the new 'allowed_pages'
    return supabase.table("users_hydraulicuri").select("*").eq("username", username).execute().data

def update_user_permissions(username, allowed_pages):
    """Updates the allowed pages for a specific user."""
    supabase = init_supabase()
    if not supabase: return None
    try:
        # Ensure allowed_pages is a list
        if allowed_pages is None:
            pages_to_set = []
        else:
            pages_to_set = list(allowed_pages)

        return supabase.table("users_hydraulicuri") \
                       .update({"allowed_pages": pages_to_set}) \
                       .eq("username", username) \
                       .execute()
    except Exception as e:
        st.error(f"Database error updating permissions for {username}: {e}")
        return None
