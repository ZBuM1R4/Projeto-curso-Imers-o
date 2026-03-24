FILLER_WORDS = [
    "né",
    "tipo",
    "então",
    "assim",
    "tá",
    "ah",
    "hum",
    #"é",
]


def analyze_filler_words(text: str) -> dict:
    texto_normalizado = (
        text.lower()
        .replace(",", "")
        .replace(".", "")
        .replace("!", "")
        .replace("?", "")
    )

    palavras = texto_normalizado.split()
    contagem = {}

    for filler in FILLER_WORDS:
        quantidade = palavras.count(filler)
        if quantidade > 0:
            contagem[filler] = quantidade

    return contagem