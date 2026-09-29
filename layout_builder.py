from pathlib import Path
from typing import List

from .models import PanelOutline, PanelStory


def build_comic_layout(outline: List[PanelOutline],
                       stories: List[PanelStory],
                       image_paths: List[str]) -> List[dict]:
    story_by_panel = {item.panel_number: item for item in stories}
    layout = []

    for index, panel in enumerate(outline):
        story = story_by_panel.get(panel.panel_number)
        if story is None:
            raise ValueError(f"Missing story for panel {panel.panel_number}.")

        image_path = image_paths[index]
        layout.append({
            "panel_number": panel.panel_number,
            "title": story.title or panel.title,
            "image_path": image_path,
            "image_url": "/static/panels/" + Path(image_path).name,
            "scene_description": story.scene_description or panel.scene_description,
            "caption": story.caption,
            "narration": story.narration,
            "dialogue": story.dialogue,
            "image_prompt": panel.image_prompt,
        })

    return layout
