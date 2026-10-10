from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import STATIC_DIR, SECRET_KEY
from app.database import engine
import app.models  # Nécessaire pour enregistrer tous les modèles SQLAlchemy
from app.database import Base
from app.routes import auth, items

# Création des tables dans la base de données SQLite
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lost & Found ENSAM Rabat")

# Middleware de session (gestion des cookies sécurisés)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Montage des fichiers statiques (css, js, images)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Enregistrement des routeurs modulaires
app.include_router(auth.router)
app.include_router(items.router)

