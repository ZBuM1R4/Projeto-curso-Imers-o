from io import BytesIO

import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches


def generate_bar_chart(title: str, labels: list[str], values: list[int]) -> BytesIO | None:
    if not labels or not values:
        return None

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_title(title)
    ax.set_ylabel("Ocorrências")

    buffer = BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    plt.close(fig)

    return buffer


def generate_pie_chart(title: str, labels: list[str], values: list[float]) -> BytesIO | None:
    if not labels or not values or sum(values) == 0:
        return None

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct="%1.1f%%")
    ax.set_title(title)

    buffer = BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    plt.close(fig)

    return buffer


def build_docx_report(report: dict, video_name: str = "Vídeo analisado") -> bytes:
    document = Document()

    document.add_heading("Relatório de Análise de Comunicação", level=0)
    document.add_paragraph(f"Arquivo analisado: {video_name}")
    
    score_data = report.get("score_comunicacao", {})
    document.add_heading("Score de comunicação", level=1)
    document.add_paragraph(f"Pontuação geral: {score_data.get('score', 0)}/100")
    document.add_paragraph(f"Classificação: {score_data.get('classificacao', 'N/A')}")
    document.add_paragraph(score_data.get("comentario", ""))

    document.add_heading("Pontos de atenção", level=1)
    for ponto in report.get("pontos_atencao", []):
        document.add_paragraph(ponto, style="List Bullet")

    document.add_heading("1. Transcrição", level=1)
    document.add_paragraph(report.get("transcricao", ""))

    document.add_heading("2. Vícios de linguagem", level=1)
    filler_words = report.get("vicios_de_linguagem", {})
    if filler_words:
        for termo, qtd in filler_words.items():
            document.add_paragraph(f"{termo}: {qtd} ocorrência(s)", style="List Bullet")

        filler_chart = generate_bar_chart(
            title="Frequência de vícios de linguagem",
            labels=list(filler_words.keys()),
            values=list(filler_words.values())
        )
        if filler_chart:
            document.add_picture(filler_chart, width=Inches(5.8))
    else:
        document.add_paragraph("Nenhum vício de linguagem encontrado.")

    document.add_heading("3. Pausas", level=1)
    pausas = report.get("pausas", {})
    document.add_paragraph(f"Duração total: {pausas.get('duracao_total', 0)}s")
    document.add_paragraph(f"Quantidade de pausas longas: {pausas.get('quantidade_pausas_longas', 0)}")
    document.add_paragraph(f"Tempo total de silêncio: {pausas.get('tempo_total_silencio', 0)}s")

    pausas_longas = pausas.get("pausas_longas", [])
    if pausas_longas:
        document.add_paragraph("Pausas longas detectadas:")
        for pausa in pausas_longas:
            document.add_paragraph(
                f"Início: {round(pausa['start'], 2)}s | "
                f"Fim: {round(pausa['end'], 2)}s | "
                f"Duração: {round(pausa['duration'], 2)}s",
                style="List Bullet"
            )
    else:
        document.add_paragraph("Nenhuma pausa longa detectada.")

    tempo_total = pausas.get("duracao_total", 0)
    tempo_silencio = pausas.get("tempo_total_silencio", 0)
    tempo_fala = max(tempo_total - tempo_silencio, 0)

    pie_chart = generate_pie_chart(
        title="Distribuição entre fala e silêncio",
        labels=["Fala", "Silêncio"],
        values=[tempo_fala, tempo_silencio]
    )
    if pie_chart:
        document.add_picture(pie_chart, width=Inches(5.2))

    document.add_heading("4. Repetições", level=1)
    repeticoes = report.get("repeticoes", {})

    sequenciais = repeticoes.get("sequenciais", [])
    if sequenciais:
        document.add_paragraph("Repetições em sequência:")
        for repeticao in sequenciais:
            document.add_paragraph(
                f"Termo repetido: {repeticao['termo']}",
                style="List Bullet"
            )
    else:
        document.add_paragraph("Nenhuma repetição em sequência.")

    recorrentes = repeticoes.get("termos_recorrentes", {})
    if recorrentes:
        document.add_paragraph("Termos mais recorrentes:")
        for termo, qtd in recorrentes.items():
            document.add_paragraph(f"{termo}: {qtd}", style="List Bullet")

        recorrentes_chart = generate_bar_chart(
            title="Termos mais recorrentes",
            labels=list(recorrentes.keys()),
            values=list(recorrentes.values())
        )
        if recorrentes_chart:
            document.add_picture(recorrentes_chart, width=Inches(5.8))
    else:
        document.add_paragraph("Nenhum termo recorrente relevante.")

    document.add_heading("5. Observações para revisão humana", level=1)
    document.add_paragraph(
        "Espaço reservado para comentários, correções e observações do revisor."
    )
    document.add_paragraph("\n\n\n")

    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()