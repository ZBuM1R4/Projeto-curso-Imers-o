import streamlit as st


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
            background: #061A24;
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