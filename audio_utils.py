from moviepy import AudioFileClip

def get_audio_duration(audio_path):
    try:
        audio = AudioFileClip(audio_path)
        duration = audio.duration
        audio.close()
        return duration
    except Exception:
        return 0

