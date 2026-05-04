import matplotlib.pyplot as plt
import streamlit as st

from app.database.db import (
    DEFAULT_USER_ID,
    create_tables,
    delete_analysis,
    get_all_analyses,
    get_analysis_by_id,
    get_average_score,
    get_history_stats,
    get_score_history,
    save_analysis,
)
from app.services.attention_points_analyzer import generate_attention_points
from app.services.audio_extractor import extract_audio
from app.services.docx_exporter import build_docx_report
from app.services.filler_word_analyzer import analyze_filler_words
from app.services.gemini_full_context_analyzer import (
    analyze_full_transcription_with_gemini,
)
from app.services.pause_analyzer import analyze_pauses
from app.services.report_builder import build_report
from app.services.repetition_analyzer import (
    analyze_frequent_terms,
    analyze_sequential_repetitions,
)
from app.services.score_analyzer import calculate_communication_score
from app.services.transcriber import transcribe_audio
from app.services.transcription_marker import highlight_transcription
from app.utils.file_manager import save_uploaded_file


st.set_page_config(page_title="Análise de Comunicação", layout="centered")

create_tables()

CURRENT_USER_ID = DEFAULT_USER_ID


def get_score_color(score: float) -> str:
    if score == 0:
        return "#d9d9d9"
    if score <= 20:
        return "#ff4d4d"
    if score <= 40:
        return "#ff9900"
    if score <= 60:
        return "#ffd966"
    if score < 80:
        return "#93c47d"
    return "#00b050"


