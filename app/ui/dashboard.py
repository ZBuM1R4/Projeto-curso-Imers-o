import matplotlib.pyplot as plt
import streamlit as st

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

    score_data = calculate_communication_score(partial_report)
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

    ai_full_analysis = analyze_full_transcription_with_gemini(texto)
    report["analise_global_ia"] = ai_full_analysis

    return report


def render_home():
    st.title("Análise de Comunicação por Vídeo")
    st.write("Faça upload de um vídeo para gerar a análise inicial.")

    uploaded_file = st.file_uploader(
        "Envie um vídeo",
        type=["mp4", "mov", "avi", "mkv"]
    )

    if uploaded_file is not None:
        video_path = f"data/input/{uploaded_file.name}"
        audio_path = "data/temp/audio.wav"

        save_uploaded_file(uploaded_file, video_path)

        st.session_state["video_path"] = video_path
        st.session_state["audio_path"] = audio_path

        st.info("Vídeo enviado com sucesso.")

    if "video_path" in st.session_state:
        st.subheader("Pré-visualização do vídeo")
        st.video(st.session_state["video_path"])

    if "video_path" in st.session_state and "audio_path" in st.session_state:
        if st.button("Analisar vídeo"):
            with st.spinner("Processando vídeo..."):
                report = generate_report(
                    st.session_state["video_path"],
                    st.session_state["audio_path"]
                )

                if not report:
                    st.error("Falha na extração do áudio.")
                    return

                st.session_state["report"] = report
                st.success("Análise concluída.")

    if "report" in st.session_state:
        report = st.session_state["report"]
        score_data = report["score_comunicacao"]

        st.subheader("Score de comunicação")
        st.metric("Pontuação geral", f"{score_data['score']}/100")
        st.write(f"**Classificação:** {score_data['classificacao']}")
        st.write(score_data["comentario"])

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
        analise_ia = report.get("analise_global_ia", {})

        if analise_ia.get("disponivel"):
            st.success(analise_ia.get("mensagem", ""))
            st.write(analise_ia.get("analise", ""))
        else:
            st.info(analise_ia.get("mensagem", ""))

        st.subheader("Pontos de atenção")
        for ponto in report["pontos_atencao"]:
            st.write(f"⚠️ {ponto}")

        st.subheader("Vícios de linguagem")
        if report["vicios_de_linguagem"]:
            for termo, qtd in report["vicios_de_linguagem"].items():
                st.write(f"🔹 {termo}: {qtd} ocorrência(s)")
        else:
            st.write("Nenhum vício de linguagem encontrado.")

        st.subheader("Pausas")
        pausas = report["pausas"]

        st.write(f"⏱ Duração total: {pausas['duracao_total']}s")
        st.write(f"🛑 Pausas longas: {pausas['quantidade_pausas_longas']}")
        st.write(f"🔇 Tempo em silêncio: {pausas['tempo_total_silencio']}s")

        if pausas["pausas_longas"]:
            for p in pausas["pausas_longas"]:
                st.write(
                    f"- {round(p['start'], 2)}s → "
                    f"{round(p['end'], 2)}s "
                    f"({round(p['duration'], 2)}s)"
                )
        else:
            st.write("Nenhuma pausa longa detectada.")

        st.subheader("Repetições")
        repeticoes = report["repeticoes"]

        if repeticoes["sequenciais"]:
            for r in repeticoes["sequenciais"]:
                st.write(f"- {r['termo']}")
        else:
            st.write("Nenhuma repetição em sequência.")

        if repeticoes["termos_recorrentes"]:
            for termo, qtd in repeticoes["termos_recorrentes"].items():
                st.write(f"- {termo}: {qtd}")
        else:
            st.write("Nenhum termo recorrente relevante.")

        st.divider()

        if st.button("Ver painel BI"):
            st.session_state["page"] = "bi"
            st.rerun()

        docx_bytes = build_docx_report(
            report,
            video_name=st.session_state.get("video_path", "video_analisado")
        )

        st.download_button(
            label="Baixar relatório em DOCX",
            data=docx_bytes,
            file_name="relatorio_analise_comunicacao.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )


def render_bi():
    st.title("Painel BI")

    if "report" not in st.session_state:
        st.warning("Nenhuma análise encontrada.")
        if st.button("Voltar"):
            st.session_state["page"] = "home"
            st.rerun()
        return

    report = st.session_state["report"]
    score_data = report["score_comunicacao"]

    if st.button("Voltar para tela inicial"):
        st.session_state["page"] = "home"
        st.rerun()

    st.subheader("Score")
    st.metric("Pontuação", f"{score_data['score']}/100")

    pausas = report["pausas"]
    repeticoes = report["repeticoes"]

    st.subheader("Análise global por IA")
    analise_ia = report.get("analise_global_ia", {})

    if analise_ia.get("disponivel"):
        st.success(analise_ia.get("mensagem", ""))
        st.write(analise_ia.get("analise", ""))
    else:
        st.info(analise_ia.get("mensagem", ""))

    col1, col2, col3 = st.columns(3)
    col1.metric("Pausas", pausas["quantidade_pausas_longas"])
    col2.metric("Silêncio", f"{pausas['tempo_total_silencio']}s")
    col3.metric("Repetições", len(repeticoes["termos_recorrentes"]))

    st.subheader("Gráficos")

    if report["vicios_de_linguagem"]:
        fig, ax = plt.subplots()
        ax.bar(
            list(report["vicios_de_linguagem"].keys()),
            list(report["vicios_de_linguagem"].values())
        )
        st.pyplot(fig)

    fig, ax = plt.subplots()
    ax.pie(
        [
            pausas["duracao_total"] - pausas["tempo_total_silencio"],
            pausas["tempo_total_silencio"],
        ],
        labels=["Fala", "Silêncio"],
        autopct="%1.1f%%"
    )
    st.pyplot(fig)


if "page" not in st.session_state:
    st.session_state["page"] = "home"

if st.session_state["page"] == "home":
    render_home()
else:
    render_bi()