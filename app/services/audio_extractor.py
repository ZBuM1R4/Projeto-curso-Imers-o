import ffmpeg


def extract_audio(video_path: str, output_path: str) -> str | None:
    try:
        (
            ffmpeg
            .input(video_path)
            .output(
                output_path,
                format="wav",
                acodec="pcm_s16le",
                ac=1,
                ar="16000"
            )
            .run(overwrite_output=True)
        )
        return output_path
    except Exception as e:
        print(f"Erro ao extrair áudio: {e}")
        return None