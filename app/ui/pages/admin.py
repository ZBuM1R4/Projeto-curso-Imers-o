import streamlit as st

from app.database.admin_db import (
    get_admin_analyses,
    get_admin_profiles,
    is_admin_user,
)
from app.services.network_checker import has_network_connection
from app.ui.components.navigation import render_back_to_home_button
from app.ui.components.score import render_score_badge


def get_input_type_label(input_type: str) -> str:
    if input_type == "audio":
        return "Áudio"

    return "Vídeo"


def render_admin_metrics(profiles: list, analyses: list):
    total_users = len(profiles)
    total_analyses = len(analyses)

    total_audio = sum(
        1 for analysis in analyses
        if analysis.get("input_type") == "audio"
    )

    total_video = sum(
        1 for analysis in analyses
        if analysis.get("input_type") == "video"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Usuários", total_users)

    with col2:
        st.metric("Análises", total_analyses)

    with col3:
        st.metric("Áudio", total_audio)

    with col4:
        st.metric("Vídeo", total_video)


def render_admin_profiles(profiles: list):
    st.subheader("Usuários cadastrados")

    if not profiles:
        st.info("Nenhum usuário encontrado.")
        return

    for profile in profiles:
        full_name = (
            f"{profile.get('first_name', '')} "
            f"{profile.get('last_name', '')}"
        ).strip()

        if not full_name:
            full_name = "Usuário sem nome"

        city = profile.get("city") or "Cidade não informada"
        state = profile.get("state") or ""

        with st.container(border=True):
            st.write(f"👤 **{full_name}**")
            st.caption(f"Localização: {city} {state}")
            st.caption(f"Cadastrado em: {profile.get('created_at')}")


def render_admin_analyses(analyses: list):
    st.subheader("Últimas análises")

    if not analyses:
        st.info("Nenhuma análise encontrada.")
        return

    for analysis in analyses:
        title = analysis.get("title") or "Análise sem título"
        input_type = get_input_type_label(analysis.get("input_type", "video"))
        score = analysis.get("score", 0)
        status = analysis.get("status", "active")
        created_at = analysis.get("created_at")
        ai_available = analysis.get("ai_available", False)

        with st.container(border=True):
            col1, col2, col3 = st.columns([4, 1.5, 2])

            with col1:
                st.write(f"📄 **{title}**")
                st.caption(f"Tipo: {input_type}")
                st.caption(f"Status: {status}")
                st.caption(f"Criada em: {created_at}")

                if not ai_available:
                    st.caption(
                        "⚠️ Análise gerada sem IA ou com IA indisponível."
                    )

            with col2:
                render_score_badge(score)

            with col3:
                st.caption(f"Usuário: {analysis.get('user_id')}")


def render_admin(user_id: str, access_token: str):
    if not has_network_connection():
        st.error("Erro, verifique sua conexão com a rede.")
        return

    if not is_admin_user(user_id, access_token):
        st.error("Acesso restrito a administradores.")
        render_back_to_home_button()
        return

    st.title("Painel Administrativo")

    st.caption(
        "Área somente leitura para acompanhamento de usuários e análises do sistema."
    )

    try:
        profiles = get_admin_profiles(user_id, access_token)
        analyses = get_admin_analyses(user_id, access_token)
    except Exception:
        st.error("Erro, verifique sua conexão com a rede.")
        return

    render_admin_metrics(profiles, analyses)

    st.divider()

    render_admin_profiles(profiles)

    st.divider()

    render_admin_analyses(analyses)

    render_back_to_home_button()