import whisper

model = whisper.load_model("small")


def transcribe_audio(audio_path: str) -> str:
    result = model.transcribe(audio_path, language="pt")
    #result = model.transcribe(audio_path)
    return result["text"]