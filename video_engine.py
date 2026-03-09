from moviepy import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
)
from pathlib import Path
from render_engine import render_slide

OUTPUT_DIR = Path("generated_videos")
OUTPUT_DIR.mkdir(exist_ok=True)


def create_video_from_scenes(slides, audio_path):

    audio_clip = AudioFileClip(audio_path)

    clips = []

    for idx, slide in enumerate(slides, 1):

        # fallback duration protection
        duration = getattr(slide, "audio_duration", None)

        if not duration or duration <= 0:
            print(f"Slide {idx} missing duration, using fallback 5s")
            duration = 5

        # render slide frame
        image_path = render_slide(slide, idx)

        if not image_path:
            print(f"Slide {idx} render failed, skipping")
            continue

        base_clip = ImageClip(image_path).with_duration(duration)

        scene_clip = CompositeVideoClip(
            [base_clip],
            size=(960, 540),
        ).with_duration(duration)

        clips.append(scene_clip)

    if not clips:
        raise ValueError("No video clips were generated.")

    final_clip = concatenate_videoclips(clips, method="compose")

    final_clip = final_clip.with_audio(audio_clip)

    output_path = OUTPUT_DIR / "lesson_video.mp4"

    final_clip.write_videofile(
        str(output_path),
        fps=12,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=4,
    )

    return str(output_path)
