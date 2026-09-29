import os

os.environ["DEMO_MODE"] = "true"

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert "ComicCraft" in response.text


def test_json_generation():
    payload = {
        "story_prompt": "A brave fox exploring an enchanted forest",
        "character_name": "Luna",
        "setting": "enchanted forest",
        "tone": "dramatic",
        "art_style": "comic book",
    }
    response = client.post("/generate-comic/json", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["panels"]) == 5
    assert data["pdf_url"].endswith(".pdf")
