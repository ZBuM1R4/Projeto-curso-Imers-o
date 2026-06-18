import streamlit as st

from app.database.supabase_db import get_analysis_by_id_supabase
from app.services.network_checker import has_network_connection
from app.ui.components.navigation import render_back_to_home_button
from app.ui.components.report_view import render_report_details


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
        st.error("Análise não encontrada.")
        render_back_to_home_button()
        return

    if st.button("Voltar ao histórico"):
        st.session_state["page"] = "history"
        st.rerun()

    render_report_details(report, video_name="analise_historico")
    render_back_to_home_button()