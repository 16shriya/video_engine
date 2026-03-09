# storyboard_engine.py

from models import Storyboard
from parser import safe_parse_llm_output
from llm_engine import generate_slides  # reuse your LLM wrapper


def generate_storyboard(sublesson_text: str) -> Storyboard:

    prompt = f"""
You are a visual educational storyboard generator.

Convert the following educational paragraph into a Gen-Z style animated storyboard.

RULES:
- Break into 5–7 scenes.
- Each scene must contain:
  - headline (max 8 words)
  - highlight_word (1 powerful keyword)
  - 2–3 key_points (max 6 words each)
  - icon (simple noun, single word)
  - animation (choose one: fade, slide, zoom, stagger)

Return ONLY valid JSON in this format:

{{
  "scenes": [
    {{
      "headline": "...",
      "highlight_word": "...",
      "key_points": ["...", "..."],
      "icon": "...",
      "animation": "fade"
    }}
  ]
}}

Do not wrap in markdown.
Do not explain.
Do not add extra text.

TEXT:
{sublesson_text}
"""

    raw_output = generate_slides(prompt)

    parsed = safe_parse_llm_output(raw_output, "storyboard")

    storyboard = Storyboard(**parsed)

    return storyboard
