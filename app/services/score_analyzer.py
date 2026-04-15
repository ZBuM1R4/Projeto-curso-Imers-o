def calculate_communication_score(report: dict, ia_metricas: dict = None) -> dict:
    score = 100

    filler_words = report.get("vicios_de_linguagem", {})
    pausas = report.get("pausas", {})
    repeticoes = report.get("repeticoes", {})

    total_filler_words = sum(filler_words.values())
    total_pausas_longas = pausas.get("quantidade_pausas_longas", 0)
    total_termos_recorrentes = len(repeticoes.get("termos_recorrentes", {}))

    # Penalidades base (regras locais)
    score -= total_filler_words * 2
    score -= total_pausas_longas * 5
    score -= total_termos_recorrentes * 3

    # Penalidade baseada na IA
    if ia_metricas:
        controle_linguagem = ia_metricas.get("controle_linguagem", 1)
        clareza = ia_metricas.get("clareza", 1)
        formalidade = ia_metricas.get("formalidade", 1)
        fluidez = ia_metricas.get("fluidez", 1)
        qualidade_comunicacao = ia_metricas.get("qualidade_comunicacao", 1)

        penalidade_ia = (
            (1 - controle_linguagem) * 20 +
            (1 - clareza) * 25 +
            (1 - formalidade) * 15 +
            (1 - fluidez) * 20 +
            (1 - qualidade_comunicacao) * 30
        )

        score -= penalidade_ia

    score = max(score, 0)
    score = round(score)

    # Classificação final
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
            "ia_metricas": ia_metricas or {}
        }
    }