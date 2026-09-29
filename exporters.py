from datetime import datetime
from pathlib import Path
import re

from fpdf import FPDF

from .config import get_settings


def _ascii_safe(value: str) -> str:
    return value.encode("latin-1", "replace").decode("latin-1")


def save_pdf(layout: list[dict], title: str = "ComicCraft Comic") -> str:
    settings = get_settings()
    safe_title = re.sub(r"[^a-zA-Z0-9]+", "_", title)[:30]
    filename = f"comic_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_title}.pdf"
    output = settings.exports_dir / filename

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.multi_cell(0, 10, _ascii_safe(
            f"Panel {panel['panel_number']}: {panel['title']}"
        ))

        image_path = Path(panel["image_path"])
        if image_path.exists():
            pdf.image(str(image_path), x=15, y=40, w=180, h=115)

        pdf.set_y(160)
        pdf.set_font("Helvetica", "I", 11)
        pdf.multi_cell(0, 7, _ascii_safe(panel["scene_description"]))

        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 7, _ascii_safe("Caption: " + panel["caption"]))

        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, _ascii_safe("Narration: " + panel["narration"]))

        if panel.get("dialogue"):
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 7, _ascii_safe("Dialogue: " + panel["dialogue"]))

    pdf.output(str(output))
    return str(output)
