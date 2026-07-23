from app.services.supabase_client import get_supabase_client


def is_admin_user(user_id: str, access_token: str) -> bool:
    if not user_id or not access_token:
        return False

    supabase = get_supabase_client()
    supabase.postgrest.auth(access_token)

    response = (
        supabase
        .table("admin_users")
        .select("id")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )

    return bool(response.data)