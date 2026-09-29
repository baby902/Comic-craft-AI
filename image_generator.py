from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont

from .config import get_settings


def _safe_filename(panel_number: int) -> str:
    return f"panel_{panel_number}_{uuid4().hex[:8]}.png"


def _demo_image(path: Path, panel_number: int, prompt: str) -> str:
    settings = get_settings()
    image = Image.new("RGB", (settings.image_width, settings.image_height), "white")
    draw = ImageDraw.Draw(image)

    try:
        title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
        body_font = ImageFont.truetype("DejaVuSans.ttf", 20)
    except OSError:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    draw.rectangle(
        (20, 20, settings.image_width - 20, settings.image_height - 20),
        outline="black", width=5
    )
    draw.text((50, 60), f"ComicCraft — Panel {panel_number}", fill="black", font=title_font)

    cx, cy = settings.image_width // 2, settings.image_height // 2
    draw.ellipse((cx - 100, cy - 120, cx + 100, cy + 80), outline="black", width=5)
    draw.arc((cx - 60, cy - 30, cx + 60, cy + 60), 0, 180, fill="black", width=4)
    draw.line((cx - 45, cy - 45, cx - 15, cy - 65), fill="black", width=5)
    draw.line((cx + 45, cy - 45, cx + 15, cy - 65), fill="black", width=5)

    lines = [prompt[:500][i:i + 60] for i in range(0, len(prompt[:500]), 60)]
    y = settings.image_height - 170
    for line in lines[:5]:
        draw.text((50, y), line, fill="black", font=body_font)
        y += 25

    image.save(path, "PNG")
    return str(path)


def generate_image(image_prompt: str, panel_number: int) -> str:
    settings = get_settings()
    output = settings.panels_dir / _safe_filename(panel_number)

    if settings.demo_mode or not settings.hf_token:
        return _demo_image(output, panel_number, image_prompt)

    from huggingface_hub import InferenceClient

    client = InferenceClient(
        provider=settings.hf_provider,
        api_key=settings.hf_token,
    )
    image = client.text_to_image(
        prompt=image_prompt,
        model=settings.hf_image_model,
    )
    image.save(output, "PNG")
    return str(output)
