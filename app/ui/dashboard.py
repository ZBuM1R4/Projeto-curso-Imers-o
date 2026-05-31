import base64
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from app.database.profile_db import get_profile, profile_exists, save_profile
from app.database.supabase_db import (
    MONTHLY_ANALYSIS_LIMIT,
    can_create_analysis_supabase,
    delete_analysis_supabase,
    get_all_analyses_supabase,
    get_analysis_by_id_supabase,
    get_average_score_supabase,
    get_history_stats_supabase,
    get_remaining_monthly_analyses_supabase,
    save_analysis_supabase,
)
from app.services.attention_points_analyzer import generate_attention_points
from app.services.audio_extractor import extract_audio
from app.services.docx_exporter import build_docx_report
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
from app.services.supabase_client import get_supabase_client
from app.services.transcriber import transcribe_audio
from app.services.temp_file_cleaner import clean_temp_files
from app.utils.file_manager import save_uploaded_file
from app.utils.validators import get_password_rules_message, is_valid_password
from app.ui.styles import apply_global_styles
from app.ui.components.sidebar import render_sidebar


st.set_page_config(
    page_title="Análise de Comunicação",
    layout="wide",
    initial_sidebar_state="expanded"
)


supabase = get_supabase_client()


def translate_auth_error(error_message: str) -> str:
    error_message = error_message.lower()

    if "user already registered" in error_message:
        return "Este e-mail já possui cadastro."

    if "invalid login credentials" in error_message:
        return "E-mail ou senha incorretos."

    if "email not confirmed" in error_message:
        return "E-mail ainda não confirmado. Verifique sua caixa de entrada."

    if "password" in error_message:
        return get_password_rules_message()

    return "Não foi possível concluir a operação. Verifique os dados informados."


