import base64
from pathlib import Path

import streamlit as st


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