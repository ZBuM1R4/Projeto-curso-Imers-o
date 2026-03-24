def build_report(
    transcription_text: str,
    filler_words: dict,
    pause_data: dict,
    frequent_terms: dict,
    sequential_repetitions: list,
) -> dict:
    return {
        "transcricao": transcription_text,
        "vicios_de_linguagem": filler_words,
        "pausas": {
            "duracao_total": pause_data.get("duracao_total", 0),
            "quantidade_pausas_longas": pause_data.get("quantidade_pausas_longas", 0),
            "tempo_total_silencio": pause_data.get("tempo_total_silencio", 0),
            "pausas_longas": pause_data.get("pausas_longas", []),
        },
        "repeticoes": {
            "sequenciais": sequential_repetitions,
            "termos_recorrentes": frequent_terms,
        },
    }