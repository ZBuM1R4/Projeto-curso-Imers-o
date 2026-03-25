import re


FILLER_WORDS = [
    "né",
    "tipo",
    "então",
    "assim",
    "tá",
    "ah",
    "hum",
]


def _apply_highlight(text: str, terms: list[str], color: str) -> str:
    highlighted_text = text

    for term in sorted(set(terms), key=len, reverse=True):
        pattern = rf"\b({re.escape(term)})\b"
        replacement = (
            f'<span style="background-color: {color}; '
            f'padding: 2px 4px; border-radius: 4px;">\\1</span>'
        )

        highlighted_text = re.sub(
            pattern,
            replacement,
            highlighted_text,
            flags=re.IGNORECASE
        )

    return highlighted_text


def highlight_transcription(text: str, recurring_terms: dict | None = None) -> str:
    highlighted_text = text

    # Primeiro destaca termos recorrentes
    if recurring_terms:
        recurring_list = list(recurring_terms.keys())
        highlighted_text = _apply_highlight(
            highlighted_text,
            recurring_list,
            "#ffe599"  # amarelo
        )

    # Depois destaca vícios de linguagem
    highlighted_text = _apply_highlight(
        highlighted_text,
        FILLER_WORDS,
        "#ffcccc"  # vermelho claro
    )

    return highlighted_text