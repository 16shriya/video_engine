import json
import re


def extract_points_block(text):
    match = re.search(r"Points:\s*\[(.*?)\]", text, re.DOTALL)
    if not match:
        return None

    content = match.group(1)
    bullets = re.findall(r'"(.*?)"', content)

    return bullets


def safe_parse_llm_output(raw_text, topic):

    raw_text = raw_text.strip()

    # Remove markdown if present
    raw_text = re.sub(r"```json", "", raw_text)
    raw_text = re.sub(r"```", "", raw_text)

    # Extract first JSON object
    json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)

    if not json_match:
        raise ValueError("No JSON object found in LLM output.")

    json_text = json_match.group(0)

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        print("Invalid JSON detected:")
        print(json_text)
        raise ValueError("LLM returned malformed JSON.")
