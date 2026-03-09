import requests

AI_PIPE_ENDPOINT = "https://aipipe.org/openrouter/v1/chat/completions"
AI_PIPE_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InNocml5dThAZ21haWwuY29tIn0.t1RMJkUiQOkRT6ecbjn90qjI1T88pCdth6xfjnIHzV8"


def generate_slides(prompt):
    response = requests.post(
        AI_PIPE_ENDPOINT,
        headers={
            "Authorization": f"Bearer {AI_PIPE_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "openai/gpt-4.1-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        },
        timeout=60,
    )

    if response.status_code == 401:
        raise RuntimeError("Authentication failed. Token expired.")

    if response.status_code != 200:
        raise RuntimeError(f"API Error: {response.status_code} - {response.text}")

    data = response.json()
    return data["choices"][0]["message"]["content"]
