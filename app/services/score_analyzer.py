def calculate_communication_score(report: dict) -> dict:
    score = 100

    filler_words = report.get("vicios_de_linguagem", {})
    pausas = report.get("pausas", {})
    repeticoes = report.get("repeticoes", {})

    total_filler_words = sum(filler_words.values())
    total_pausas_longas = pausas.get("quantidade_pausas_longas", 0)
    total_termos_recorrentes = len(repeticoes.get("termos_recorrentes", {}))

    score -= total_filler_words * 2
    score -= total_pausas_longas * 5
    score -= total_termos_recorrentes * 3

    score = max(score, 0)

    if score >= 85:
        classificacao = "Excelente"
        comentario = "Comunicação muito boa, com poucos desvios relevantes."
    elif score >= 70:
        classificacao = "Boa"
        comentario = "Comunicação boa, com alguns pontos de melhoria."
    elif score >= 50:
        classificacao = "Regular"
        comentario = "Comunicação razoável, mas com sinais importantes de ajuste."
    else:
        classificacao = "Precisa melhorar"
        comentario = "Comunicação com muitos pontos que merecem revisão."

    return {
        "score": score,
        "classificacao": classificacao,
        "comentario": comentario,
        "detalhes": {
            "total_vicios": total_filler_words,
            "total_pausas_longas": total_pausas_longas,
            "total_termos_recorrentes": total_termos_recorrentes,
        }
    }