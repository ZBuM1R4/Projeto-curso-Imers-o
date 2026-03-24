import collections
import contextlib
import wave
import webrtcvad


def read_wave(path):
    with contextlib.closing(wave.open(path, "rb")) as wf:
        num_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        sample_rate = wf.getframerate()
        pcm_data = wf.readframes(wf.getnframes())

        if num_channels != 1:
            raise ValueError("O áudio deve ser mono.")
        if sample_width != 2:
            raise ValueError("O áudio deve estar em PCM 16 bits.")
        if sample_rate not in (8000, 16000, 32000, 48000):
            raise ValueError("Taxa de amostragem deve ser 8000, 16000, 32000 ou 48000 Hz.")

        return pcm_data, sample_rate


def frame_generator(frame_duration_ms, audio, sample_rate):
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0

    while offset + n < len(audio):
        yield {
            "bytes": audio[offset:offset + n],
            "timestamp": timestamp,
            "duration": duration,
        }
        timestamp += duration
        offset += n


def analyze_pauses(audio_path: str, pause_threshold: float = 1.0) -> dict:
    audio, sample_rate = read_wave(audio_path)
    vad = webrtcvad.Vad(2)

    frames = list(frame_generator(30, audio, sample_rate))

    speech_segments = []
    current_segment = None

    for frame in frames:
        is_speech = vad.is_speech(frame["bytes"], sample_rate)

        if is_speech:
            if current_segment is None:
                current_segment = {
                    "start": frame["timestamp"],
                    "end": frame["timestamp"] + frame["duration"]
                }
            else:
                current_segment["end"] = frame["timestamp"] + frame["duration"]
        else:
            if current_segment is not None:
                speech_segments.append(current_segment)
                current_segment = None

    if current_segment is not None:
        speech_segments.append(current_segment)

    total_duration = frames[-1]["timestamp"] + frames[-1]["duration"] if frames else 0
    pauses = []
    total_silence = 0.0

    for i in range(1, len(speech_segments)):
        previous_end = speech_segments[i - 1]["end"]
        current_start = speech_segments[i]["start"]
        pause_duration = current_start - previous_end

        if pause_duration > 0:
            total_silence += pause_duration

        if pause_duration >= pause_threshold:
            pauses.append({
                "start": previous_end,
                "end": current_start,
                "duration": round(pause_duration, 2)
            })

    return {
        "duracao_total": round(total_duration, 2),
        "quantidade_pausas_longas": len(pauses),
        "tempo_total_silencio": round(total_silence, 2),
        "pausas_longas": pauses
    }