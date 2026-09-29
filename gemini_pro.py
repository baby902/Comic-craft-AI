import json
import re
from typing import List

from google import genai
from google.genai import types

from .config import get_settings
from .models import PanelOutline, PanelStory


def _client():
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=settings.gemini_api_key)


def _extract_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\[[\s\S]*\]", text)
        if match:
            return json.loads(match.group(0))
        raise


def generate_story(outline: List[PanelOutline], character_name: str,
                   tone: str) -> List[PanelStory]:
    settings = get_settings()
    client = _client()

    outline_json = [item.model_dump() for item in outline]
    prompt = f"""
Expand this comic outline into a polished comic script.

Main character: {character_name}
Tone: {tone}

Outline:
{json.dumps(outline_json, ensure_ascii=False, indent=2)}

Return ONLY valid JSON: an array with one object per panel.
Each object must contain:
- panel_number
- title
- scene_description
- caption
- narration
- dialogue

Keep continuity between panels. Keep the writing suitable for a general audience.
""".strip()

    response = client.models.generate_content(
        model=settings.gemini_pro_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.85,
            max_output_tokens=6000,
            response_mime_type="application/json",
        ),
    )
    data = _extract_json(response.text or "")

    if not isinstance(data, list) or len(data) != len(outline):
        raise ValueError("Gemini returned an invalid story panel count.")

    return [PanelStory.model_validate(item) for item in data]
