import base64
from pathlib import Path

import streamlit as st

from app.database.profile_db import get_profile, profile_exists, save_profile
from app.database.supabase_db import (
    delete_analysis_supabase,
    get_all_analyses_supabase,
    get_analysis_by_id_supabase,
    get_average_score_supabase,
    get_history_stats_supabase,
    save_analysis_supabase,
)
from app.services.attention_points_analyzer import generate_attention_points
from app.services.audio_extractor import extract_audio
from app.services.docx_exporter import build_docx_report
from app.services.filler_word_analyzer import analyze_filler_words
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
from app.services.transcription_marker import highlight_transcription
from app.utils.file_manager import save_uploaded_file
from app.utils.validators import get_password_rules_message, is_valid_password


st.set_page_config(
    page_title="Análise de Comunicação",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown(
    """
    <style>
        :root {
            --bg-main: #070b14;
            --bg-card: rgba(18, 24, 38, 0.84);
            --bg-card-soft: rgba(22, 29, 46, 0.72);
            --border-soft: rgba(148, 163, 184, 0.18);
            --border-accent: rgba(99, 102, 241, 0.55);
            --text-main: #f8fafc;
            --text-muted: #aab4c4;
            --text-soft: #7d8798;
            --accent-blue: #4f7cff;
            --accent-purple: #7c3aed;
            --accent-green: #34d399;
        }

        html, body, [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 20% 10%, rgba(79, 124, 255, 0.10), transparent 28%),
                radial-gradient(circle at 80% 30%, rgba(124, 58, 237, 0.12), transparent 32%),
                linear-gradient(135deg, #070b14 0%, #0a0f1c 48%, #070b14 100%) !important;
            color: var(--text-main);
        }

        [data-testid="stHeader"] {
            background: transparent !important;
        }

        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapseButton"],
        button[title="Close sidebar"],
        button[title="Open sidebar"] {
            display: none !important;
        }

        [data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(15, 20, 34, 0.98), rgba(10, 14, 24, 0.98)) !important;
            border-right: 1px solid rgba(148, 163, 184, 0.14);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 2rem;
        }

        .block-container {
            max-width: 1240px;
            padding-top: 2.4rem;
            padding-left: 4rem;
            padding-right: 4rem;
        }

        h1, h2, h3 {
            letter-spacing: -0.04em;
        }

        p {
            color: var(--text-muted);
            line-height: 1.65;
        }

        div.stButton > button {
            border-radius: 12px;
            border: 1px solid rgba(148, 163, 184, 0.22);
            background: rgba(15, 23, 42, 0.72);
            color: #f8fafc;
            padding: 0.72rem 1.05rem;
            font-weight: 700;
            transition: all 0.2s ease;
        }

        div.stButton > button:hover {
            border-color: rgba(99, 102, 241, 0.75);
            background: rgba(79, 124, 255, 0.18);
            color: #ffffff;
            transform: translateY(-1px);
        }

        [data-testid="stFileUploader"] {
            background: rgba(15, 23, 42, 0.72);
            border: 1px dashed rgba(148, 163, 184, 0.26);
            border-radius: 22px;
            padding: 1.2rem;
        }

        [data-testid="stFileUploader"] section {
            border: none !important;
            background: transparent !important;
        }

        .app-shell {
            border: 1px solid rgba(148, 163, 184, 0.12);
            border-radius: 28px;
            background:
                radial-gradient(circle at 30% 20%, rgba(79, 124, 255, 0.08), transparent 32%),
                radial-gradient(circle at 80% 40%, rgba(124, 58, 237, 0.10), transparent 34%),
                rgba(8, 13, 24, 0.42);
            padding: 0;
        }

        .brand-wrap {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 2.2rem;
        }

        .brand-icon {
            width: 38px;
            height: 38px;
            border-radius: 12px;
            background: linear-gradient(135deg, #4f7cff, #7c3aed);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 34px rgba(99, 102, 241, 0.32);
            font-size: 20px;
        }

        .brand-title {
            font-size: 1.08rem;
            font-weight: 800;
            line-height: 1.08;
            color: #f8fafc;
        }

        .sidebar-profile-card {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 1rem;
            margin-bottom: 1.3rem;
            border-radius: 18px;
            background: rgba(15, 23, 42, 0.62);
            border: 1px solid rgba(148, 163, 184, 0.14);
        }

        .sidebar-profile-name {
            font-weight: 800;
            color: #f8fafc;
            margin-bottom: 2px;
        }

        .sidebar-profile-email {
            color: #94a3b8;
            font-size: 0.82rem;
        }

        .sidebar-section-divider {
            height: 1px;
            background: rgba(148, 163, 184, 0.14);
            margin: 1.6rem 0;
        }

        .welcome-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            border: 1px solid rgba(148, 163, 184, 0.16);
            background: rgba(15, 23, 42, 0.62);
            color: #bcd0ff;
            border-radius: 999px;
            padding: 0.52rem 0.9rem;
            font-size: 0.92rem;
            margin-bottom: 1.2rem;
        }

        .hero-title {
            font-size: clamp(2.35rem, 4.4vw, 4.2rem);
            line-height: 1.04;
            font-weight: 850;
            letter-spacing: -0.065em;
            color: #f8fafc;
            margin-bottom: 1.15rem;
        }

        .hero-description {
            max-width: 760px;
            color: #aab4c4;
            font-size: 1.13rem;
            line-height: 1.75;
            margin-bottom: 2.2rem;
        }

        .home-grid {
            display: grid;
            grid-template-columns: minmax(0, 1.12fr) minmax(320px, 0.88fr);
            gap: 1.4rem;
            margin-top: 1.4rem;
            margin-bottom: 1.25rem;
        }

        .upload-card {
            min-height: 300px;
            border-radius: 26px;
            border: 1px solid rgba(99, 102, 241, 0.48);
            background:
                radial-gradient(circle at 50% 10%, rgba(79, 124, 255, 0.18), transparent 36%),
                linear-gradient(135deg, rgba(18, 24, 38, 0.92), rgba(18, 24, 38, 0.58));
            box-shadow:
                0 0 0 1px rgba(255,255,255,0.02) inset,
                0 24px 80px rgba(0, 0, 0, 0.25);
            padding: 1.25rem;
        }

        .upload-card-inner {
            height: 100%;
            min-height: 260px;
            border: 1px dashed rgba(148, 163, 184, 0.20);
            border-radius: 22px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 2rem;
        }

        .upload-icon {
            width: 92px;
            height: 92px;
            border-radius: 50%;
            background:
                radial-gradient(circle, rgba(79, 124, 255, 0.32), rgba(79, 124, 255, 0.08));
            border: 1px solid rgba(99, 102, 241, 0.22);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.45rem;
            margin-bottom: 1.3rem;
            color: #7da2ff;
        }

        .upload-title {
            font-size: 1.42rem;
            font-weight: 800;
            color: #f8fafc;
            margin-bottom: 0.35rem;
        }

        .upload-subtitle {
            color: #aab4c4;
            margin-bottom: 1.4rem;
        }

        .gradient-button-fake {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            border-radius: 14px;
            padding: 0.9rem 2rem;
            min-width: 230px;
            background: linear-gradient(135deg, #4f7cff, #7c3aed);
            color: white;
            font-weight: 800;
            box-shadow: 0 16px 38px rgba(79, 124, 255, 0.22);
            margin-bottom: 1rem;
        }

        .formats-text {
            color: #94a3b8;
            font-size: 0.92rem;
        }

        .history-card {
            position: relative;
            min-height: 300px;
            overflow: hidden;
            border-radius: 26px;
            border: 1px solid rgba(148, 163, 184, 0.16);
            background:
                radial-gradient(circle at 85% 20%, rgba(124, 58, 237, 0.24), transparent 30%),
                linear-gradient(135deg, rgba(18, 24, 38, 0.86), rgba(18, 24, 38, 0.52));
            padding: 2rem;
        }

        .history-icon {
            width: 78px;
            height: 78px;
            border-radius: 50%;
            background:
                radial-gradient(circle, rgba(124, 58, 237, 0.32), rgba(124, 58, 237, 0.08));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            margin-bottom: 2rem;
        }

        .history-title {
            font-size: 1.45rem;
            font-weight: 800;
            color: #f8fafc;
            margin-bottom: 0.6rem;
        }

        .history-description {
            color: #aab4c4;
            max-width: 340px;
            margin-bottom: 1.4rem;
        }

        .chart-art {
            position: absolute;
            right: -10px;
            bottom: -2px;
            width: 260px;
            height: 150px;
            opacity: 0.72;
        }

        .chart-line {
            stroke: #8b5cf6;
            stroke-width: 4;
            fill: none;
            filter: drop-shadow(0 0 8px rgba(139, 92, 246, 0.55));
        }

        .chart-area {
            fill: url(#purpleGradient);
            opacity: 0.5;
        }

        .privacy-card {
            margin-top: 1rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            border-radius: 22px;
            border: 1px solid rgba(148, 163, 184, 0.13);
            background: rgba(15, 23, 42, 0.55);
            padding: 1.1rem 1.3rem;
        }

        .privacy-icon {
            width: 48px;
            height: 48px;
            border-radius: 14px;
            background: rgba(79, 124, 255, 0.12);
            color: #8ca8ff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.45rem;
            flex: 0 0 auto;
        }

        .privacy-title {
            font-weight: 800;
            color: #f8fafc;
            margin-bottom: 0.15rem;
        }

        .privacy-text {
            color: #aab4c4;
        }

        .section-card {
            border-radius: 24px;
            border: 1px solid rgba(148, 163, 184, 0.14);
            background: rgba(15, 23, 42, 0.58);
            padding: 1.4rem;
            margin-bottom: 1rem;
        }

        .score-badge {
            padding: 0.55rem 0.85rem;
            border-radius: 999px;
            text-align: center;
            font-weight: 800;
            color: white;
            min-width: 86px;
            display: inline-block;
        }

        @media (max-width: 980px) {
            .block-container {
                padding-left: 1.6rem;
                padding-right: 1.6rem;
            }

            .home-grid {
                grid-template-columns: 1fr;
            }

            .chart-art {
                opacity: 0.35;
            }
        }
    </style>
    """,
    unsafe_allow_html=True
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


def render_sidebar(user_id: str, access_token: str):
    profile = get_profile(user_id, access_token)
    user = st.session_state.get("user")
    user_email = getattr(user, "email", "") if user else ""

    with st.sidebar:
        st.markdown(
            """
            <div class="brand-wrap">
                <div class="brand-icon">AI</div>
                <div class="brand-title">Análise de<br>Comunicação</div>
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
            st.session_state["page"] = "analysis"
            st.session_state.pop("report", None)
            st.session_state.pop("video_path", None)
            st.session_state.pop("audio_path", None)
            st.session_state.pop("uploaded_file_name", None)
            st.rerun()

        if st.button("Histórico"):
            st.session_state["page"] = "history"
            st.rerun()

        if st.button("Perfil"):
            st.session_state["page"] = "profile"
            st.rerun()

        st.markdown(
            '<div class="sidebar-section-divider"></div>',
            unsafe_allow_html=True
        )

        if st.button("Sair da conta"):
            st.session_state.clear()
            st.rerun()


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
    filler_words = analyze_filler_words(texto)
    pause_data = analyze_pauses(extracted_audio)
    sequential_repetitions = analyze_sequential_repetitions(texto)
    frequent_terms = analyze_frequent_terms(texto)

    partial_report = {
        "transcricao": texto,
        "vicios_de_linguagem": filler_words,
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
        filler_words=filler_words,
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

    show_markers = st.toggle("Exibir marcações na transcrição", value=False)

    if show_markers:
        st.caption("Legenda:")
        st.caption("🟡 termo recorrente")

        marked_text = highlight_transcription(
            report["transcricao"],
            report["repeticoes"]["termos_recorrentes"]
        )
        st.markdown(marked_text, unsafe_allow_html=True)
    else:
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
            transcrição, hábitos de linguagem, pausas, repetições, pontos de atenção
            e uma avaliação geral por inteligência artificial.
        </div>
        """,
        unsafe_allow_html=True
    )

    col_analysis, col_history = st.columns([1.15, 0.85])

    with col_analysis:
        with st.container(border=True):
            st.markdown("### ☁️ Iniciar uma nova análise")
            st.write(
                "Comece uma nova avaliação enviando um vídeo da sua apresentação "
                "ou fala para análise."
            )

            st.caption("Formatos aceitos: MP4, MOV, AVI, MKV • Até 2GB")

            if st.button("Iniciar análise"):
                st.session_state["page"] = "analysis"
                st.session_state.pop("report", None)
                st.session_state.pop("video_path", None)
                st.session_state.pop("audio_path", None)
                st.session_state.pop("uploaded_file_name", None)
                st.rerun()

    with col_history:
        with st.container(border=True):
            st.markdown("### 📈 Acompanhe sua evolução")
            st.write(
                "Veja análises anteriores, scores e sua evolução "
                "ao longo do tempo."
            )

            if st.button("Ver histórico"):
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
            with st.container(border=True):
                st.subheader("Vídeo analisado")
                st.caption("Arquivo utilizado para gerar esta análise.")
                st.video(video_path)

        st.divider()

        render_report_details(
            st.session_state["report"],
            video_name=st.session_state.get("video_path", "video_analisado")
        )

        st.divider()

        if st.button("Iniciar nova análise"):
            st.session_state.pop("report", None)
            st.session_state.pop("video_path", None)
            st.session_state.pop("audio_path", None)
            st.session_state.pop("uploaded_file_name", None)
            st.rerun()

        return

    st.title("Análise")

    st.write(
        "Envie um vídeo para iniciar a análise da sua comunicação. "
        "Após o envio, confira a pré-visualização antes de processar."
    )

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

            st.video(st.session_state["video_path"])

            if st.button("Analisar vídeo"):
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

    st.subheader("Aproveitamento geral")
    render_score_circle(avg_score)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Análises feitas", stats["total_analyses"])

    with col2:
        st.metric("Melhor score", f"{stats['best_score']}/100")

    with col3:
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

        col1, col2, col3, col4 = st.columns([5, 2, 2, 2])

        with col1:
            render_analysis_title(title, ai_available)
            st.caption(created_at)

        with col2:
            render_score_badge(score)

        with col3:
            if st.button("Abrir", key=f"open_{analysis_id}"):
                st.session_state["selected_analysis"] = analysis_id
                st.session_state["page"] = "detail"
                st.rerun()

        with col4:
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

        render_sidebar(user_id, access_token)

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