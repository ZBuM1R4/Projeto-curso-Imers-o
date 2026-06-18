import streamlit as st

from app.database.supabase_db import (
    MONTHLY_ANALYSIS_LIMIT,
    can_create_analysis_supabase,
    get_remaining_monthly_analyses_supabase,
)
from app.services.analysis_pipeline import generate_report
from app.services.network_checker import has_network_connection
from app.services.temp_file_cleaner import clean_temp_files
from app.ui.components.navigation import render_back_to_home_button
from app.ui.components.report_view import render_report_details
from app.ui.session_state import clear_analysis_session
from app.utils.file_manager import save_uploaded_file


def render_analysis(user_id: str, access_token: str):
    if "report" in st.session_state:
        st.title("Resultado da análise")

        video_path = st.session_state.get("video_path")

        if video_path:
            st.markdown('<div class="result-video-card">', unsafe_allow_html=True)

            with st.container(border=True):
                st.subheader("Vídeo analisado")
                st.caption("Arquivo utilizado para gerar esta análise.")
                st.video(video_path)

            st.markdown("</div>", unsafe_allow_html=True)

        st.divider()

        render_report_details(
            st.session_state["report"],
            video_name=st.session_state.get("video_path", "video_analisado")
        )

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Voltar ao início", use_container_width=True):
                st.session_state["page"] = "home"
                st.rerun()

        with col2:
            if st.button("Acompanhe sua evolução", use_container_width=True):
                st.session_state["page"] = "history"
                st.rerun()

        with col3:
            if st.button("Iniciar nova análise", use_container_width=True):
                clean_temp_files()
                clear_analysis_session()
                st.session_state["page"] = "analysis"
                st.rerun()

        return

    st.title("Análise")

    st.write(
        "Envie um vídeo para iniciar a análise da sua comunicação. "
        "Após o envio, confira a pré-visualização antes de processar."
    )

    if not has_network_connection():
        st.error("Erro, verifique sua conexão com a rede.")
        render_back_to_home_button()
        return

    try:
        remaining_analyses = get_remaining_monthly_analyses_supabase(
            user_id,
            access_token
        )
    except Exception:
        st.error("Erro, verifique sua conexão com a rede.")
        render_back_to_home_button()
        return

    st.info(
        f"Você possui {remaining_analyses} de "
        f"{MONTHLY_ANALYSIS_LIMIT} análises disponíveis neste mês."
    )

    if remaining_analyses <= 0:
        st.warning(
            f"Você atingiu o limite mensal de {MONTHLY_ANALYSIS_LIMIT} análises. "
            "Tente novamente no próximo mês ou entre em contato com a equipe."
        )
        render_back_to_home_button()
        return

    with st.container(border=True):
        st.markdown("### Enviar vídeo")

        uploaded_file = st.file_uploader(
            "Envie um vídeo",
            type=["mp4", "mov", "avi", "mkv"]
        )

        st.caption("Formatos aceitos: MP4, MOV, AVI, MKV • Até 2GB")

        if uploaded_file:
            current_file_name = st.session_state.get("uploaded_file_name")

            if current_file_name != uploaded_file.name:
                st.session_state["uploaded_file_name"] = uploaded_file.name
                st.session_state.pop("report", None)

                video_path = f"data/input/{uploaded_file.name}"
                audio_path = "data/temp/audio.wav"

                save_uploaded_file(uploaded_file, video_path)

                st.session_state["video_path"] = video_path
                st.session_state["audio_path"] = audio_path

            st.divider()

            st.markdown("### Pré-visualização do vídeo")
            st.caption("Confira se o arquivo enviado está correto antes de analisar.")

            preview_col, _ = st.columns([0.72, 0.28])

            with preview_col:
                st.video(st.session_state["video_path"])

            if st.button("Analisar vídeo"):
                try:
                    can_create_analysis = can_create_analysis_supabase(
                        user_id,
                        access_token
                    )
                except Exception:
                    st.error("Erro, verifique sua conexão com a rede.")
                    return

                if not can_create_analysis:
                    st.warning(
                        f"Você atingiu o limite mensal de {MONTHLY_ANALYSIS_LIMIT} análises. "
                        "Tente novamente no próximo mês ou entre em contato com a equipe."
                    )
                    return

                with st.spinner("Processando vídeo..."):
                    report = generate_report(
                        st.session_state["video_path"],
                        st.session_state["audio_path"],
                        user_id,
                        access_token
                    )

                    if not report:
                        return

                    st.session_state["report"] = report
                    st.success("Análise concluída e salva no histórico.")
                    st.rerun()

    render_back_to_home_button()