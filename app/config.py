import os
from pathlib import Path
from fastapi.templating import Jinja2Templates

# Dossier racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Récupération de l'URL de base de données (supporte Railway MYSQL_URL, DATABASE_URL ou SQLite local)
db_url = (
    os.environ.get("DATABASE_URL")
    or os.environ.get("MYSQL_URL")
    or os.environ.get("MYSQL_PRIVATE_URL")
    or f"sqlite:///{BASE_DIR / 'lost_found.db'}"
)

# Correction pour SQLAlchemy avec le driver pymysql
if db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)

DATABASE_URL = db_url
SECRET_KEY = os.environ.get("SECRET_KEY", "ensam-rabat-lost-found-secret-key-2026")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

