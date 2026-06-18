def calculate_communication_score(report: dict, ia_metricas: dict = None) -> dict:
    score = 100

    pausas = report.get("pausas", {})
    repeticoes = report.get("repeticoes", {})

    total_pausas_longas = pausas.get("quantidade_pausas_longas", 0)
    total_termos_recorrentes = len(repeticoes.get("termos_recorrentes", {}))

    score -= total_pausas_longas * 5
    score -= total_termos_recorrentes * 3

    if ia_metricas:
        controle_linguagem = ia_metricas.get("controle_linguagem", 1)
        clareza = ia_metricas.get("clareza", 1)
        formalidade = ia_metricas.get("formalidade", 1)
        fluidez = ia_metricas.get("fluidez", 1)
        qualidade_comunicacao = ia_metricas.get("qualidade_comunicacao", 1)

        penalidade_ia = (
            (1 - controle_linguagem) * 30 +
            (1 - clareza) * 30 +
            (1 - formalidade) * 25 +
            (1 - fluidez) * 25 +
            (1 - qualidade_comunicacao) * 40
        )

        score -= penalidade_ia

        metricas_baixas = [
            controle_linguagem,
            clareza,
            formalidade,
            fluidez,
            qualidade_comunicacao,
        ]

        quantidade_metricas_criticas = sum(
            1 for metrica in metricas_baixas if metrica <= 0.40
        )

        if qualidade_comunicacao <= 0.25:
            score = min(score, 20)

        elif qualidade_comunicacao <= 0.40:
            score = min(score, 30)

        if controle_linguagem <= 0.35 and formalidade <= 0.40:
            score = min(score, 25)

        if controle_linguagem <= 0.35 and qualidade_comunicacao <= 0.40:
            score = min(score, 25)

        if clareza <= 0.40 or fluidez <= 0.40:
            score = min(score, 35)

        if quantidade_metricas_criticas >= 3:
            score = min(score, 25)

        if quantidade_metricas_criticas >= 4:
            score = min(score, 20)

    score = max(score, 0)
    score = round(score)

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
            "total_pausas_longas": total_pausas_longas,
            "total_termos_recorrentes": total_termos_recorrentes,
            "ia_metricas": ia_metricas or {}
        }
    }