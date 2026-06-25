import base64
from html import escape
from pathlib import Path

import streamlit as st


def is_remote_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def image_to_base64(image_path: str) -> str:
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception:
        return ""


def render_avatar_image(image_src: str, width: int = 120):
    safe_src = escape(image_src, quote=True)

    st.markdown(
        f"""
        <div style="
            width:{width}px;
            height:{width}px;
            border-radius:18px;
            overflow:hidden;
            background:#082B36;
            margin-bottom:10px;
            border:1px solid rgba(217, 226, 231, 0.16);
        ">
            <img src="{safe_src}" style="
                width:100%;
                height:100%;
                object-fit:cover;
            ">
        </div>
        """,
        unsafe_allow_html=True
    )


def render_avatar_placeholder(width: int = 120):
    st.markdown(
        f"""
        <div style="
            width:{width}px;
            height:{width}px;
            border-radius:18px;
            background:#082B36;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:42px;
            margin-bottom:10px;
            border:1px solid rgba(217, 226, 231, 0.16);
        ">
            👤
        </div>
        """,
        unsafe_allow_html=True
    )


def render_avatar(avatar_url: str, width: int = 120):
    if avatar_url and is_remote_url(avatar_url):
        render_avatar_image(avatar_url, width=width)
        return

    if avatar_url and Path(avatar_url).exists():
        encoded = image_to_base64(avatar_url)
        suffix = Path(avatar_url).suffix.lower().replace(".", "")

        mime_type = "jpeg" if suffix in ["jpg", "jpeg"] else suffix

        if mime_type not in ["png", "jpeg", "webp"]:
            mime_type = "png"

        render_avatar_image(
            f"data:image/{mime_type};base64,{encoded}",
            width=width
        )
        return

    render_avatar_placeholder(width=width)


def render_uploaded_avatar_preview(uploaded_file, width: int = 120):
    if uploaded_file:
        file_bytes = uploaded_file.getvalue()
        encoded = base64.b64encode(file_bytes).decode()

        render_avatar_image(
            f"data:image/png;base64,{encoded}",
            width=width
        )
    else:
        render_avatar("", width=width)