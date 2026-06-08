import streamlit as st


def render_back_to_home_button():
    st.divider()

    if st.button("Voltar para início"):
        st.session_state["page"] = "home"
        st.rerun()