import streamlit as st

from app.services.audio_extractor import extract_audio
from app.services.transcriber import transcribe_audio
from app.services.filler_word_analyzer import analyze_filler_words
from app.services.pause_analyzer import analyze_pauses
from app.services.repetition_analyzer import (
    analyze_sequential_repetitions,
    analyze_frequent_terms,
)
from app.services.report_builder import build_report
from app.utils.file_manager import save_uploaded_file


st.set_page_config(page_title="Análise de Comunicação", layout="centered")

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

    st.info("Vídeo enviado com sucesso.")

    st.subheader("Pré-visualização do vídeo")
    st.video(video_path)

    if st.button("Analisar vídeo"):
        with st.spinner("Processando vídeo..."):
            extracted_audio = extract_audio(video_path, audio_path)

            if not extracted_audio:
                st.error("Falha na extração do áudio.")
            else:
                texto = transcribe_audio(extracted_audio)
                filler_words = analyze_filler_words(texto)
                pause_data = analyze_pauses(extracted_audio)
                sequential_repetitions = analyze_sequential_repetitions(texto)
                frequent_terms = analyze_frequent_terms(texto)

                report = build_report(
                    transcription_text=texto,
                    filler_words=filler_words,
                    pause_data=pause_data,
                    frequent_terms=frequent_terms,
                    sequential_repetitions=sequential_repetitions,
                )

                st.success("Análise concluída.")

                st.subheader("Transcrição")
                st.write(report["transcricao"])

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
                    st.write("Pausas detectadas:")
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
                    st.write("Repetições em sequência:")
                    for r in repeticoes["sequenciais"]:
                        st.write(f"- {r['termo']}")
                else:
                    st.write("Nenhuma repetição em sequência.")

                if repeticoes["termos_recorrentes"]:
                    st.write("Termos mais recorrentes:")
                    for termo, qtd in repeticoes["termos_recorrentes"].items():
                        st.write(f"- {termo}: {qtd}")
                else:
                    st.write("Nenhum termo recorrente relevante.")