from supabase import create_client
from config import Config
from services.pdf_service import generate_payorder_pdf

supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

def create_bill(bill_data):
    # Insert bill and handle PDF generation
    result = supabase.table("bills").insert(bill_data).execute()
    if result.data:
        pdf_path = generate_payorder_pdf(bill_data)
        return result.data[0], pdf_path
    return None, None

def get_recent_bills(start_date=None, end_date=None):
    """Get bills filtered by date range"""
    query = supabase.table("bills").select("*")
    
    if start_date and end_date:
        query = query.gte("created_at", start_date.isoformat())
        query = query.lte("created_at", end_date.isoformat())
    
    result = query.execute()
    return result.data
