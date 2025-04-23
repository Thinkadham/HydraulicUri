from supabase import create_client
from config import Config

supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

def get_contractors():
    """Fetch all contractors from Supabase"""
    try:
        return supabase.table("contractors").select("*").execute().data
    except Exception as e:
        print(f"Error fetching contractors: {e}")
        return []

def add_contractor(contractor_data):
    """Add a new contractor to Supabase"""
    try:
        result = supabase.table("contractors").insert(contractor_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error adding contractor: {e}")
        return None
