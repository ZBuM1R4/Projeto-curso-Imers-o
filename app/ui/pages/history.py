from datetime import datetime, timezone

import streamlit as st

from app.database.supabase_db import (
    MONTHLY_ANALYSIS_LIMIT,
    delete_analysis_supabase,
    get_all_analyses_supabase,
    get_average_score_supabase,
    get_history_stats_supabase,
    get_remaining_monthly_analyses_supabase,
)
from app.services.network_checker import has_network_connection


def get_days_until_expiration(expires_at: str) -> int:
    if not expires_at:
        return 0

    try:
        expires_datetime = datetime.fromisoformat(
            expires_at.replace("Z", "+00:00")
        )

        now = datetime.now(timezone.utc)
        remaining_time = expires_datetime - now

        return max(remaining_time.days + 1, 0)

    except Exception:
        return 0


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
            background: #0f172a;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            font-weight: bold;
            color: #f8fafc;
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
        <span class="score-badge" style="background-color: {color};">
            {score}/100
        </span>
        """,
        unsafe_allow_html=True
    )


def render_analysis_title(title: str, ai_available: bool):
    if ai_available:
        st.write(f"📄 {title}")
    else:
        st.write(f"⚠️ 📄 {title}")
        st.caption("Análise feita sem IA. Resultados podem ser inconsistentes.")


def render_back_to_home_button():
    st.divider()

    if st.button("Voltar para início"):
        st.session_state["page"] = "home"
        st.rerun()


def render_history(user_id: str, access_token: str):
    if not has_network_connection():
        st.error("Erro, verifique sua conexão com a rede.")
        return

    st.title("Histórico de Análises")

    avg_score = get_average_score_supabase(user_id, access_token)
    stats = get_history_stats_supabase(user_id, access_token)

    try:
        remaining_analyses = get_remaining_monthly_analyses_supabase(
            user_id,
            access_token
        )
    except Exception:
        st.error("Erro, verifique sua conexão com a rede.")
        return

    st.subheader("Aproveitamento geral")
    render_score_circle(avg_score)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Análises disponíveis", stats["total_analyses"])

    with col2:
        st.metric(
            "Restantes no mês",
            f"{remaining_analyses}/{MONTHLY_ANALYSIS_LIMIT}"
        )

    with col3:
        st.metric("Melhor score", f"{stats['best_score']}/100")

    with col4:
        delta = stats["score_delta"]
        st.metric("Evolução", f"{delta:+} pontos")

    st.divider()

    analyses = get_all_analyses_supabase(user_id, access_token)

    if not analyses:
        st.info("Nenhuma análise encontrada.")
        render_back_to_home_button()
        return

    st.subheader("Análises realizadas")

    for analysis in analyses:
        analysis_id = analysis["id"]
        title = analysis["title"]
        score = analysis["score"]
        created_at = analysis["created_at"]
        ai_available = analysis["ai_available"]
        expires_at = analysis.get("expires_at")

        days_remaining = get_days_until_expiration(expires_at)

        col1, col2, col3, col4, col5 = st.columns([4, 1.5, 2, 1.5, 1.5])

        with col1:
            render_analysis_title(title, ai_available)
            st.caption(f"Criada em: {created_at}")

        with col2:
            render_score_badge(score)

        with col3:
            if days_remaining <= 1:
                st.caption("Descartada em até 1 dia")
            else:
                st.caption(f"Descartada em {days_remaining} dias")

        with col4:
            if st.button("Abrir", key=f"open_{analysis_id}"):
                st.session_state["selected_analysis"] = analysis_id
                st.session_state["page"] = "detail"
                st.rerun()

        with col5:
            if st.button("Descartar", key=f"delete_{analysis_id}"):
                try:
                    delete_analysis_supabase(analysis_id, user_id, access_token)
                except Exception:
                    st.error("Erro, verifique sua conexão com a rede.")
                    return

                if st.session_state.get("selected_analysis") == analysis_id:
                    del st.session_state["selected_analysis"]

                st.success("Análise descartada.")
                st.rerun()

        st.divider()

    render_back_to_home_button()