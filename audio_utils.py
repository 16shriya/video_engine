from pydub import AudioSegment
import os

# Explicitly define ffmpeg path
AudioSegment.converter = r"C:\Program Files\ffmpeg-2026-02-18-git-52b676bb29-essentials_build\ffmpeg-2026-02-18-git-52b676bb29-essentials_build\bin\ffmpeg.exe"


def get_audio_duration(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Audio file not found: {filepath}")

    audio = AudioSegment.from_file(filepath)
    return len(audio) / 1000
