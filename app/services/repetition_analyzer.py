from collections import Counter

STOPWORDS = {
    "a", "o", "e", "é", "de", "do", "da", "dos", "das", "em", "um", "uma",
    "para", "com", "no", "na", "nos", "nas", "por", "que", "eu", "meu",
    "minha", "seu", "sua", "os", "as"
}


def normalize_text(text: str) -> list[str]:
    texto = (
        text.lower()
        .replace(",", "")
        .replace(".", "")
        .replace("!", "")
        .replace("?", "")
        .replace(";", "")
        .replace(":", "")
    )
    return texto.split()


def analyze_sequential_repetitions(text: str) -> list[dict]:
    palavras = normalize_text(text)
    repeticoes = []

    for i in range(len(palavras) - 1):
        if palavras[i] == palavras[i + 1]:
            repeticoes.append({
                "termo": palavras[i],
                "posicao": i
            })

    return repeticoes


def analyze_frequent_terms(text: str, min_occurrences: int = 2) -> dict:
    palavras = normalize_text(text)
    palavras_filtradas = [
        palavra for palavra in palavras
        if palavra not in STOPWORDS and len(palavra) > 2
    ]

    contagem = Counter(palavras_filtradas)

    return {
        termo: qtd
        for termo, qtd in contagem.items()
        if qtd >= min_occurrences
    }