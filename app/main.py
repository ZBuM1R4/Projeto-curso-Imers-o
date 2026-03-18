from services.audio_extractor import extract_audio
from services.transcriber import transcribe_audio


def main():
    video_path = "data/input/teste.mp4"
    audio_path = "data/temp/audio.wav"

    extracted_audio = extract_audio(video_path, audio_path)

    if not extracted_audio:
        print("Falha na extração do áudio.")
        return

    texto = transcribe_audio(extracted_audio)

    print("\nTRANSCRIÇÃO:\n")
    print(texto)


if __name__ == "__main__":
    main()