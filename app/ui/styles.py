import streamlit as st


def apply_global_styles():
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
                    linear-gradient(135deg, #4f7cff 0%, #7c3aed 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow:
                    0 0 28px rgba(99, 102, 241, 0.42),
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
                color: #f8fafc;
            }

            .brand-subtitle {
                color: #94a3b8;
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
            .custom-upload-card {
                min-height: 360px;
                border-radius: 26px;
                border: 1px solid rgba(99, 102, 241, 0.48);
                background:
                    radial-gradient(circle at 50% 12%, rgba(79, 124, 255, 0.20), transparent 35%),
                    linear-gradient(135deg, rgba(18, 24, 38, 0.92), rgba(18, 24, 38, 0.58));
                box-shadow:
                    0 0 0 1px rgba(255,255,255,0.02) inset,
                    0 24px 80px rgba(0, 0, 0, 0.25);
                padding: 1.25rem;
                margin-bottom: 1rem;
            }

            .custom-upload-inner {
                min-height: 315px;
                border: 1px dashed rgba(148, 163, 184, 0.22);
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
                    radial-gradient(circle, rgba(79, 124, 255, 0.34), rgba(79, 124, 255, 0.08));
                border: 1px solid rgba(99, 102, 241, 0.28);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2.35rem;
                margin-bottom: 0.7rem;
                box-shadow: 0 0 34px rgba(79, 124, 255, 0.18);
            }

            .custom-card-title {
                font-size: 1.45rem;
                font-weight: 850;
                color: #f8fafc;
                letter-spacing: -0.035em;
            }

            .custom-card-text {
                max-width: 520px;
                color: #aab4c4;
                line-height: 1.65;
                font-size: 1rem;
            }

            .custom-card-note {
                color: #7d8798;
                font-size: 0.9rem;
                margin-top: 0.5rem;
            }

            .custom-history-card {
                position: relative;
                min-height: 360px;
                overflow: hidden;
                border-radius: 26px;
                border: 1px solid rgba(148, 163, 184, 0.18);
                background:
                    radial-gradient(circle at 85% 20%, rgba(124, 58, 237, 0.24), transparent 30%),
                    linear-gradient(135deg, rgba(18, 24, 38, 0.86), rgba(18, 24, 38, 0.52));
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
                min-height: 310px;
                border-radius: 26px;
                border: 1px solid rgba(148, 163, 184, 0.18);
                background:
                    radial-gradient(circle at 50% 10%, rgba(79, 124, 255, 0.16), transparent 35%),
                    linear-gradient(135deg, rgba(18, 24, 38, 0.90), rgba(18, 24, 38, 0.58));
                padding: 2rem;
                text-align: center;
                margin-bottom: 1rem;
            }

            .home-action-icon {
                width: 86px;
                height: 86px;
                border-radius: 50%;
                background:
                    radial-gradient(circle, rgba(79, 124, 255, 0.34), rgba(79, 124, 255, 0.08));
                border: 1px solid rgba(99, 102, 241, 0.28);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2.25rem;
                margin: 0 auto 1.2rem auto;
            }

            .home-action-title {
                font-size: 1.45rem;
                font-weight: 850;
                color: #f8fafc;
                margin-bottom: 0.7rem;
            }

            .home-action-text {
                color: #aab4c4;
                line-height: 1.65;
                margin-bottom: 0.8rem;
            }

            .home-action-note {
                color: #7d8798;
                font-size: 0.9rem;
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

            .welcome-pill {
                display: inline-flex !important;
                align-items: center !important;
                gap: 8px !important;
                border: 1px solid rgba(148, 163, 184, 0.16) !important;
                background: rgba(15, 23, 42, 0.62) !important;
                color: #bcd0ff !important;
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
                color: #f8fafc !important;
                margin-bottom: 1.15rem !important;
            }

            .hero-description {
                max-width: 760px !important;
                color: #aab4c4 !important;
                font-size: 1.13rem !important;
                line-height: 1.75 !important;
                margin-bottom: 2.2rem !important;
            }

            .home-action-card {
                min-height: 310px !important;
                border-radius: 26px !important;
                border: 1px solid rgba(148, 163, 184, 0.18) !important;
                background:
                    radial-gradient(circle at 50% 10%, rgba(79, 124, 255, 0.16), transparent 35%),
                    linear-gradient(135deg, rgba(18, 24, 38, 0.90), rgba(18, 24, 38, 0.58)) !important;
                padding: 2rem !important;
                text-align: center !important;
                margin-bottom: 1rem !important;
            }

            .home-action-icon {
                width: 86px !important;
                height: 86px !important;
                border-radius: 50% !important;
                background:
                    radial-gradient(circle, rgba(79, 124, 255, 0.34), rgba(79, 124, 255, 0.08)) !important;
                border: 1px solid rgba(99, 102, 241, 0.28) !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                font-size: 2.25rem !important;
                margin: 0 auto 1.2rem auto !important;
            }

            .home-action-title {
                font-size: 1.45rem !important;
                font-weight: 850 !important;
                color: #f8fafc !important;
                margin-bottom: 0.7rem !important;
            }

            .home-action-text {
                color: #aab4c4 !important;
                line-height: 1.65 !important;
                margin-bottom: 0.8rem !important;
            }

            .home-action-note {
                color: #7d8798 !important;
                font-size: 0.9rem !important;
            }

            .privacy-card {
                margin-top: 1rem !important;
                display: flex !important;
                align-items: center !important;
                gap: 1rem !important;
                border-radius: 22px !important;
                border: 1px solid rgba(148, 163, 184, 0.13) !important;
                background: rgba(15, 23, 42, 0.55) !important;
                padding: 1.1rem 1.3rem !important;
            }

            .privacy-icon {
                width: 48px !important;
                height: 48px !important;
                border-radius: 14px !important;
                background: rgba(79, 124, 255, 0.12) !important;
                color: #8ca8ff !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                font-size: 1.45rem !important;
                flex: 0 0 auto !important;
            }

            .privacy-title {
                font-weight: 800 !important;
                color: #f8fafc !important;
                margin-bottom: 0.15rem !important;
            }

            .privacy-text {
                color: #aab4c4 !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )