from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from .config import get_settings
from .exporters import save_pdf
from .gemini_flash import generate_outline
from .gemini_pro import generate_story
from .image_generator import generate_image
from .layout_builder import build_comic_layout
from .models import PanelOutline, PanelStory, PromptRequest

router = APIRouter()
settings = get_settings()
templates = Jinja2Templates(directory=str(settings.templates_dir))


def _demo_outline(data: PromptRequest) -> list[PanelOutline]:
    pairs = [
        ("A New Adventure", f"{data.character_name} begins an adventure in {data.setting}."),
        ("A Strange Discovery", f"{data.character_name} discovers something unexpected in {data.setting}."),
        ("The Challenge", f"{data.character_name} faces a challenge and must act bravely."),
        ("A Clever Solution", f"{data.character_name} finds a creative way to solve the problem."),
        ("A Bright Ending", f"{data.character_name} reaches a satisfying ending and looks toward the next adventure."),
    ]
    return [
        PanelOutline(
            panel_number=i,
            title=title,
            scene_description=desc,
            image_prompt=(
                f"{data.art_style} comic panel, {desc}, main character "
                f"{data.character_name}, {data.setting}, cohesive character design, "
                "expressive composition"
            ),
        )
        for i, (title, desc) in enumerate(pairs, start=1)
    ]


def _demo_story(outline: list[PanelOutline]) -> list[PanelStory]:
    return [
        PanelStory(
            panel_number=p.panel_number,
            title=p.title,
            scene_description=p.scene_description,
            caption="A new moment begins...",
            narration="The adventure moves forward as the scene changes around the hero.",
            dialogue="Let's see what happens next!",
        )
        for p in outline
    ]


def _generate(data: PromptRequest) -> dict:
    if settings.demo_mode or not settings.gemini_api_key:
        outline = _demo_outline(data)
        stories = _demo_story(outline)
    else:
        outline = generate_outline(
            data.story_prompt, data.character_name, data.setting,
            data.tone, data.art_style
        )
        stories = generate_story(outline, data.character_name, data.tone)

    image_paths = [
        generate_image(panel.image_prompt, panel.panel_number)
        for panel in outline
    ]

    layout = build_comic_layout(outline, stories, image_paths)
    title = f"{data.character_name}'s Comic"
    pdf_path = save_pdf(layout, title)

    return {
        "title": title,
        "layout": layout,
        "pdf_url": "/exports/" + Path(pdf_path).name,
        "pdf_path": pdf_path,
    }


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"request": request}
    )


@router.post("/generate", response_class=HTMLResponse)
def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        data = _generate(PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        ))
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context=data,
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"request": request, "error": str(exc)},
            status_code=500,
        )


@router.post("/generate-comic/json")
def generate_comic_json(payload: PromptRequest):
    try:
        data = _generate(payload)
        return {
            "success": True,
            "title": data["title"],
            "panels": data["layout"],
            "pdf_url": data["pdf_url"],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/test-image")
def test_image(prompt: str = "A friendly fox in an enchanted forest, comic book art"):
    try:
        path = generate_image(prompt, 0)
        return {
            "success": True,
            "image_url": "/static/panels/" + Path(path).name,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/exports/{filename}")
def export_pdf(filename: str):
    path = settings.exports_dir / filename
    if not path.exists() or path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(path, media_type="application/pdf", filename=filename)


@router.get("/export-success", response_class=HTMLResponse)
def export_success(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={"request": request},
    )
