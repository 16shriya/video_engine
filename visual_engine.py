import requests
import hashlib
import base64
import time
from pathlib import Path

# Folder for generated images
OUTPUT_DIR = Path("generated_images")
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_image_from_text(image_prompt: str):

    if not image_prompt:
        return None

    # Hash prompt so identical prompts reuse same image
    prompt_hash = hashlib.md5(image_prompt.encode()).hexdigest()
    output_path = OUTPUT_DIR / f"{prompt_hash}.jpg"

    # Reuse cached image if valid
    if output_path.exists() and output_path.stat().st_size > 5000:
        return str(output_path)

    url = "https://solitary-heart-16ff.aiml-leapot.workers.dev"

    retries = 3

    for attempt in range(retries):

        try:

            response = requests.post(url, json={"prompt": image_prompt}, timeout=120)

            if response.status_code != 200:
                print("Image API error:", response.status_code)
                time.sleep(2)
                continue

            if not response.content:
                print("Empty image response")
                time.sleep(2)
                continue

            try:
                # Cloudflare returns base64 image
                image_bytes = base64.b64decode(response.content)

                with open(output_path, "wb") as f:
                    f.write(image_bytes)

                if output_path.stat().st_size > 5000:
                    print("Saved image:", output_path)
                    return str(output_path)

            except Exception as decode_error:
                print("Base64 decode failed:", decode_error)
                return None

        except Exception as e:
            print("Image generation failed:", e)

        time.sleep(2)

    print("Image generation failed after retries")
    return None