def render_score_circle(score: float):
    color = get_score_color(score)

    html = f"""
    <div style="
        width: 180px;
        height: 180px;
        border-radius: 50%;
        background: conic-gradient({color} {score}%, #e6e6e6 {score}%);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px auto;
    ">
        <div style="
            width: 130px;
            height: 130px;
            border-radius: 50%;
            background: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            font-weight: bold;
            color: #222222;
        ">
            {score:.1f}%
        </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


def render_score_badge(score: int):
    color = get_score_color(score)

    st.markdown(
        f"""
        <div style="
            background-color: {color};
            padding: 8px 12px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            color: white;
            min-width: 80px;
        ">
            {score}/100
        </div>
        """,
        unsafe_allow_html=True
    )


def render_score_evolution_chart():
    history = get_score_history(CURRENT_USER_ID)

    if len(history) < 2:
        st.info("Faça pelo menos duas análises para visualizar a evolução.")
        return

    labels = [str(index + 1) for index, _ in enumerate(history)]
    scores = [row[1] for row in history]

    fig, ax = plt.subplots()
    ax.plot(labels, scores, marker="o")
    ax.set_ylim(0, 100)
    ax.set_xlabel("Análises")
    ax.set_ylabel("Score")
    ax.set_title("Evolução do score ao longo do tempo")

    st.pyplot(fig)


def generate_report(video_path: str, audio_path: str):
    extracted_audio = extract_audio(video_path, audio_path)

    if not extracted_audio:
        return None

    texto = transcribe_audio(extracted_audio)
    filler_words = analyze_filler_words(texto)
    pause_data = analyze_pauses(extracted_audio)
    sequential_repetitions = analyze_sequential_repetitions(texto)
    frequent_terms = analyze_frequent_terms(texto)

    partial_report = {
        "transcricao": texto,
        "vicios_de_linguagem": filler_words,
        "pausas": pause_data,
        "repeticoes": {
            "sequenciais": sequential_repetitions,
            "termos_recorrentes": frequent_terms,
        },
    }

    ai_full_analysis = analyze_full_transcription_with_gemini(texto)
    ia_metricas = ai_full_analysis.get("metricas", {})

    score_data = calculate_communication_score(
        partial_report,
        ia_metricas=ia_metricas
    )

    attention_points = generate_attention_points(partial_report)

    report = build_report(
        transcription_text=texto,
        filler_words=filler_words,
        pause_data=pause_data,
        frequent_terms=frequent_terms,
        sequential_repetitions=sequential_repetitions,
        score_data=score_data,
        attention_points=attention_points,
    )

    report["analise_global_ia"] = ai_full_analysis

    save_analysis(report, video_path, CURRENT_USER_ID)

    return report


def render_report_details(report: dict, video_name: str = "video_analisado"):
    score_data = report["score_comunicacao"]

    st.subheader("Score de comunicação")
    st.metric("Pontuação geral", f"{score_data['score']}/100")
    st.write(f"**Classificação:** {score_data['classificacao']}")
    st.write(score_data["comentario"])

    analise_ia = report.get("analise_global_ia", {})

    if not analise_ia.get("disponivel", False):
        st.warning(
            "⚠️ Esta análise foi gerada sem a avaliação da IA. "
            "Os resultados podem apresentar inconsistências."
        )

    st.subheader("Transcrição")

    show_markers = st.toggle("Exibir marcações na transcrição", value=False)

    if show_markers:
        st.caption("Legenda:")
        st.caption("🔴 vício de linguagem")
        st.caption("🟡 termo recorrente")

        marked_text = highlight_transcription(
            report["transcricao"],
            report["repeticoes"]["termos_recorrentes"]
        )
        st.markdown(marked_text, unsafe_allow_html=True)
    else:
        st.write(report["transcricao"])

    st.subheader("Análise global por IA")

    if analise_ia.get("disponivel"):
        st.success(analise_ia.get("mensagem", ""))
        st.write(analise_ia.get("analise", ""))
    else:
        st.info(analise_ia.get("mensagem", ""))

    st.subheader("Pontos de atenção")
    for ponto in report["pontos_atencao"]:
        st.write(f"⚠️ {ponto}")

    st.subheader("Vícios de linguagem")
    vicios = report.get("vicios_de_linguagem", {})

    if vicios:
        for termo, qtd in vicios.items():
            st.write(f"🔹 {termo}: {qtd} ocorrência(s)")
    else:
        st.write("Nenhum vício de linguagem encontrado.")

    st.subheader("Pausas")
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

    st.subheader("Repetições")
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

    st.divider()

    docx_bytes = build_docx_report(
        report,
        video_name=video_name
    )

    st.download_button(
        label="Baixar relatório em DOCX",
        data=docx_bytes,
        file_name="relatorio_analise_comunicacao.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


def render_home():
    st.title("Análise de Comunicação por Vídeo")
    st.caption(f"Usuário local atual: {CURRENT_USER_ID}")

    if st.button("Ver histórico de análises"):
        st.session_state["page"] = "history"
        st.rerun()

    uploaded_file = st.file_uploader(
        "Envie um vídeo",
        type=["mp4", "mov", "avi", "mkv"]
    )

    if uploaded_file:
        video_path = f"data/input/{uploaded_file.name}"
        audio_path = "data/temp/audio.wav"

        save_uploaded_file(uploaded_file, video_path)

        st.session_state["video_path"] = video_path
        st.session_state["audio_path"] = audio_path

    if "video_path" in st.session_state:
        st.video(st.session_state["video_path"])

        if st.button("Analisar vídeo"):
            with st.spinner("Processando vídeo..."):
                report = generate_report(
                    st.session_state["video_path"],
                    st.session_state["audio_path"]
                )

                if not report:
                    st.error("Falha ao gerar análise.")
                    return

                st.session_state["report"] = report
                st.success("Análise concluída e salva no histórico.")

    if "report" in st.session_state:
        render_report_details(
            st.session_state["report"],
            video_name=st.session_state.get("video_path", "video_analisado")
        )


def render_history():
    st.title("Histórico de Análises")
    st.caption(f"Usuário local atual: {CURRENT_USER_ID}")

    avg_score = get_average_score(CURRENT_USER_ID)
    stats = get_history_stats(CURRENT_USER_ID)

    st.subheader("Aproveitamento geral")
    render_score_circle(avg_score)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Análises feitas", stats["total_analyses"])

    with col2:
        st.metric("Melhor score", f"{stats['best_score']}/100")

    with col3:
        delta = stats["score_delta"]
        st.metric("Evolução", f"{delta:+} pontos")

    st.subheader("Evolução")
    render_score_evolution_chart()

    st.divider()

    analyses = get_all_analyses(CURRENT_USER_ID)

    if not analyses:
        st.info("Nenhuma análise encontrada.")
        if st.button("Voltar"):
            st.session_state["page"] = "home"
            st.rerun()
        return

    st.subheader("Análises realizadas")

    for analysis in analyses:
        analysis_id, title, score, created_at, ai_available = analysis

        col1, col2, col3, col4 = st.columns([5, 2, 2, 2])

        with col1:
            if ai_available:
                st.write(f"📄 {title}")
            else:
                st.write(f"⚠️ 📄 {title}")
                st.caption("Análise feita sem IA. Resultados podem ser inconsistentes.")

            st.caption(f"{created_at}")

        with col2:
            render_score_badge(score)

        with col3:
            if st.button("Abrir", key=f"open_{analysis_id}"):
                st.session_state["selected_analysis"] = analysis_id
                st.session_state["page"] = "detail"
                st.rerun()

        with col4:
            if st.button("Descartar", key=f"delete_{analysis_id}"):
                delete_analysis(analysis_id, CURRENT_USER_ID)

                if st.session_state.get("selected_analysis") == analysis_id:
                    del st.session_state["selected_analysis"]

                st.success("Análise descartada.")
                st.rerun()

        st.divider()

    if st.button("Voltar"):
        st.session_state["page"] = "home"
        st.rerun()


def render_detail():
    selected_analysis = st.session_state.get("selected_analysis")

    if not selected_analysis:
        st.warning("Nenhuma análise selecionada.")
        if st.button("Voltar"):
            st.session_state["page"] = "history"
            st.rerun()
        return

    report = get_analysis_by_id(selected_analysis, CURRENT_USER_ID)

    if not report:
        st.error("Essa análise não existe mais ou foi descartada.")
        if st.button("Voltar"):
            st.session_state["page"] = "history"
            st.rerun()
        return

    if st.button("Voltar"):
        st.session_state["page"] = "history"
        st.rerun()

    render_report_details(report, video_name="analise_historico")


if "page" not in st.session_state:
    st.session_state["page"] = "home"

if st.session_state["page"] == "home":
    render_home()
elif st.session_state["page"] == "history":
    render_history()
elif st.session_state["page"] == "detail":
    render_detail()