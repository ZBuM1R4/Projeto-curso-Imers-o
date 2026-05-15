import re


def only_digits(value: str) -> str:
    if not value:
        return ""

    return re.sub(r"\D", "", value)


def normalize_cpf(cpf: str) -> str:
    return only_digits(cpf)


def normalize_phone(phone: str) -> str:
    return only_digits(phone)


def normalize_cep(cep: str) -> str:
    return only_digits(cep)


def is_valid_cpf(cpf: str) -> bool:
    cpf = normalize_cpf(cpf)

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    sum_first_digit = 0
    for i in range(9):
        sum_first_digit += int(cpf[i]) * (10 - i)

    first_digit = (sum_first_digit * 10) % 11
    if first_digit == 10:
        first_digit = 0

    if first_digit != int(cpf[9]):
        return False

    sum_second_digit = 0
    for i in range(10):
        sum_second_digit += int(cpf[i]) * (11 - i)

    second_digit = (sum_second_digit * 10) % 11
    if second_digit == 10:
        second_digit = 0

    return second_digit == int(cpf[10])


def is_valid_cep(cep: str) -> bool:
    cep = normalize_cep(cep)
    return len(cep) == 8


def is_valid_phone(phone: str) -> bool:
    phone = normalize_phone(phone)

    # Brasil com DDI: 55 + DDD + número
    if phone.startswith("55"):
        return 12 <= len(phone) <= 13

    # Brasil sem DDI: DDD + número
    return 10 <= len(phone) <= 11


def is_valid_password(password: str) -> bool:
    if not password:
        return False

    if len(password) < 8 or len(password) > 64:
        return False

    has_upper = any(char.isupper() for char in password)
    has_number = any(char.isdigit() for char in password)
    has_special = any(not char.isalnum() for char in password)

    return has_upper and has_number and has_special


def get_password_rules_message() -> str:
    return (
        "A senha deve ter entre 8 e 64 caracteres, "
        "com pelo menos uma letra maiúscula, um número e um caractere especial."
    )