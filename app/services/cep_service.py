import requests

from app.utils.validators import normalize_cep


def get_address_by_cep(cep: str) -> dict:
    clean_cep = normalize_cep(cep)

    if len(clean_cep) != 8:
        return {
            "success": False,
            "message": "CEP inválido.",
            "data": {}
        }

    try:
        response = requests.get(
            f"https://viacep.com.br/ws/{clean_cep}/json/",
            timeout=5
        )

        data = response.json()

        if data.get("erro"):
            return {
                "success": False,
                "message": "CEP não encontrado.",
                "data": {}
            }

        return {
            "success": True,
            "message": "CEP encontrado.",
            "data": {
                "street": data.get("logradouro", ""),
                "neighborhood": data.get("bairro", ""),
                "city": data.get("localidade", ""),
                "state": data.get("uf", ""),
            }
        }

    except Exception:
        return {
            "success": False,
            "message": "Erro ao buscar CEP. Verifique sua conexão.",
            "data": {}
        }