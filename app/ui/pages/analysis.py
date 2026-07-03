import streamlit as st

from app.database.supabase_db import (
    MONTHLY_ANALYSIS_LIMIT,
    can_create_analysis_supabase,
    get_remaining_monthly_analyses_supabase,
)
from app.services.analysis_pipeline import generate_report, generate_report_from_audio
from app.services.network_checker import has_network_connection
from app.services.temp_file_cleaner import clean_temp_files
from app.services.audio_file_manager import save_recorded_audio
from app.ui.components.navigation import render_back_to_home_button
from app.ui.components.report_view import render_report_details
from app.ui.session_state import clear_analysis_session
from app.utils.file_manager import save_uploaded_file
from app.utils.app_mode import get_app_mode_label, is_web_mode


def render_analysis_result():
    st.title("Resultado da análise")

    video_path = st.session_state.get("video_path")

    if video_path:
        render_result_video(video_path)

    st.divider()

    render_report_details(
        st.session_state["report"],
        video_name=st.session_state.get("video_path", "video_analisado")
    )

    st.divider()

    render_result_actions()


def render_result_video(video_path: str):
    st.markdown('<div class="result-video-card">', unsafe_allow_html=True)

    with st.container(border=True):
        st.subheader("Vídeo analisado")
        st.caption("Arquivo utilizado para gerar esta análise.")
        st.video(video_path)

    st.markdown("</div>", unsafe_allow_html=True)


def render_result_actions():
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


def render_analysis_intro():
    st.title("Análise")

    st.write(
        "Envie um vídeo para iniciar a análise da sua comunicação. "
        "Após o envio, confira a pré-visualização antes de processar."
    )


def get_remaining_analyses_or_show_error(user_id: str, access_token: str):
    if not has_network_connection():
        st.error("Erro, verifique sua conexão com a rede.")
        render_back_to_home_button()
        return None

    try:
        return get_remaining_monthly_analyses_supabase(user_id, access_token)
    except Exception:
        st.error("Erro, verifique sua conexão com a rede.")
        render_back_to_home_button()
        return None


def render_monthly_limit_status(remaining_analyses: int) -> bool:
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
        return False

    return True


def render_video_uploader(user_id: str, access_token: str):
    with st.container(border=True):
        st.markdown("### Enviar vídeo")

        uploaded_file = st.file_uploader(
            "Envie um vídeo",
            type=["mp4", "mov", "avi", "mkv"]
        )

        st.caption("Formatos aceitos: MP4, MOV, AVI, MKV • Até 2GB")

        if not uploaded_file:
            return

        handle_uploaded_video(uploaded_file)

        st.divider()

        render_video_preview()

        if st.button("Analisar vídeo"):
            process_video_analysis(user_id, access_token)


def handle_uploaded_video(uploaded_file):
    current_file_name = st.session_state.get("uploaded_file_name")

    if current_file_name == uploaded_file.name:
        return

    st.session_state["uploaded_file_name"] = uploaded_file.name
    st.session_state.pop("report", None)

    video_path = f"data/input/{uploaded_file.name}"
    audio_path = "data/temp/audio.wav"

    save_uploaded_file(uploaded_file, video_path)

    st.session_state["video_path"] = video_path
    st.session_state["audio_path"] = audio_path


def render_video_preview():
    st.markdown("### Pré-visualização do vídeo")
    st.caption("Confira se o arquivo enviado está correto antes de analisar.")

    preview_col, _ = st.columns([0.72, 0.28])

    with preview_col:
        st.video(st.session_state["video_path"])


def can_user_create_analysis_or_show_warning(
    user_id: str,
    access_token: str
) -> bool:
    try:
        can_create_analysis = can_create_analysis_supabase(
            user_id,
            access_token
        )
    except Exception:
        st.error("Erro, verifique sua conexão com a rede.")
        return False

    if not can_create_analysis:
        st.warning(
            f"Você atingiu o limite mensal de {MONTHLY_ANALYSIS_LIMIT} análises. "
            "Tente novamente no próximo mês ou entre em contato com a equipe."
        )
        return False

    return True


def process_video_analysis(user_id: str, access_token: str):
    if not can_user_create_analysis_or_show_warning(user_id, access_token):
        return

    video_path = st.session_state.get("video_path")
    audio_path = st.session_state.get("audio_path")

    if not video_path or not audio_path:
        st.error("Não foi possível localizar o vídeo enviado. Tente enviar novamente.")
        return

    with st.spinner("Processando vídeo..."):
        report = generate_report(
            video_path,
            audio_path,
            user_id,
            access_token
        )

        if not report:
            return

        st.session_state["report"] = report
        st.success("Análise concluída e salva no histórico.")
        st.rerun()


def render_audio_analysis_placeholder(user_id: str, access_token: str):
    remaining = get_remaining_analyses_or_show_error(user_id, access_token)

    if remaining is None:
        return

    render_monthly_limit_status(remaining)

    st.subheader("Grave seu discurso")

    st.write(
        "Na versão web, a análise será feita a partir do áudio gravado diretamente pelo navegador."
    )

    audio_file = st.audio_input("Clique para gravar seu áudio")

    if audio_file:
        st.audio(audio_file)

        if st.button("Analisar áudio", type="primary"):
            if not can_user_create_analysis_or_show_warning(user_id, access_token):
                return

            audio_path = save_recorded_audio(audio_file)

            st.session_state["audio_path"] = audio_path
            st.session_state["uploaded_file_name"] = "Áudio gravado pelo navegador"

            with st.spinner("Analisando seu áudio..."):
                report = generate_report_from_audio(
                    audio_path,
                    user_id,
                    access_token
                )

            if report:
                st.session_state["report"] = report
                st.success("Análise concluída com sucesso.")
                st.rerun()


def render_analysis(user_id: str, access_token: str):
    if "report" in st.session_state:
        render_analysis_result()
        return

    render_analysis_intro()

    st.caption(get_app_mode_label())

    if is_web_mode():
        render_audio_analysis_placeholder(user_id, access_token)
        render_back_to_home_button()
        return

    remaining_analyses = get_remaining_analyses_or_show_error(
        user_id,
        access_token
    )

    if remaining_analyses is None:
        return

    can_continue = render_monthly_limit_status(remaining_analyses)

    if not can_continue:
        return

    render_video_uploader(user_id, access_token)

    render_back_to_home_button()