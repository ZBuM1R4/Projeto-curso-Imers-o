import streamlit as st


def apply_global_styles():
    st.markdown(
        """
        <style>
            :root {
                --bg-main: #061A24;
                --bg-main-dark: #031118;
                --bg-sidebar: #04141C;
                --bg-card: rgba(8, 43, 54, 0.84);
                --bg-card-soft: rgba(11, 53, 66, 0.72);

                --border-soft: rgba(217, 226, 231, 0.16);
                --border-strong: rgba(217, 226, 231, 0.28);
                --border-accent: rgba(0, 166, 180, 0.48);

                --text-main: #F8FAFC;
                --text-muted: #A8BBC4;
                --text-soft: #D9E2E7;
                --text-subtle: #78909A;

                --accent-primary: #005F73;
                --accent-primary-light: #0A7C8C;
                --accent-primary-bright: #00A6B4;
                --accent-green: #34D399;
            }

            html, body, [data-testid="stAppViewContainer"] {
                background:
                    radial-gradient(circle at 20% 10%, rgba(0, 166, 180, 0.10), transparent 28%),
                    radial-gradient(circle at 80% 30%, rgba(0, 95, 115, 0.14), transparent 32%),
                    linear-gradient(135deg, #061A24 0%, #031118 48%, #082B36 100%) !important;
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
                    linear-gradient(180deg, rgba(4, 20, 28, 0.98), rgba(3, 17, 24, 0.98)) !important;
                border-right: 1px solid rgba(217, 226, 231, 0.12);
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
                color: var(--text-main);
            }

            p {
                color: var(--text-muted);
                line-height: 1.65;
            }

            div.stButton > button {
                border-radius: 12px;
                border: 1px solid var(--border-strong);
                background: rgba(6, 26, 36, 0.72);
                color: var(--text-main);
                padding: 0.72rem 1.05rem;
                font-weight: 700;
                transition: all 0.2s ease;
            }

            div.stButton > button:hover {
                border-color: rgba(0, 166, 180, 0.65);
                background: linear-gradient(135deg, rgba(0, 95, 115, 0.92), rgba(10, 124, 140, 0.86));
                color: #ffffff;
                transform: translateY(-1px);
                box-shadow: 0 12px 28px rgba(0, 166, 180, 0.16);
            }

            [data-testid="stFileUploader"] {
                background: rgba(6, 26, 36, 0.72);
                border: 1px dashed rgba(217, 226, 231, 0.26);
                border-radius: 22px;
                padding: 1.2rem;
            }

            [data-testid="stFileUploader"] section {
                border: none !important;
                background: transparent !important;
            }

            .app-shell {
                border: 1px solid rgba(217, 226, 231, 0.12);
                border-radius: 28px;
                background:
                    radial-gradient(circle at 30% 20%, rgba(0, 166, 180, 0.08), transparent 32%),
                    radial-gradient(circle at 80% 40%, rgba(0, 95, 115, 0.12), transparent 34%),
                    rgba(3, 17, 24, 0.42);
                padding: 0;
            }

            .brand-wrap {
                display: flex;
                align-items: center;
                gap: 14px;
                margin-bottom: 2.4rem;
                padding: 0.2rem 0.1rem;
            }

            .brand-icon {
                width: 46px;
                height: 46px;
                border-radius: 14px;
                background:
                    radial-gradient(circle at 30% 20%, rgba(255,255,255,0.30), transparent 24%),
                    linear-gradient(135deg, #005F73 0%, #00A6B4 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow:
                    0 0 28px rgba(0, 166, 180, 0.30),
                    inset 0 0 12px rgba(255, 255, 255, 0.12);
                color: #ffffff;
                font-size: 0.95rem;
                font-weight: 900;
                letter-spacing: -0.04em;
            }

            .brand-title {
                font-size: 1.05rem;
                font-weight: 850;
                line-height: 1.08;
                letter-spacing: -0.035em;
                color: var(--text-main);
            }

            .brand-subtitle {
                color: var(--text-muted);
                font-size: 0.78rem;
                margin-top: 0.2rem;
            }

            .sidebar-profile-card {
                display: flex;
                align-items: center;
                gap: 14px;
                padding: 1rem;
                margin-bottom: 1.3rem;
                border-radius: 18px;
                background: rgba(6, 26, 36, 0.62);
                border: 1px solid rgba(217, 226, 231, 0.14);
            }

            .sidebar-profile-name {
                font-weight: 800;
                color: var(--text-main);
                margin-bottom: 2px;
            }

            .sidebar-profile-email {
                color: var(--text-muted);
                font-size: 0.82rem;
            }

            .sidebar-section-divider {
                height: 1px;
                background: rgba(217, 226, 231, 0.14);
                margin: 1.6rem 0;
            }

            .welcome-pill {
                display: inline-flex !important;
                align-items: center !important;
                gap: 8px !important;
                border: 1px solid rgba(217, 226, 231, 0.16) !important;
                background: rgba(8, 43, 54, 0.62) !important;
                color: #D9E2E7 !important;
                border-radius: 999px !important;
                padding: 0.52rem 0.9rem !important;
                font-size: 0.92rem !important;
                margin-bottom: 1.2rem !important;
            }

            .hero-title {
                font-size: clamp(2.35rem, 4.4vw, 4.2rem) !important;
                line-height: 1.04 !important;
                font-weight: 850 !important;
                letter-spacing: -0.065em !important;
                color: var(--text-main) !important;
                margin-bottom: 1.15rem !important;
            }

            .hero-description {
                max-width: 760px !important;
                color: var(--text-muted) !important;
                font-size: 1.13rem !important;
                line-height: 1.75 !important;
                margin-bottom: 2.2rem !important;
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
                border: 1px solid rgba(0, 166, 180, 0.42);
                background:
                    radial-gradient(circle at 50% 10%, rgba(0, 166, 180, 0.16), transparent 36%),
                    linear-gradient(135deg, rgba(8, 43, 54, 0.92), rgba(6, 26, 36, 0.58));
                box-shadow:
                    0 0 0 1px rgba(255,255,255,0.02) inset,
                    0 24px 80px rgba(0, 0, 0, 0.25);
                padding: 1.25rem;
            }

            .upload-card-inner {
                height: 100%;
                min-height: 260px;
                border: 1px dashed rgba(217, 226, 231, 0.20);
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
                    radial-gradient(circle, rgba(0, 166, 180, 0.30), rgba(0, 95, 115, 0.10));
                border: 1px solid rgba(0, 166, 180, 0.24);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2.45rem;
                margin-bottom: 1.3rem;
                color: #D9E2E7;
            }

            .upload-title {
                font-size: 1.42rem;
                font-weight: 800;
                color: var(--text-main);
                margin-bottom: 0.35rem;
            }

            .upload-subtitle {
                color: var(--text-muted);
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
                background: linear-gradient(135deg, #005F73, #00A6B4);
                color: white;
                font-weight: 800;
                box-shadow: 0 16px 38px rgba(0, 166, 180, 0.20);
                margin-bottom: 1rem;
            }

            .formats-text {
                color: var(--text-subtle);
                font-size: 0.92rem;
            }

            .history-card {
                position: relative;
                min-height: 300px;
                overflow: hidden;
                border-radius: 26px;
                border: 1px solid rgba(217, 226, 231, 0.16);
                background:
                    radial-gradient(circle at 85% 20%, rgba(0, 166, 180, 0.18), transparent 30%),
                    linear-gradient(135deg, rgba(8, 43, 54, 0.86), rgba(6, 26, 36, 0.52));
                padding: 2rem;
            }

            .history-icon {
                width: 78px;
                height: 78px;
                border-radius: 50%;
                background:
                    radial-gradient(circle, rgba(0, 166, 180, 0.30), rgba(0, 95, 115, 0.10));
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2rem;
                margin-bottom: 2rem;
            }

            .history-title {
                font-size: 1.45rem;
                font-weight: 800;
                color: var(--text-main);
                margin-bottom: 0.6rem;
            }

            .history-description {
                color: var(--text-muted);
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
                stroke: #00A6B4;
                stroke-width: 4;
                fill: none;
                filter: drop-shadow(0 0 8px rgba(0, 166, 180, 0.45));
            }

            .chart-area {
                fill: url(#purpleGradient);
                opacity: 0.45;
            }

            .privacy-card {
                margin-top: 1rem !important;
                display: flex !important;
                align-items: center !important;
                gap: 1rem !important;
                border-radius: 22px !important;
                border: 1px solid rgba(217, 226, 231, 0.13) !important;
                background: rgba(8, 43, 54, 0.55) !important;
                padding: 1.1rem 1.3rem !important;
            }

            .privacy-icon {
                width: 48px !important;
                height: 48px !important;
                border-radius: 14px !important;
                background: linear-gradient(135deg, rgba(0, 95, 115, 0.92), rgba(0, 166, 180, 0.84)) !important;
                color: #FFFFFF !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                font-size: 1.45rem !important;
                flex: 0 0 auto !important;
                box-shadow: 0 10px 28px rgba(0, 166, 180, 0.14);
            }

            .privacy-title {
                font-weight: 800 !important;
                color: var(--text-main) !important;
                margin-bottom: 0.15rem !important;
            }

            .privacy-text {
                color: var(--text-muted) !important;
            }

            .section-card {
                border-radius: 24px;
                border: 1px solid rgba(217, 226, 231, 0.14);
                background: rgba(8, 43, 54, 0.58);
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

            .custom-upload-card {
                min-height: 360px;
                border-radius: 26px;
                border: 1px solid rgba(0, 166, 180, 0.42);
                background:
                    radial-gradient(circle at 50% 12%, rgba(0, 166, 180, 0.18), transparent 35%),
                    linear-gradient(135deg, rgba(8, 43, 54, 0.92), rgba(6, 26, 36, 0.58));
                box-shadow:
                    0 0 0 1px rgba(255,255,255,0.02) inset,
                    0 24px 80px rgba(0, 0, 0, 0.25);
                padding: 1.25rem;
                margin-bottom: 1rem;
            }

            .custom-upload-inner {
                min-height: 315px;
                border: 1px dashed rgba(217, 226, 231, 0.22);
                border-radius: 22px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 0.7rem;
                text-align: center;
                padding: 2rem;
            }

            .custom-card-icon {
                width: 92px;
                height: 92px;
                border-radius: 50%;
                background:
                    radial-gradient(circle, rgba(0, 166, 180, 0.30), rgba(0, 95, 115, 0.10));
                border: 1px solid rgba(0, 166, 180, 0.26);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2.35rem;
                margin-bottom: 0.7rem;
                box-shadow: 0 0 34px rgba(0, 166, 180, 0.16);
            }

            .custom-card-title {
                font-size: 1.45rem;
                font-weight: 850;
                color: var(--text-main);
                letter-spacing: -0.035em;
            }

            .custom-card-text {
                max-width: 520px;
                color: var(--text-muted);
                line-height: 1.65;
                font-size: 1rem;
            }

            .custom-card-note {
                color: var(--text-subtle);
                font-size: 0.9rem;
                margin-top: 0.5rem;
            }

            .custom-history-card {
                position: relative;
                min-height: 360px;
                overflow: hidden;
                border-radius: 26px;
                border: 1px solid rgba(217, 226, 231, 0.18);
                background:
                    radial-gradient(circle at 85% 20%, rgba(0, 166, 180, 0.18), transparent 30%),
                    linear-gradient(135deg, rgba(8, 43, 54, 0.86), rgba(6, 26, 36, 0.52));
                padding: 2rem;
                margin-bottom: 1rem;
            }

            .custom-chart-line {
                position: absolute;
                right: 0;
                bottom: 0;
                width: 72%;
                opacity: 0.72;
                pointer-events: none;
            }

            .home-action-card {
                min-height: 310px !important;
                border-radius: 26px !important;
                border: 1px solid rgba(217, 226, 231, 0.18) !important;
                background:
                    radial-gradient(circle at 50% 10%, rgba(0, 166, 180, 0.14), transparent 35%),
                    linear-gradient(135deg, rgba(8, 43, 54, 0.90), rgba(6, 26, 36, 0.58)) !important;
                padding: 2rem !important;
                text-align: center !important;
                margin-bottom: 1rem !important;
            }

            .home-action-icon {
                width: 86px !important;
                height: 86px !important;
                border-radius: 50% !important;
                background:
                    radial-gradient(circle, rgba(0, 166, 180, 0.30), rgba(0, 95, 115, 0.10)) !important;
                border: 1px solid rgba(0, 166, 180, 0.26) !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                font-size: 2.25rem !important;
                margin: 0 auto 1.2rem auto !important;
                box-shadow: 0 0 32px rgba(0, 166, 180, 0.14);
            }

            .home-action-title {
                font-size: 1.45rem !important;
                font-weight: 850 !important;
                color: var(--text-main) !important;
                margin-bottom: 0.7rem !important;
            }

            .home-action-text {
                color: var(--text-muted) !important;
                line-height: 1.65 !important;
                margin-bottom: 0.8rem !important;
            }

            .home-action-note {
                color: var(--text-subtle) !important;
                font-size: 0.9rem !important;
            }

            .result-video-card {
                max-width: 760px;
            }

            .welcome-pill,
            .hero-title,
            .hero-description,
            .home-action-card,
            .home-action-icon,
            .home-action-title,
            .home-action-text,
            .home-action-note,
            .privacy-card,
            .privacy-icon,
            .privacy-title,
            .privacy-text,
            .brand-wrap,
            .brand-icon,
            .brand-title,
            .brand-subtitle {
                box-sizing: border-box !important;
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