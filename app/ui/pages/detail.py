import streamlit as st

from app.database.supabase_db import get_analysis_by_id_supabase
from app.services.network_checker import has_network_connection
from app.ui.components.navigation import render_back_to_home_button
from app.ui.components.report_view import render_report_details


def get_input_type_label(input_type: str) -> str:
    if input_type == "audio":
        return "Áudio"

    return "Vídeo"


def get_input_type_icon(input_type: str) -> str:
    if input_type == "audio":
        return "🎙️"

    return "🎥"


def render_analysis_type_summary(report: dict):
    input_type = report.get("input_type", "video")
    icon = get_input_type_icon(input_type)
    label = get_input_type_label(input_type)

    st.caption(f"{icon} Tipo da análise: {label}")


def render_detail(user_id: str, access_token: str):
    if not has_network_connection():
        st.error("Erro, verifique sua conexão com a rede.")
        return

    selected_analysis = st.session_state.get("selected_analysis")

    if not selected_analysis:
        st.warning("Nenhuma análise selecionada.")
        render_back_to_home_button()
        return

    try:
        report = get_analysis_by_id_supabase(
            selected_analysis,
            user_id,
            access_token
        )
    except Exception:
        st.error("Erro, verifique sua conexão com a rede.")
        return

    if not report:
        st.error("Análise não encontrada ou não disponível.")
        render_back_to_home_button()
        return

    if st.button("Voltar ao histórico"):
        st.session_state["page"] = "history"
        st.rerun()

    render_analysis_type_summary(report)

    render_report_details(report, video_name="analise_historico")
    render_back_to_home_button()