from pathlib import Path
from uuid import uuid4


TEMP_AUDIO_DIR = Path("data/temp")


def save_recorded_audio(audio_file) -> str:
    TEMP_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    if audio_file is None:
        return ""

    file_extension = "wav"

    if hasattr(audio_file, "name") and "." in audio_file.name:
        file_extension = audio_file.name.rsplit(".", 1)[-1].lower()

    audio_path = TEMP_AUDIO_DIR / f"recorded_audio_{uuid4()}.{file_extension}"

    with open(audio_path, "wb") as file:
        file.write(audio_file.getvalue())

    return str(audio_path)


def delete_temp_audio_file(audio_path: str):
    if not audio_path:
        return

    try:
        Path(audio_path).unlink(missing_ok=True)
    except OSError:
        pass