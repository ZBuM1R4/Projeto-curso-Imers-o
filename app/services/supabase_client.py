import os

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


def get_supabase_client() -> Client:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL ou SUPABASE_KEY não configurados no .env")

    return create_client(supabase_url, supabase_key)