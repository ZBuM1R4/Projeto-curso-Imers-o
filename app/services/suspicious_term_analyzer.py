from rapidfuzz import process, fuzz

TERMOS_TECNICOS = [
    "software",
    "hardware",
    "marketing",
    "mindset",
    "feedback",
    "networking",
    "performance",
    "desenvolvedor",
    "programação",
    "tecnologia",
]


def analyze_suspicious_terms(text: str, threshold: int = 70) -> list[dict]:
    palavras = text.lower().replace(",", "").replace(".", "").split()
    alertas = []

    for palavra in palavras:
        match = process.extractOne(
            palavra,
            TERMOS_TECNICOS,
            scorer=fuzz.ratio
        )

        if not match:
            continue

        termo_sugerido, score, _ = match

        if score >= threshold and palavra != termo_sugerido:
            alertas.append({
                "trecho": palavra,
                "tipo": "termo_suspeito",
                "sugestao": termo_sugerido,
                "similaridade": score
            })

    return alertas