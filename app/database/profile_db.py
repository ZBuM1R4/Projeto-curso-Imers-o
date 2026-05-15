from app.services.supabase_client import get_supabase_client
from app.utils.validators import (
    is_valid_cep,
    is_valid_cpf,
    is_valid_phone,
    normalize_cep,
    normalize_cpf,
    normalize_phone,
)


def get_authenticated_client(access_token: str):
    client = get_supabase_client()
    client.postgrest.auth(access_token)
    return client


def save_profile(
    user_id: str,
    access_token: str,
    first_name: str,
    last_name: str,
    cpf: str,
    phone: str,
    cep: str,
    street: str = "",
    number: str = "",
    neighborhood: str = "",
    city: str = "",
    state: str = "",
    avatar_url: str = "",
):
    supabase = get_authenticated_client(access_token)

    clean_cpf = normalize_cpf(cpf)
    clean_phone = normalize_phone(phone)
    clean_cep = normalize_cep(cep)

    if not first_name or len(first_name.strip()) < 2:
        return {"success": False, "message": "Informe um nome válido."}

    if not last_name or len(last_name.strip()) < 2:
        return {"success": False, "message": "Informe um sobrenome válido."}

    if not is_valid_cpf(clean_cpf):
        return {"success": False, "message": "Informe um CPF válido."}

    if not is_valid_phone(clean_phone):
        return {"success": False, "message": "Informe um telefone válido."}

    if not is_valid_cep(clean_cep):
        return {"success": False, "message": "Informe um CEP válido."}

    data = {
        "id": user_id,
        "first_name": first_name.strip(),
        "last_name": last_name.strip(),
        "cpf": clean_cpf,
        "phone": clean_phone,
        "cep": clean_cep,
        "street": street.strip() if street else "",
        "number": number.strip() if number else "",
        "neighborhood": neighborhood.strip() if neighborhood else "",
        "city": city.strip() if city else "",
        "state": state.strip().upper() if state else "",
        "avatar_url": avatar_url,
    }

    try:
        supabase.table("profiles").upsert(data).execute()
        return {"success": True, "message": "Perfil salvo com sucesso."}

    except Exception as e:
        error_message = str(e).lower()

        if "duplicate" in error_message and "cpf" in error_message:
            return {"success": False, "message": "Este CPF já está cadastrado."}

        return {
            "success": False,
            "message": "Erro ao salvar perfil. Verifique os dados e tente novamente."
        }


def get_profile(user_id: str, access_token: str):
    supabase = get_authenticated_client(access_token)

    try:
        response = (
            supabase
            .table("profiles")
            .select("*")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    except Exception:
        return None


def profile_exists(user_id: str, access_token: str) -> bool:
    return get_profile(user_id, access_token) is not None