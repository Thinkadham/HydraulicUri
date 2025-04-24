import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SUPABASE_URL = os.getenv("https://erxcqsswhljjccuytcoo.supabase.co")
    SUPABASE_KEY = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVyeGNxc3N3aGxqamNjdXl0Y29vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU0MTE4NDEsImV4cCI6MjA2MDk4Nzg0MX0.SXzmtAfecw1grfp6P8dFOPTeCRryK-ZXi3rDsFheDXE")
    FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")
