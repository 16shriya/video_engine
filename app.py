import sys
import asyncio
from moviepy import AudioFileClip, concatenate_audioclips
from pathlib import Path

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import streamlit as st
import os
from visual_engine import generate_image_from_text
from models import Lesson
from llm_engine import generate_slides
from parser import safe_parse_llm_output, extract_points_block
from tts_engine import clean_latex_For_TTS, generate_local_tts
from audio_utils import get_audio_duration

# from video_engine import create_final_video
# from scene_renderer import render_scene
from video_engine import create_video_from_scenes


# -------------------------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------

duration_map = {
    "3 minutes": {"slides": 6, "words": 450},
    "4 minutes": {"slides": 8, "words": 600},
    "5 minutes": {"slides": 10, "words": 750},
}

PROJECT_DIR = "generated_audio"

if not os.path.exists(PROJECT_DIR):
    os.makedirs(PROJECT_DIR)


# -----------------------------
# UI HEADER
# -----------------------------
st.logo("Blue logo.png", link="https://leapot.in/")
st.title("Welcome Learners! ")
st.subheader("Personalized learning just for u.....")


# -----------------------------
# INPUT SECTION
# -----------------------------

predefined_topics = [
    "Select Topic",
    "Bayes Theorem",
    "Linear Regression",
    "Python Basics",
    "Neural Networks Introduction",
    "Data Structures Overview",
]

topic_choice = st.selectbox("Select Topic", predefined_topics)
custom_topic = st.text_input("Or Enter Topic u want to study", key="custom_topic_input")
# final_topic = custom_topic if custom_topic else topic_choice

difficulty = st.selectbox(
    "Select Difficulty Level", ["Beginner", "Intermediate", "Advanced"]
)

duration = st.selectbox("Target Duration", ["3 minutes", "4 minutes", "5 minutes"])

tone = st.selectbox("Tone of Explanation", ["Academic", "Conversational", "Concise"])

selected_config = duration_map[duration]
max_slides = selected_config["slides"]
target_words = selected_config["words"]


# -----------------------------
# GENERATE SLIDES BUTTON
# -----------------------------
if st.button("Generate Slides"):

    # Decide final topic
    if custom_topic.strip():
        final_topic = custom_topic.strip()
    elif topic_choice != "Select Topic":
        final_topic = topic_choice
    else:
        st.warning("Please select or enter a topic.")
        st.stop()

    with st.spinner("Generating slides..."):

        prompt = f"""
You are an expert educational content generator.

Generate a structured slide lesson in valid JSON.

Topic: {final_topic}
Difficulty: {difficulty}
Target Duration: {duration}
Tone: {tone}

Content Rules:

• Generate exactly {max_slides} slides.
• Total voiceover length ≈ {target_words} words.
• Distribute narration evenly across slides.
• Slides must progress logically from basic → deeper understanding.

Each slide must include:

slide_number (integer starting from 1)
title (short)
bullets (max 5 bullet points, each under 8 words)
voiceover (clear explanation)
image_prompt:
Minimal flat vector illustration of {{CONCEPT}} in the slide.

modern educational diagram,
flat vector shapes,
soft pastel color palette,
clean white background,
subtle gradients,
minimalist design.

single clear conceptual visualization using simple icons and arrows,
balanced composition,
presentation slide friendly.

no text, no labels, no letters, no numbers, no typography, no watermark.


high quality educational graphic
Bullet Rules:
• Max 5 bullets
• Each bullet ≤ 8 words
• Bullets should be concise key ideas


Voiceover Rules:
• Explain the concept clearly
• Conversational but educational tone
• Avoid repeating bullet text exactly

Important rule:
Return ONLY a short visual prompt describing the scene in **≤20 words**.

Use LaTeX ($...$) for formulas when needed.

Return ONLY valid JSON in this format:

{{
  "title": "Lesson Title",
  "slides": [
    {{
      "slide_number": 1,
      "title": "Slide Title",
      "bullets": ["point1", "point2"],
      "voiceover": "Explanation text",
      "image_prompt": "clean conceptual diagram showing probability update arrows minimal pastel illustration no text",
      "visual_theme": {{
        "background_query": "abstract neural network gradient",
        "text_mode": "light_box"
      }}
    }}
  ]
}}

Do NOT wrap JSON in markdown.
Do NOT add explanations. """
        # aspect ratio 16:9
        try:
            raw_output = generate_slides(prompt)
            parsed = safe_parse_llm_output(raw_output, final_topic)
            lesson = Lesson(**parsed)

            st.session_state["lesson"] = lesson
            st.success("Slides Generated Successfully")

        except Exception as e:
            st.error("Generation Failed")
            st.write(str(e))


# ============================================================
# STEP 2 — DISPLAY & EDIT SLIDES
# ============================================================

