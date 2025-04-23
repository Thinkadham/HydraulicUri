from supabase import create_client
from hydraulicuri.config import Config

supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

def get_works():
    """Fetch all works from Supabase"""
    try:
        return supabase.table("works").select("*").execute().data
    except Exception as e:
        print(f"Error fetching works: {e}")
        return []

def add_work(work_data):
    """Add a new work to Supabase"""
    try:
        result = supabase.table("works").insert(work_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error adding work: {e}")
        return None
