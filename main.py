from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from typing import cast
import bcrypt

from database import engine, get_db
import models

# Initialisation des tables SQLite
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lost & Found ENSAM Rabat")

app.add_middleware(SessionMiddleware, secret_key="ensam-rabat-lost-found-secret-key-2026")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Fonctions sécurisées de hachage avec bcrypt (sans passlib pour éviter les bugs de version)
def get_password_hash(password: str) -> str:
    pwd_bytes = password.strip().encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        pwd_bytes = plain_password.strip().encode("utf-8")[:72]
        return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))
    except Exception:
        return False


@app.get("/")
def page_inscription(request: Request, db: Session = Depends(get_db)):
    # Si déjà connecté, rediriger directement vers la page principale
    user_id = request.session.get("user_id")
    if user_id:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user:
            return RedirectResponse(url="/accueil", status_code=303)
        else:
            request.session.clear()

    return templates.TemplateResponse(
        request=request,
        name="inscription.html",
        context={"active_page": "accueil", "active_view": "inscription"}
    )


@app.post("/inscription")
def creer_compte(
    request: Request,
    nom: str = Form(""),
    prenom: str = Form(""),
    email: str = Form(""),
    tel: str = Form(""),
    password: str = Form(""),
    db: Session = Depends(get_db)
):
    nom = nom.strip()
    prenom = prenom.strip()
    email = email.strip().lower()
    tel = tel.strip()

    def render_error(msg: str):
        return templates.TemplateResponse(
            request=request,
            name="inscription.html",
            context={
                "active_page": "accueil",
                "active_view": "inscription",
                "error_inscription": msg,
                "nom": nom,
                "prenom": prenom,
                "email": email,
                "tel": tel,
            }
        )

    # 1. Vérifications des champs obligatoires
    if not nom or not prenom:
        return render_error("Le nom et le prénom sont obligatoires.")

    # 2. Vérification stricte du domaine institutionnel @um5.ac.ma
    if not email.endswith("um5.ac.ma"):
        return render_error("L'adresse e-mail doit obligatoirement se terminer par @um5.ac.ma")

    # 3. Vérification du numéro de téléphone (uniquement chiffres)
    if not tel.isdigit() or len(tel) < 9:
        return render_error("Le numéro de téléphone doit comporter uniquement des chiffres (au moins 9 chiffres).")

    # 4. Vérification de la longueur du mot de passe
    if len(password) < 6:
        return render_error("Le mot de passe doit comporter au moins 6 caractères.")

    # 5. Vérification de l'unicité de l'e-mail dans la base de données
    existant_email = db.query(models.User).filter(models.User.email == email).first()
    if existant_email:
        return render_error("Cette adresse e-mail est déjà associée à un compte. Veuillez vous connecter.")

    # 6. Vérification de l'unicité du numéro de téléphone
    existant_tel = db.query(models.User).filter(models.User.telephone == tel).first()
    if existant_tel:
        return render_error("Ce numéro de téléphone est déjà associé à un compte.")

    # 6. Création et enregistrement de l'utilisateur
    hashed_pw = get_password_hash(password)
    new_user = models.User(
        nom=nom,
        prenom=prenom,
        email=email,
        telephone=tel,
        hashed_password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Connexion automatique : on enregistre l'identifiant dans la session
    request.session["user_id"] = new_user.id
    return RedirectResponse(url="/accueil", status_code=303)


@app.post("/connexion")
def se_connecter(
    request: Request,
    email: str = Form(""),
    password: str = Form(""),
    db: Session = Depends(get_db)
):
    email = email.strip().lower()
    password = password.strip()

    def render_login_error(msg: str):
        return templates.TemplateResponse(
            request=request,
            name="inscription.html",
            context={
                "active_page": "accueil",
                "active_view": "connexion",
                "error_connexion": msg,
                "login_email": email,
            }
        )

    if not email or not password:
        return render_login_error("Veuillez renseigner votre e-mail et votre mot de passe.")

    # Recherche de l'utilisateur par e-mail
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(password, cast(str, user.hashed_password)):
        return render_login_error("Adresse e-mail ou mot de passe incorrect.")

    # Connexion réussie : enregistrement en session
    request.session["user_id"] = user.id
    return RedirectResponse(url="/accueil", status_code=303)


@app.get("/deconnexion")
def se_deconnecter(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


@app.get("/accueil")
def page_accueil(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        request.session.clear()
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="accueil.html",
        context={"user": user, "active_page": "accueil"}
    )


@app.get("/perdu")
def page_perdu(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/", status_code=303)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return templates.TemplateResponse(
        request=request,
        name="perdu.html",
        context={"user": user, "active_page": "perdu"}
    )


@app.get("/trouve")
def page_trouve(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/", status_code=303)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return templates.TemplateResponse(
        request=request,
        name="trouve.html",
        context={"user": user, "active_page": "trouve"}
    )