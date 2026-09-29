# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI web application based on the supplied project documentation.

It:
1. Generates a structured 5-panel outline with Gemini Flash.
2. Expands the outline into narration/dialogue with a Gemini Pro-role model.
3. Generates one illustration per panel through Hugging Face Inference Providers.
4. Builds a panel layout.
5. Exports the comic to PDF.
6. Displays the result with Jinja2.
7. Exposes JSON API endpoints and `/docs`.

The supplied document names historical Gemini 1.5 Flash/Pro and `runwayml/stable-diffusion-v1-5`. This implementation preserves that architecture and module naming, but makes model IDs configurable in `.env` so the application can use current model endpoints.

## Structure

```text
ComicCraft/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── routes.py
│   ├── gemini_flash.py
│   ├── gemini_pro.py
│   ├── image_generator.py
│   ├── layout_builder.py
│   └── exporters.py
├── templates/
├── static/
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## VS Code setup

Use Python 3.11+.

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Windows Command Prompt

```bat
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`.

For a first test, keep:

```env
DEMO_MODE=true
```

Demo mode uses local placeholder images and sample story content, so all routes and PDF export can be tested without API keys.

For real AI generation:

```env
DEMO_MODE=false
GEMINI_API_KEY=your_google_key
HF_TOKEN=your_huggingface_token
```

Run:

```bash
uvicorn app.main:app --reload
```

Open:
- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

Run tests:

```bash
pytest -q
```

## JSON API test

```bash
curl -X POST http://127.0.0.1:8000/generate-comic/json   -H "Content-Type: application/json"   -d "{"story_prompt":"A brave fox exploring an enchanted forest","character_name":"Luna","setting":"enchanted forest","tone":"dramatic","art_style":"comic book"}"
```

Never commit `.env` or API keys.