def save_avatar_image(uploaded_file, user_id: str) -> str:
    if uploaded_file is None:
        return ""

    avatar_dir = Path("data/profile_images")
    avatar_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(uploaded_file.name).suffix.lower()

    if suffix not in [".png", ".jpg", ".jpeg", ".webp"]:
        suffix = ".png"

    avatar_path = avatar_dir / f"{user_id}{suffix}"

    with open(avatar_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    return str(avatar_path)


def image_to_base64(image_path: str) -> str:
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception:
        return ""


def render_avatar(avatar_url: str, width: int = 120):
    if avatar_url and Path(avatar_url).exists():
        encoded = image_to_base64(avatar_url)
        suffix = Path(avatar_url).suffix.lower().replace(".", "")

        mime_type = "jpeg" if suffix in ["jpg", "jpeg"] else suffix
        if mime_type not in ["png", "jpeg", "webp"]:
            mime_type = "png"

        st.markdown(
            f"""
            <div style="
                width:{width}px;
                height:{width}px;
                border-radius:18px;
                overflow:hidden;
                background:#2b2d36;
                margin-bottom:10px;
                border:1px solid rgba(148, 163, 184, 0.16);
            ">
                <img src="data:image/{mime_type};base64,{encoded}" style="
                    width:100%;
                    height:100%;
                    object-fit:cover;
                ">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="
                width:{width}px;
                height:{width}px;
                border-radius:18px;
                background:#2b2d36;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:42px;
                margin-bottom:10px;
                border:1px solid rgba(148, 163, 184, 0.16);
            ">
                👤
            </div>
            """,
            unsafe_allow_html=True
        )


def render_uploaded_avatar_preview(uploaded_file, width: int = 120):
    if uploaded_file:
        file_bytes = uploaded_file.getvalue()
        encoded = base64.b64encode(file_bytes).decode()

        st.markdown(
            f"""
            <div style="
                width:{width}px;
                height:{width}px;
                border-radius:18px;
                overflow:hidden;
                background:#2b2d36;
                display:flex;
                align-items:center;
                justify-content:center;
                margin-bottom:10px;
                border:1px solid rgba(148, 163, 184, 0.16);
            ">
                <img src="data:image/png;base64,{encoded}" style="
                    width:100%;
                    height:100%;
                    object-fit:cover;
                ">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        render_avatar("", width=width)


def render_login():
    st.title("Análise de Comunicação")
    st.subheader("Acesse sua conta")

    tab_login, tab_signup = st.tabs(["Entrar", "Criar conta"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar")

            if submitted:
                if not has_network_connection():
                    st.error("Erro, verifique sua conexão com a rede.")
                    return

                try:
                    response = supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })

                    clean_temp_files()

                    st.session_state["user"] = response.user
                    st.session_state["access_token"] = response.session.access_token
                    st.success("Login realizado com sucesso!")
                    st.rerun()

                except Exception as e:
                    st.error(translate_auth_error(str(e)))

    with tab_signup:
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Senha", type="password", key="signup_password")
            confirm_password = st.text_input(
                "Confirmar senha",
                type="password",
                key="signup_confirm_password"
            )

            st.caption(get_password_rules_message())

            submitted = st.form_submit_button("Criar conta")

            if submitted:
                if not has_network_connection():
                    st.error("Erro, verifique sua conexão com a rede.")
                    return

                if password != confirm_password:
                    st.error("As senhas não coincidem.")
                    return

                if not is_valid_password(password):
                    st.error(get_password_rules_message())
                    return

                try:
                    response = supabase.auth.sign_up({
                        "email": email,
                        "password": password
                    })

                    if response.session:

                        clean_temp_files()

                        st.session_state["user"] = response.user
                        st.session_state["access_token"] = response.session.access_token
                        st.success("Conta criada com sucesso! Complete seu cadastro.")
                        st.rerun()
                    else:
                        st.success("Conta criada com sucesso! Agora faça login.")

                except Exception as e:
                    st.error(translate_auth_error(str(e)))


def render_complete_profile(user_id: str, access_token: str):
    st.title("Complete seu cadastro")
    st.write("Antes de continuar, preencha suas informações pessoais.")

    if st.button("Logout"):
        clean_temp_files()
        st.session_state.clear()
        st.rerun()

    st.subheader("Foto de perfil")

    avatar_file = st.file_uploader(
        "Foto de perfil (opcional)",
        type=["png", "jpg", "jpeg", "webp"]
    )

    render_uploaded_avatar_preview(avatar_file, width=120)

    with st.form("profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            first_name = st.text_input("Nome")
            cpf = st.text_input("CPF", placeholder="000.000.000-00")
            cep = st.text_input("CEP", placeholder="00000-000")
            number = st.text_input("Número")

        with col2:
            last_name = st.text_input("Sobrenome")
            phone = st.text_input("Telefone", placeholder="+55 (31) 99999-9999")
            street = st.text_input("Rua")
            neighborhood = st.text_input("Bairro")

        col3, col4 = st.columns(2)

        with col3:
            city = st.text_input("Cidade")

        with col4:
            state = st.text_input("Estado", placeholder="MG", max_chars=2)

        submitted = st.form_submit_button("Salvar cadastro")

        if submitted:
            if not has_network_connection():
                st.error("Erro, verifique sua conexão com a rede.")
                return

            avatar_url = save_avatar_image(avatar_file, user_id)

            result = save_profile(
                user_id=user_id,
                access_token=access_token,
                first_name=first_name,
                last_name=last_name,
                cpf=cpf,
                phone=phone,
                cep=cep,
                street=street,
                number=number,
                neighborhood=neighborhood,
                city=city,
                state=state,
                avatar_url=avatar_url,
            )

            if result["success"]:
                st.success(result["message"])
                st.rerun()
            else:
                st.error(result["message"])


def render_back_to_home_button():
    st.divider()

    if st.button("Voltar para início"):
        st.session_state["page"] = "home"
        st.rerun()


def get_current_user_id():
    user = st.session_state.get("user")
    return user.id if user else None


def get_access_token():
    return st.session_state.get("access_token")


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


def render_ai_warning():
    st.warning(
        "⚠️ Esta análise foi gerada sem a avaliação da IA. "
        "Os resultados podem apresentar inconsistências."
    )


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
            st.error("Erro ao conectar com a IA.")
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


def render_report_details(report: dict, video_name: str = "video_analisado"):
    score_data = report["score_comunicacao"]

    st.subheader("Score de comunicação")
    st.metric("Pontuação geral", f"{score_data['score']}/100")
    st.write(f"**Classificação:** {score_data['classificacao']}")
    st.write(score_data["comentario"])

    analise_ia = report.get("analise_global_ia", {})

    if not analise_ia.get("disponivel", False):
        render_ai_warning()

    st.subheader("Transcrição")
    st.write(report["transcricao"])

    st.subheader("Análise global por IA")
    st.write(analise_ia.get("analise", ""))

    st.subheader("Pontos de atenção")

    pontos_filtrados = []

    for ponto in report.get("pontos_atencao", []):
        ponto_lower = ponto.lower()

        if "uso frequente" in ponto_lower:
            continue

        if "vício" in ponto_lower or "vicio" in ponto_lower:
            continue

        if "vícios" in ponto_lower or "vicios" in ponto_lower:
            continue

        pontos_filtrados.append(ponto)

    if pontos_filtrados:
        for ponto in pontos_filtrados:
            st.write(f"⚠️ {ponto}")
    else:
        st.write("Nenhum ponto crítico identificado nesta análise.")

    st.subheader("Pausas")
    pausas = report.get("pausas", {})

    st.write(f"⏱ Duração total: {pausas.get('duracao_total', 0)}s")
    st.write(f"🛑 Pausas longas: {pausas.get('quantidade_pausas_longas', 0)}")
    st.write(f"🔇 Tempo em silêncio: {pausas.get('tempo_total_silencio', 0)}s")

    pausas_longas = pausas.get("pausas_longas", [])

    if pausas_longas:
        st.write("Pausas detectadas:")
        for pausa in pausas_longas:
            st.write(
                f"- {round(pausa['start'], 2)}s → "
                f"{round(pausa['end'], 2)}s "
                f"({round(pausa['duration'], 2)}s)"
            )
    else:
        st.write("Nenhuma pausa longa detectada.")

    st.subheader("Repetições")
    repeticoes = report.get("repeticoes", {})

    sequenciais = repeticoes.get("sequenciais", [])
    termos_recorrentes = repeticoes.get("termos_recorrentes", {})

    if sequenciais:
        st.write("Repetições em sequência:")
        for repeticao in sequenciais:
            st.write(f"- {repeticao['termo']}")
    else:
        st.write("Nenhuma repetição em sequência.")

    if termos_recorrentes:
        st.write("Termos mais recorrentes:")
        for termo, qtd in termos_recorrentes.items():
            st.write(f"- {termo}: {qtd}")
    else:
        st.write("Nenhum termo recorrente relevante.")

    st.divider()

    docx_bytes = build_docx_report(report, video_name=video_name)

    st.download_button(
        label="Baixar relatório em DOCX",
        data=docx_bytes,
        file_name="relatorio_analise_comunicacao.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


def render_home_intro(profile: dict):
    first_name = profile.get("first_name", "").strip() if profile else ""
    name_label = first_name if first_name else "usuário"

    st.markdown(
        f"""
        <div class="welcome-pill">
            Bem-vindo de volta, {name_label} 👋
        </div>

        <div class="hero-title">
            Vamos analisar sua<br>comunicação?
        </div>

        <div class="hero-description">
            Envie um vídeo da sua oratória e receba uma análise completa com
            transcrição, hábitos de linguagem, pausas, repetições, pontos de atenção
            e uma avaliação geral por inteligência artificial.
        </div>
        """,
        unsafe_allow_html=True
    )


def render_home(user_id: str, access_token: str):
    profile = get_profile(user_id, access_token)
    first_name = profile.get("first_name", "").strip() if profile else ""
    name_label = first_name if first_name else "usuário"

    st.markdown(
        f"""
        <div class="welcome-pill">
            Bem-vindo de volta, {name_label} 👋
        </div>

        <div class="hero-title">
            Vamos analisar sua<br>comunicação?
        </div>

        <div class="hero-description">
            Envie um vídeo da sua oratória e receba uma análise completa com
            transcrição, organização da fala, pausas, repetições, pontos de atenção
            e uma avaliação geral por inteligência artificial.
        </div>
        """,
        unsafe_allow_html=True
    )

    col_analysis, col_history = st.columns([1.15, 0.85])

    with col_analysis:
        with st.container(border=True):
            st.markdown(
                """
                <div class="home-action-card">
                    <div class="home-action-icon">☁️</div>
                    <div class="home-action-title">Iniciar uma nova análise</div>
                    <div class="home-action-text">
                        Envie um vídeo da sua apresentação ou fala para receber
                        um feedback estruturado sobre sua comunicação.
                    </div>
                    <div class="home-action-note">
                        Formatos aceitos: MP4, MOV, AVI, MKV · Até 2GB
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            col_a, col_b, col_c = st.columns([1, 1.4, 1])

            with col_b:
                if st.button("Iniciar análise", use_container_width=True):
                    clean_temp_files()

                    st.session_state["page"] = "analysis"
                    st.session_state.pop("report", None)
                    st.session_state.pop("video_path", None)
                    st.session_state.pop("audio_path", None)
                    st.session_state.pop("uploaded_file_name", None)
                    st.rerun()

    with col_history:
        with st.container(border=True):
            st.markdown(
                """
                <div class="home-action-card">
                    <div class="home-action-icon">📈</div>
                    <div class="home-action-title">Acompanhe sua evolução</div>
                    <div class="home-action-text">
                        Veja análises anteriores, acompanhe seus scores e observe
                        sua evolução ao longo do tempo.
                    </div>
                    <div class="home-action-note">
                        Histórico organizado por análise e desempenho.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            col_a, col_b, col_c = st.columns([1, 1.4, 1])

            with col_b:
                if st.button("Ver histórico", use_container_width=True):
                    if not has_network_connection():
                        st.error("Erro, verifique sua conexão com a rede.")
                        return

                    st.session_state["page"] = "history"
                    st.rerun()

    st.markdown(
        """
        <div class="privacy-card">
            <div class="privacy-icon">🔒</div>
            <div>
                <div class="privacy-title">Privacidade e segurança em primeiro lugar</div>
                <div class="privacy-text">
                    Seus vídeos são privados e utilizados apenas para análise.
                    Não compartilhamos seu conteúdo com terceiros.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


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
                
                st.session_state.pop("report", None)
                st.session_state.pop("video_path", None)
                st.session_state.pop("audio_path", None)
                st.session_state.pop("uploaded_file_name", None)
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


def render_profile(user_id: str, access_token: str):
    profile = get_profile(user_id, access_token)

    if not profile:
        st.warning("Perfil não encontrado.")
        render_back_to_home_button()
        return

    st.title("Meu perfil")

    render_avatar(profile.get("avatar_url", ""), width=140)

    avatar_file = st.file_uploader(
        "Alterar foto de perfil (opcional)",
        type=["png", "jpg", "jpeg", "webp"]
    )

    if avatar_file:
        render_uploaded_avatar_preview(avatar_file, width=120)

    with st.form("edit_profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            first_name = st.text_input("Nome", value=profile.get("first_name", ""))
            cpf = st.text_input("CPF", value=profile.get("cpf", ""))
            cep = st.text_input("CEP", value=profile.get("cep", ""))
            number = st.text_input("Número", value=profile.get("number", ""))

        with col2:
            last_name = st.text_input("Sobrenome", value=profile.get("last_name", ""))
            phone = st.text_input("Telefone", value=profile.get("phone", ""))
            street = st.text_input("Rua", value=profile.get("street", ""))
            neighborhood = st.text_input("Bairro", value=profile.get("neighborhood", ""))

        col3, col4 = st.columns(2)

        with col3:
            city = st.text_input("Cidade", value=profile.get("city", ""))

        with col4:
            state = st.text_input("Estado", value=profile.get("state", ""), max_chars=2)

        submitted = st.form_submit_button("Salvar alterações")

        if submitted:
            if not has_network_connection():
                st.error("Erro, verifique sua conexão com a rede.")
                return

            avatar_url = profile.get("avatar_url", "")

            if avatar_file:
                avatar_url = save_avatar_image(avatar_file, user_id)

            result = save_profile(
                user_id=user_id,
                access_token=access_token,
                first_name=first_name,
                last_name=last_name,
                cpf=cpf,
                phone=phone,
                cep=cep,
                street=street,
                number=number,
                neighborhood=neighborhood,
                city=city,
                state=state,
                avatar_url=avatar_url,
            )

            if result["success"]:
                st.success("Perfil atualizado com sucesso.")
                st.rerun()
            else:
                st.error(result["message"])

    render_back_to_home_button()


def run_app():
    apply_global_styles()

    user_id = get_current_user_id()
    access_token = get_access_token()

    if not user_id or not access_token:
        render_login()
    else:
        if not has_network_connection():
            st.error("Erro, verifique sua conexão com a rede.")

        elif not profile_exists(user_id, access_token):
            render_complete_profile(user_id, access_token)

        else:
            if "page" not in st.session_state:
                st.session_state["page"] = "home"

            render_sidebar(user_id, access_token, render_avatar)

            current_page = st.session_state.get("page", "home")

            if current_page == "home":
                render_home(user_id, access_token)

            elif current_page == "analysis":
                render_analysis(user_id, access_token)

            elif current_page == "history":
                render_history(user_id, access_token)

            elif current_page == "detail":
                render_detail(user_id, access_token)

            elif current_page == "profile":
                render_profile(user_id, access_token)

            else:
                st.session_state["page"] = "home"
                st.rerun()


if __name__ == "__main__":
    run_app()