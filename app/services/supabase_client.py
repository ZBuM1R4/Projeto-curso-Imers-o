import os

from dotenv import load_dotenv
from supabase import Client, create_client


load_dotenv()


def get_supabase_settings() -> tuple[str, str]:
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = (
        os.getenv("SUPABASE_KEY")
        or os.getenv("SUPABASE_ANON_KEY")
        or ""
    ).strip()

    if not supabase_url:
        raise ValueError(
            "SUPABASE_URL não configurada nas variáveis de ambiente."
        )

    if not supabase_key:
        raise ValueError(
            "SUPABASE_KEY ou SUPABASE_ANON_KEY não configurada nas variáveis de ambiente."
        )

    return supabase_url, supabase_key


def get_supabase_client() -> Client:
    supabase_url, supabase_key = get_supabase_settings()

    return create_client(supabase_url, supabase_key)