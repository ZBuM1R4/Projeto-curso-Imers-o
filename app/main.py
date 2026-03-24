from services.audio_extractor import extract_audio
from services.transcriber import transcribe_audio
from services.filler_word_analyzer import analyze_filler_words
from services.pause_analyzer import analyze_pauses
from services.repetition_analyzer import (
    analyze_sequential_repetitions,
    analyze_frequent_terms,
)
from services.report_builder import build_report


def main():
    video_path = "data/input/teste.mp4"
    audio_path = "data/temp/audio.wav"

    extracted_audio = extract_audio(video_path, audio_path)

    if not extracted_audio:
        print("Falha na extração do áudio.")
        return

    texto = transcribe_audio(extracted_audio)
    filler_words = analyze_filler_words(texto)
    pause_data = analyze_pauses(extracted_audio)
    sequential_repetitions = analyze_sequential_repetitions(texto)
    frequent_terms = analyze_frequent_terms(texto)

    report = build_report(
        transcription_text=texto,
        filler_words=filler_words,
        pause_data=pause_data,
        frequent_terms=frequent_terms,
        sequential_repetitions=sequential_repetitions,
    )

    print("\nRELATÓRIO ESTRUTURADO:\n")
    print(report)


if __name__ == "__main__":
    main()