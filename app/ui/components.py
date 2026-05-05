import streamlit as st


def render_ai_warning():
    st.warning(
        "⚠️ Esta análise foi gerada sem a avaliação da IA. "
        "Os resultados podem apresentar inconsistências."
    )


def render_analysis_title(title: str, ai_available: bool):
    if ai_available:
        st.write(f"📄 {title}")
    else:
        st.write(f"⚠️ 📄 {title}")
        st.caption("Análise feita sem IA. Resultados podem ser inconsistentes.")


def render_score_badge(score: int, color: str):
    st.markdown(
        f"""
        <div style="
            background-color: {color};
            padding: 8px 12px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            color: white;
        ">
            {score}/100
        </div>
        """,
        unsafe_allow_html=True
    )