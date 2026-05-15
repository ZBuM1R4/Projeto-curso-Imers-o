import re


def only_digits(value: str) -> str:
    if not value:
        return ""
    return re.sub(r"\D", "", value)


def format_cpf(value: str) -> str:
    digits = only_digits(value)[:11]

    if len(digits) <= 3:
        return digits
    if len(digits) <= 6:
        return f"{digits[:3]}.{digits[3:]}"
    if len(digits) <= 9:
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:]}"
    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"


def format_cep(value: str) -> str:
    digits = only_digits(value)[:8]

    if len(digits) <= 5:
        return digits

    return f"{digits[:5]}-{digits[5:]}"


def format_phone_br(value: str) -> str:
    digits = only_digits(value)

    if digits.startswith("55"):
        digits = digits[2:]

    digits = digits[:11]

    if len(digits) <= 2:
        return f"+55 ({digits}"

    if len(digits) <= 7:
        return f"+55 ({digits[:2]}) {digits[2:]}"

    return f"+55 ({digits[:2]}) {digits[2:7]}-{digits[7:]}"


def normalize_phone_br(value: str) -> str:
    digits = only_digits(value)

    if digits.startswith("55"):
        return digits

    return f"55{digits}"