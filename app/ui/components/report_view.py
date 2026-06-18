import streamlit as st

from app.services.docx_exporter import build_docx_report


def render_ai_warning():
    st.warning(
        "⚠️ Esta análise foi gerada sem a avaliação da IA. "
        "Os resultados podem apresentar inconsistências."
    )


def render_filtered_attention_points(report: dict):
    pontos_filtrados = []

    for ponto in report.get("pontos_atencao", []):
        ponto_lower = ponto.lower()

        if "uso frequente" in ponto_lower:
            continue

        if "vício" in ponto_lower or "vicio" in ponto_lower:
            continue

        if "vícios" in ponto_lower or "vicios" in ponto_lower:
            continue

        pontos_filtrados.append(ponto)

    if pontos_filtrados:
        for ponto in pontos_filtrados:
            st.write(f"⚠️ {ponto}")
    else:
        st.write("Nenhum ponto crítico identificado nesta análise.")


def render_pause_details(report: dict):
    pausas = report.get("pausas", {})

    st.write(f"⏱ Duração total: {pausas.get('duracao_total', 0)}s")
    st.write(f"🛑 Pausas longas: {pausas.get('quantidade_pausas_longas', 0)}")
    st.write(f"🔇 Tempo em silêncio: {pausas.get('tempo_total_silencio', 0)}s")

    pausas_longas = pausas.get("pausas_longas", [])

    if pausas_longas:
        st.write("Pausas detectadas:")

        for pausa in pausas_longas:
            st.write(
                f"- {round(pausa['start'], 2)}s → "
                f"{round(pausa['end'], 2)}s "
                f"({round(pausa['duration'], 2)}s)"
            )
    else:
        st.write("Nenhuma pausa longa detectada.")


def render_repetition_details(report: dict):
    repeticoes = report.get("repeticoes", {})

    sequenciais = repeticoes.get("sequenciais", [])
    termos_recorrentes = repeticoes.get("termos_recorrentes", {})

    if sequenciais:
        st.write("Repetições em sequência:")

        for repeticao in sequenciais:
            st.write(f"- {repeticao['termo']}")
    else:
        st.write("Nenhuma repetição em sequência.")

    if termos_recorrentes:
        st.write("Termos mais recorrentes:")

        for termo, qtd in termos_recorrentes.items():
            st.write(f"- {termo}: {qtd}")
    else:
        st.write("Nenhum termo recorrente relevante.")


def render_report_download(report: dict, video_name: str):
    docx_bytes = build_docx_report(report, video_name=video_name)

    st.download_button(
        label="Baixar relatório em DOCX",
        data=docx_bytes,
        file_name="relatorio_analise_comunicacao.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


def render_report_details(report: dict, video_name: str = "video_analisado"):
    score_data = report["score_comunicacao"]

    st.subheader("Score de comunicação")
    st.metric("Pontuação geral", f"{score_data['score']}/100")
    st.write(f"**Classificação:** {score_data['classificacao']}")
    st.write(score_data["comentario"])

    analise_ia = report.get("analise_global_ia", {})

    if not analise_ia.get("disponivel", False):
        render_ai_warning()

    st.subheader("Transcrição")
    st.write(report["transcricao"])

    st.subheader("Análise global por IA")
    st.write(analise_ia.get("analise", ""))

    st.subheader("Pontos de atenção")
    render_filtered_attention_points(report)

    st.subheader("Pausas")
    render_pause_details(report)

    st.subheader("Repetições")
    render_repetition_details(report)

    st.divider()

    render_report_download(report, video_name)