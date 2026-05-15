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
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        [data-testid="collapsedControl"] {
            display: none;
        }

        [data-testid="stSidebarCollapseButton"] {
            display: none;
        }

        button[title="Close sidebar"] {
            display: none;
        }

        button[title="Open sidebar"] {
            display: none;
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


def render_avatar(avatar_url: str, width: int = 120):
    if avatar_url and Path(avatar_url).exists():
        st.image(avatar_url, width=width)
    else:
        st.markdown(
            f"""
            <div style="
                width:{width}px;
                height:{width}px;
                border-radius:50%;
                background:#2b2d36;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:42px;
                margin-bottom:10px;
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
                border-radius:50%;
                overflow:hidden;
                background:#2b2d36;
                display:flex;
                align-items:center;
                justify-content:center;
                margin-bottom:10px;
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

    with st.sidebar:
        st.title("Menu")

        if profile:
            render_avatar(profile.get("avatar_url", ""), width=90)
            st.write(f"**{profile.get('first_name', '')} {profile.get('last_name', '')}**")

        if st.button("Análise"):
            st.session_state["page"] = "home"
            st.rerun()

        if st.button("Histórico"):
            st.session_state["page"] = "history"
            st.rerun()

        if st.button("Perfil"):
            st.session_state["page"] = "profile"
            st.rerun()

        st.divider()

        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()


def render_back_to_home_button():
    st.divider()

    if st.button("Voltar para Análise"):
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
            background: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            font-weight: bold;
            color: #222222;
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
        <div style="
            background-color: {color};
            padding: 8px 12px;
            border-radius: 10px;
            text-align: center;
            color: white;
            font-weight: bold;
            min-width: 80px;
        ">
            {score}/100
        </div>
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
        st.caption("🔴 vício de linguagem")
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
    for ponto in report["pontos_atencao"]:
        st.write(f"⚠️ {ponto}")

    st.subheader("Vícios de linguagem")
    vicios = report.get("vicios_de_linguagem", {})

    if vicios:
        for termo, qtd in vicios.items():
            st.write(f"🔹 {termo}: {qtd} ocorrência(s)")
    else:
        st.write("Nenhum vício de linguagem encontrado.")

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


def render_home(user_id: str, access_token: str):
    st.title("Análise")

    if "video_path" not in st.session_state and "report" not in st.session_state:
        st.markdown(
            """
            ## Análise de oratória por inteligência artificial

            Envie um vídeo para receber uma análise inicial da sua comunicação,
            incluindo transcrição, vícios de linguagem, pausas, repetições,
            pontos de atenção e uma avaliação geral por inteligência artificial.

            Acompanhe sua evolução ao longo do tempo pelo histórico de análises.
            """
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Nova análise")
            st.write("Envie um novo vídeo para gerar uma avaliação da sua comunicação.")
            start_new_analysis = st.button("Nova análise")

        with col2:
            st.markdown("### Acompanhe seu desempenho")
            st.write("Veja análises anteriores, scores e evolução do seu desempenho.")
            go_to_history = st.button("Ver histórico")

        if go_to_history:
            if not has_network_connection():
                st.error("Erro, verifique sua conexão com a rede.")
                return

            st.session_state["page"] = "history"
            st.rerun()

        if not start_new_analysis:
            return

    uploaded_file = st.file_uploader(
        "Envie um vídeo",
        type=["mp4", "mov", "avi", "mkv"]
    )

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

        st.subheader("Pré-visualização do vídeo")
        st.video(video_path)

    if "video_path" in st.session_state and "audio_path" in st.session_state:
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

    if "report" in st.session_state:
        render_report_details(
            st.session_state["report"],
            video_name=st.session_state.get("video_path", "video_analisado")
        )


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
        render_sidebar(user_id, access_token)

        if "page" not in st.session_state:
            st.session_state["page"] = "home"

        if st.session_state["page"] == "home":
            render_home(user_id, access_token)
        elif st.session_state["page"] == "history":
            render_history(user_id, access_token)
        elif st.session_state["page"] == "detail":
            render_detail(user_id, access_token)
        elif st.session_state["page"] == "profile":
            render_profile(user_id, access_token)