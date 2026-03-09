from render_engine import render_slide


def render_scene(scene, index, slide):

    # --------------------------------
    # Fix missing bullets
    # --------------------------------
    if not slide.bullets or len(slide.bullets) == 0:

        text = slide.voiceover if slide.voiceover else ""

        sentences = [
            s.strip() for s in text.replace("\n", " ").split(".") if len(s.strip()) > 15
        ]

        if sentences:
            slide.bullets = sentences[:3]
        else:
            slide.bullets = [
                f"Key concept related to {slide.title}",
                "Important principles discussed in this section",
                "Practical implications of this topic",
            ]

    # --------------------------------
    # Always render bullet layout
    # --------------------------------
    scene.layout = "bullet"

    return render_slide(
        slide,
        index,
        mode="bullet",
    )
