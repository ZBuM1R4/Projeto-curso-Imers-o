import os
import time
import urllib.error
import urllib.parse
import urllib.request


AVATAR_BUCKET = "profile-images"


def get_supabase_storage_settings() -> tuple[str, str]:
    supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
    supabase_key = (
        os.getenv("SUPABASE_KEY")
        or os.getenv("SUPABASE_ANON_KEY")
        or ""
    )

    if not supabase_url:
        raise ValueError("SUPABASE_URL não configurada.")

    if not supabase_key:
        raise ValueError("SUPABASE_KEY não configurada.")

    return supabase_url, supabase_key


def get_content_type(uploaded_file) -> str:
    content_type = getattr(uploaded_file, "type", "") or ""

    allowed_types = {
        "image/png",
        "image/jpeg",
        "image/webp",
    }

    if content_type in allowed_types:
        return content_type

    return "image/png"


def upload_avatar_image_to_storage(
    uploaded_file,
    user_id: str,
    access_token: str
) -> str:
    if uploaded_file is None:
        return ""

    if not user_id:
        raise ValueError("Usuário não identificado.")

    if not access_token:
        raise ValueError("Token de acesso não encontrado.")

    supabase_url, supabase_key = get_supabase_storage_settings()

    storage_path = f"{user_id}/avatar"
    encoded_path = urllib.parse.quote(storage_path, safe="/")

    upload_url = (
        f"{supabase_url}/storage/v1/object/"
        f"{AVATAR_BUCKET}/{encoded_path}"
    )

    file_bytes = uploaded_file.getvalue()
    content_type = get_content_type(uploaded_file)

    request = urllib.request.Request(
        upload_url,
        data=file_bytes,
        method="POST",
        headers={
            "apikey": supabase_key,
            "Authorization": f"Bearer {access_token}",
            "Content-Type": content_type,
            "x-upsert": "true",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30):
            pass

    except urllib.error.HTTPError as error:
        error_message = error.read().decode("utf-8", errors="ignore")
        raise RuntimeError(
            f"Erro ao enviar foto para o Supabase Storage: {error_message}"
        ) from error

    public_url = (
        f"{supabase_url}/storage/v1/object/public/"
        f"{AVATAR_BUCKET}/{encoded_path}"
        f"?v={int(time.time())}"
    )

    return public_url