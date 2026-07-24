import streamlit as st

from app.database.admin_db import is_admin_user
from app.database.profile_db import get_profile
from app.services.temp_file_cleaner import clean_temp_files
from app.ui.session_state import clear_analysis_session


def user_is_admin(user_id: str, access_token: str) -> bool:
    try:
        return is_admin_user(user_id, access_token)
    except Exception:
        return False


def render_sidebar(user_id: str, access_token: str, render_avatar):
    profile = get_profile(user_id, access_token)
    user = st.session_state.get("user")
    user_email = getattr(user, "email", "") if user else ""
    is_admin = user_is_admin(user_id, access_token)

    with st.sidebar:
        st.markdown(
            """
            <div class="brand-wrap">
                <div class="brand-icon">AI</div>
                <div>
                    <div class="brand-title">Análise de<br>Comunicação</div>
                    <div class="brand-subtitle">Oratória com IA</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if profile:
            render_avatar(profile.get("avatar_url", ""), width=76)

            st.markdown(
                f"""
                <div style="margin-bottom: 1.6rem;">
                    <div class="sidebar-profile-name">
                        {profile.get('first_name', '')} {profile.get('last_name', '')}
                    </div>
                    <div class="sidebar-profile-email">{user_email}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        if st.button("Início"):
            st.session_state["page"] = "home"
            st.rerun()

        if st.button("Análise"):
            clean_temp_files()
            clear_analysis_session()
            st.session_state["page"] = "analysis"
            st.rerun()

        if st.button("Histórico"):
            st.session_state["page"] = "history"
            st.rerun()

        if st.button("Perfil"):
            st.session_state["page"] = "profile"
            st.rerun()

        if is_admin:
            if st.button("Admin"):
                st.session_state["page"] = "admin"
                st.rerun()

        st.markdown(
            '<div class="sidebar-section-divider"></div>',
            unsafe_allow_html=True
        )

        if st.button("Sair da conta"):
            clean_temp_files()
            st.session_state.clear()
            st.rerun()