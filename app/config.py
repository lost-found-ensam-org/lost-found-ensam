from pathlib import Path
from fastapi.templating import Jinja2Templates

# Dossier racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

DATABASE_URL = "sqlite:///./lost_found.db"
SECRET_KEY = "ensam-rabat-lost-found-secret-key-2026"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

