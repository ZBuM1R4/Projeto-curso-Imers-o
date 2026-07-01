import os

VALID_APP_MODES = {"local", "web"}
DEFAULT_APP_MODE = "local"


def get_app_mode() -> str:
    app_mode = os.getenv("APP_MODE", DEFAULT_APP_MODE).strip().lower()

    if app_mode not in VALID_APP_MODES:
        return DEFAULT_APP_MODE

    return app_mode


def is_local_mode() -> bool:
    return get_app_mode() == "local"


def is_web_mode() -> bool:
    return get_app_mode() == "web"


def get_app_mode_label() -> str:
    if is_web_mode():
        return "Versão Web - análise por áudio"

    return "Versão Local - análise por vídeo"