import streamlit as st


def get_current_user_id():
    user = st.session_state.get("user")
    return user.id if user else None


def get_access_token():
    return st.session_state.get("access_token")


def clear_analysis_session():
    st.session_state.pop("report", None)
    st.session_state.pop("video_path", None)
    st.session_state.pop("audio_path", None)
    st.session_state.pop("uploaded_file_name", None)