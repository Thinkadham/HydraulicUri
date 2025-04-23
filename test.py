import streamlit as st
from supabase import create_client, Client

# Supabase configuration
url = "YOUR_SUPABASE_URL"
key = "YOUR_SUPABASE_ANON_KEY"
supabase: Client = create_client(url, key)

# Streamlit app
st.title("Supabase Test App")

# Load data from Supabase
def load_data():
    data = supabase.table("bills").select("*").execute()
    return data.data

if st.button("Load Data"):
    data = load_data()
    st.write(data)
