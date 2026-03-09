import requests
import re
import time

MURF_API_KEY = "ap2_c64249b8-acd1-4c2e-aec5-43de9ef12118"


def clean_latex_For_TTS(text):
    # Removes LaTeX math blocks and commands
    text = re.sub(r"\$.*?\$", "", text)
    text = re.sub(r"\\[a-zA-Z]+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def generate_local_tts(text, filename):
    text = clean_latex_For_TTS(text)
    if not text:
        print("Warning: Cleaned text is empty. Skipping TTS.")
        return None

    url = "https://api.murf.ai/v1/speech/generate"
    headers = {"api-key": MURF_API_KEY, "Content-Type": "application/json"}

    payload = {
        "voiceId": "en-US-ronnie",
        "text": text,
        "format": "MP3",  # Explicitly request MP3
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise error for 4xx or 5xx

        data = response.json()
        audio_url = data.get("encodedAudio") or data.get("audioFile")

        if not audio_url:
            print(f"Error: Murf did not return an audio URL. Response: {data}")
            return None

        # Give the server a moment to ensure the file is accessible
        audio_response = requests.get(audio_url)

        if audio_response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(audio_response.content)

            # Final Check: Ensure the file isn't 0 bytes
            import os

            if os.path.getsize(filename) > 0:
                return filename
            else:
                print(f"Error: Saved file {filename} is empty.")
                return None
        else:
            print(f"Failed to download audio from {audio_url}")
            return None

    except Exception as e:
        print(f"TTS Generation failed: {e}")
        return None
