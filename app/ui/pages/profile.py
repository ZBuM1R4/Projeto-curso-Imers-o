from pathlib import Path

import streamlit as st

from app.database.profile_db import get_profile, save_profile
from app.services.network_checker import has_network_connection
from app.services.temp_file_cleaner import clean_temp_files
from app.ui.components.avatar import (
    render_avatar,
    render_uploaded_avatar_preview,
)
from app.ui.components.navigation import render_back_to_home_button


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
            neighborhood = st.text_input(
                "Bairro",
                value=profile.get("neighborhood", "")
            )

        col3, col4 = st.columns(2)

        with col3:
            city = st.text_input("Cidade", value=profile.get("city", ""))

        with col4:
            state = st.text_input(
                "Estado",
                value=profile.get("state", ""),
                max_chars=2
            )

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