if "lesson" in st.session_state:

    lesson = st.session_state["lesson"]
    st.header(lesson.title)

    total_words = 0

    for slide in lesson.slides:

        with st.expander(f"Slide {slide.slide_number}: {slide.title}", expanded=True):

            # Title
            slide.title = st.text_input(
                "Slide Title", slide.title, key=f"title_{slide.slide_number}"
            )

            # Bullets
            for i, bullet in enumerate(slide.bullets):
                slide.bullets[i] = st.text_input(
                    f"Bullet {i+1}", bullet, key=f"bullet_{slide.slide_number}_{i}"
                )

            # Voiceover
            slide.voiceover = st.text_area(
                "Voiceover",
                slide.voiceover,
                height=120,
                key=f"voice_{slide.slide_number}",
            )

            total_words += len(slide.voiceover.split())

    # -----------------------------
    # Duration + Validation Summary
    # -----------------------------

    st.divider()

    estimated_minutes = total_words / 150

    col1, col2 = st.columns(2)

    col1.metric("Total Words", total_words)
    col2.metric("Estimated Duration (min)", round(estimated_minutes, 2))

    if abs(total_words - target_words) > 100:
        st.warning("Voiceover length deviates significantly from target duration.")

    if len(lesson.slides) != max_slides:
        st.warning("Slide count does not match selected duration configuration.")

    # -----------------------------
    # GENERATE AUDIO BUTTON
    # -----------------------------

    if st.button("Generate Audio"):

        audio_data = []
        total_audio_duration = 0

        for slide in lesson.slides:

            filename = os.path.join(PROJECT_DIR, f"slide_{slide.slide_number}.mp3")

            clean_text = clean_latex_For_TTS(slide.voiceover)
            generate_local_tts(clean_text, filename)

            duration_seconds = get_audio_duration(filename)
            slide.audio_path = filename
            slide.audio_duration = duration_seconds
            audio_data.append(
                {
                    "slide_number": slide.slide_number,
                    "path": filename,
                    "duration": duration_seconds,
                }
            )

            total_audio_duration += duration_seconds

        st.session_state["audio_data"] = audio_data
        st.session_state["total_audio_duration"] = total_audio_duration

        st.success("Audio generated successfully.")

# -----------------------------
# AUDIO PREVIEW
# -----------------------------
# -----------------------------
# AUDIO PREVIEW + FINAL AUDIO MERGE
# -----------------------------

if "audio_data" in st.session_state:

    st.subheader("Audio Preview")

    audio_data = st.session_state["audio_data"]
    total_audio_duration = st.session_state["total_audio_duration"]

    for item in audio_data:
        st.write(
            f"Slide {item['slide_number']} Duration: {round(item['duration'], 2)} sec"
        )
        st.audio(item["path"])

    st.info(f"Total Audio Duration: {round(total_audio_duration/60, 2)} minutes")

    #  MERGE AUDIO 1
    audio_clips = [AudioFileClip(item["path"]) for item in audio_data]

    final_audio = concatenate_audioclips(audio_clips)

    Path("generated_audio").mkdir(exist_ok=True)

    final_audio_path = "generated_audio/final_audio.mp3"
    final_audio.write_audiofile(final_audio_path)

    st.session_state["final_audio_path"] = final_audio_path
    # -----------------------------
    # VIDEO GENERATION
    # -----------------------------

    # if "lesson" in st.session_state and "audio_data" in st.session_state:

    #     if st.button("Generate Slide-Based Video"):

    #         lesson = st.session_state["lesson"]
    #         slides = lesson.slides

    #         with st.spinner("Assembling slide video..."):
    #             video_path = create_final_video(slides)

    #         st.success("Slide video generated successfully!")
    #         st.video(video_path)

    # ============================================================
    # STEP 4 — GENERATE IMAGES
    # ============================================================

    if "lesson" in st.session_state and "final_audio_path" in st.session_state:

        if st.button("Generate Images for Slides"):

            lesson = st.session_state["lesson"]

            generated = 0

            with st.spinner("Generating slide images..."):

                for slide in lesson.slides:

                    print("IMAGE PROMPT:", slide.image_prompt)

                    image_path = generate_image_from_text(slide.image_prompt)

                    print("IMAGE PATH:", image_path)

                    if image_path:
                        slide.image_path = image_path
                        generated += 1

            if generated == 0:
                st.error("Image generation failed for all slides")
            else:
                st.success(f"{generated} slide images generated successfully")

    # ============================================================
    # STEP 5 — RENDER VIDEO
    # ============================================================

    if "lesson" in st.session_state and "final_audio_path" in st.session_state:

        if st.button("Render Animated Video"):

            lesson = st.session_state["lesson"]

            # ----------------------------- Ensure images exist before rendering
            for slide in lesson.slides:

                if not getattr(slide, "image_path", None):

                    image_path = generate_image_from_text(slide.image_prompt)

                    slide.image_path = image_path

            with st.spinner("Rendering animated video..."):

                video_path = create_video_from_scenes(
                    lesson.slides,
                    st.session_state["final_audio_path"],
                )

            st.success("Animated video generated successfully!")
            st.video(video_path)

# st.success("Animated video generated successfully!")
# st.video(video_path)
# -----------------------------
# CLEAR BUTTON
# -----------------------------

if st.button("Clear Slides"):
    st.session_state.pop("lesson", None)
    st.session_state.pop("audio_data", None)
    st.session_state.pop("total_audio_duration", None)
    st.session_state.pop("final_audio_path", None)
    st.session_state.pop("storyboard", None)
    st.success("Slides cleared.")
