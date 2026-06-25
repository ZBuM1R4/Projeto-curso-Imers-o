import streamlit as st

from app.database.supabase_db import save_analysis_supabase
from app.services.attention_points_analyzer import generate_attention_points
from app.services.audio_extractor import extract_audio
from app.services.gemini_full_context_analyzer import (
    analyze_full_transcription_with_gemini,
)
from app.services.network_checker import has_network_connection
from app.services.pause_analyzer import analyze_pauses
from app.services.report_builder import build_report
from app.services.repetition_analyzer import (
    analyze_frequent_terms,
    analyze_sequential_repetitions,
)
from app.services.score_analyzer import calculate_communication_score
from app.services.transcriber import transcribe_audio


def generate_report(
    video_path: str,
    audio_path: str,
    user_id: str,
    access_token: str
):
    if not has_network_connection():
        st.error("Erro, verifique sua conexão com a rede.")
        return None

    extracted_audio = extract_audio(video_path, audio_path)

    if not extracted_audio:
        return None

    texto = transcribe_audio(extracted_audio)
    pause_data = analyze_pauses(extracted_audio)
    sequential_repetitions = analyze_sequential_repetitions(texto)
    frequent_terms = analyze_frequent_terms(texto)

    partial_report = {
        "transcricao": texto,
        "pausas": pause_data,
        "repeticoes": {
            "sequenciais": sequential_repetitions,
            "termos_recorrentes": frequent_terms,
        },
    }

    ai_full_analysis = analyze_full_transcription_with_gemini(texto)

    if not ai_full_analysis.get("disponivel", False):
        if has_network_connection():
            st.error("Erro ao conectar com a IA. Tente novamente em instantes.")
        else:
            st.error("Erro, verifique sua conexão com a rede.")
        return None

    score_data = calculate_communication_score(
        partial_report,
        ia_metricas=ai_full_analysis.get("metricas", {})
    )

    attention_points = generate_attention_points(partial_report)

    report = build_report(
        transcription_text=texto,
        pause_data=pause_data,
        frequent_terms=frequent_terms,
        sequential_repetitions=sequential_repetitions,
        score_data=score_data,
        attention_points=attention_points,
    )

    report["analise_global_ia"] = ai_full_analysis

    try:
        save_analysis_supabase(report, video_path, user_id, access_token)
    except Exception:
        st.error("Erro, verifique sua conexão com a rede.")
        return None

    return report