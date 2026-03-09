from pathlib import Path
from playwright.sync_api import sync_playwright
from jinja2 import Environment, FileSystemLoader

TEMPLATE_FOLDER = "render/templates"
OUTPUT_DIR = Path("generated_slides")
OUTPUT_DIR.mkdir(exist_ok=True)

env = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER))


def generate_bullet_html(bullets):

    if not bullets:
        bullets = ["Key idea"]

    bullet_html = ""

    for bullet in bullets:
        bullet_html += f"<li>{bullet}</li>"

    return bullet_html


def detect_layout(slide):

    keywords = [
        "advantages",
        "disadvantages",
        "limitations",
        "applications",
        "challenges",
        "steps",
        "methods",
        "process",
        "types",
    ]

    title_lower = slide.title.lower()

    if any(word in title_lower for word in keywords):
        return "mindmap"

    return "standard"


def render_slide(slide, index: int):

    layout = detect_layout(slide)
    frame_path = Path("leapot_bg.png").resolve()
    frame_uri = frame_path.as_uri()

    # -------------------------
    # TEMPLATE SELECTION
    # -------------------------

    if layout == "mindmap":
        template = env.get_template("Mindmaps.html")
    else:
        template = env.get_template("main.html")

    # -------------------------
    # IMAGE HANDLING
    # -------------------------

    image_path = getattr(slide, "image_path", None)

    if not image_path or not Path(image_path).exists():
        raise RuntimeError(f"No generated image found for slide {index}")

    image_uri = Path(image_path).resolve().as_uri()

    # -------------------------
    # BULLETS
    # -------------------------

    bullet_html = generate_bullet_html(slide.bullets)

    html_content = template.render(
        title=slide.title,
        bullets=bullet_html,
        image_uri=image_uri,
        frame_uri=frame_uri,
    )

    # -------------------------
    # SAVE TEMP HTML
    # -------------------------

    temp_html_path = OUTPUT_DIR / f"temp_slide_{index}.html"
    output_image_path = OUTPUT_DIR / f"slide_{index}.png"

    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # -------------------------
    # SCREENSHOT WITH PLAYWRIGHT
    # -------------------------

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page(viewport={"width": 960, "height": 540})

        page.goto(temp_html_path.resolve().as_uri())
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(700)

        page.screenshot(path=str(output_image_path))

        browser.close()

    temp_html_path.unlink()

    return str(output_image_path)
