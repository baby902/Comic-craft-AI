import json
import re
from typing import List

from google import genai
from google.genai import types

from .config import get_settings
from .models import PanelOutline


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


def generate_outline(story_prompt: str, character_name: str, setting: str,
                     tone: str, art_style: str) -> List[PanelOutline]:
    settings = get_settings()
    client = _client()

    prompt = f"""
Create a cohesive {settings.panel_count}-panel comic outline.

User story idea: {story_prompt}
Main character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Return ONLY valid JSON: an array of exactly {settings.panel_count} objects.
Each object must contain:
- panel_number: integer
- title: short panel title
- scene_description: 1-2 sentence visual scene description
- image_prompt: detailed image-generation prompt

Keep the same main character visually consistent across panels.
Do not put dialogue into image_prompt.
""".strip()

    response = client.models.generate_content(
        model=settings.gemini_flash_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.9,
            max_output_tokens=5000,
            response_mime_type="application/json",
        ),
    )
    data = _extract_json(response.text or "")

    if not isinstance(data, list) or len(data) != settings.panel_count:
        raise ValueError("Gemini returned an invalid panel count.")

    return [PanelOutline.model_validate(item) for item in data]
