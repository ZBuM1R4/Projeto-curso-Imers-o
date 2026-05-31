def generate_attention_points(report: dict) -> list[str]:
    attention_points = []

    pausas = report.get("pausas", {})
    repeticoes = report.get("repeticoes", {})

    pausas_longas = pausas.get("pausas_longas", [])

    for pausa in pausas_longas:
        attention_points.append(
            f"Pausa longa detectada entre {round(pausa['start'], 2)}s e "
            f"{round(pausa['end'], 2)}s ({round(pausa['duration'], 2)}s)."
        )

    termos_recorrentes = repeticoes.get("termos_recorrentes", {})

    for termo, qtd in termos_recorrentes.items():
        if qtd >= 3:
            attention_points.append(
                f'Termo "{termo}" repetido com frequência ({qtd} vezes).'
            )

    if not attention_points:
        attention_points.append("Nenhum ponto crítico de atenção identificado.")

    return attention_points