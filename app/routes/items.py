from typing import Optional
from fastapi import APIRouter, Request, Depends, Form, File, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import templates
from app.database import get_db
from app.models.user import User
from app.services.item_service import (
    create_item,
    get_recent_items,
    get_all_items,
    count_items,
    save_uploaded_photo,
    get_user_items,
    delete_user_item,
)

router = APIRouter()


def get_current_user(request: Request, db: Session) -> Optional[User]:
    """Récupère l'utilisateur actuellement connecté ou None"""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        request.session.clear()
        return None
    return user


@router.get("/accueil")
def page_accueil(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    recent_items = get_recent_items(db, limit=6)
    total_count = count_items(db)

    return templates.TemplateResponse(
        request=request,
        name="accueil.html",
        context={
            "user": user,
            "items": recent_items,
            "total_count": total_count,
            "active_page": "accueil"
        }
    )


@router.get("/perdu")
def page_perdu(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="perdu.html",
        context={"user": user, "active_page": "perdu"}
    )


@router.post("/perdu")
async def publier_perdu(
    request: Request,
    nom_objet: str = Form(""),
    categorie: str = Form(""),
    lieu: str = Form(""),
    date_perte: str = Form(""),
    couleur: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    # Validation
    if not nom_objet.strip() or not categorie.strip() or not lieu.strip() or not date_perte.strip():
        return templates.TemplateResponse(
            request=request,
            name="perdu.html",
            context={
                "user": user,
                "error": "Veuillez remplir tous les champs obligatoires (*).",
                "active_page": "perdu"
            }
        )

    # Sauvegarde photo (facultative)
    image_url = await save_uploaded_photo(photo)

    # Enregistrement dans la DB
    create_item(
        db=db,
        user_id=user.id,
        item_type="perdu",
        title=nom_objet,
        category=categorie,
        location=lieu,
        date_event=date_perte,
        description=description,
        color=couleur,
        image_url=image_url
    )

    return RedirectResponse(url="/accueil?success=perdu", status_code=303)


@router.get("/trouve")
def page_trouve(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="trouve.html",
        context={"user": user, "active_page": "trouve"}
    )


@router.post("/trouve")
async def publier_trouve(
    request: Request,
    nom_objet: str = Form(""),
    categorie: str = Form(""),
    lieu: str = Form(""),
    date_trouve: str = Form(""),
    lieu_garde: str = Form(""),
    description: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    # Validation des champs textuels obligatoires
    if not nom_objet.strip() or not categorie.strip() or not lieu.strip() or not date_trouve.strip() or not lieu_garde.strip():
        return templates.TemplateResponse(
            request=request,
            name="trouve.html",
            context={
                "user": user,
                "error": "Veuillez remplir tous les champs obligatoires (*).",
                "active_page": "trouve"
            }
        )

    # Validation STRICTE de la photo obligatoire
    if not photo or not photo.filename:
        return templates.TemplateResponse(
            request=request,
            name="trouve.html",
            context={
                "user": user,
                "error": "La photo de l'objet trouvé est obligatoire.",
                "active_page": "trouve"
            }
        )

    image_url = await save_uploaded_photo(photo)
    if not image_url:
        return templates.TemplateResponse(
            request=request,
            name="trouve.html",
            context={
                "user": user,
                "error": "Format d'image non valide (JPG, PNG, WEBP acceptés).",
                "active_page": "trouve"
            }
        )

    # Enregistrement dans la DB
    create_item(
        db=db,
        user_id=user.id,
        item_type="trouve",
        title=nom_objet,
        category=categorie,
        location=lieu,
        date_event=date_trouve,
        location_keeper=lieu_garde,
        description=description,
        image_url=image_url
    )

    return RedirectResponse(url="/accueil?success=trouve", status_code=303)


@router.get("/annonces")
def page_toutes_annonces(
    request: Request,
    type: Optional[str] = None,
    search: Optional[str] = None,
    categorie: Optional[str] = None,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    items = get_all_items(db, item_type=type, search=search, category=categorie)
    total_perdus = count_items(db, item_type="perdu")
    total_trouves = count_items(db, item_type="trouve")

    return templates.TemplateResponse(
        request=request,
        name="annonces.html",
        context={
            "user": user,
            "items": items,
            "current_type": type or "tous",
            "search_query": search or "",
            "current_category": categorie or "",
            "total_perdus": total_perdus,
            "total_trouves": total_trouves,
            "total_count": len(items),
            "active_page": "annonces"
        }
    )


@router.get("/mes-annonces")
def page_mes_annonces(
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    user_items = get_user_items(db, user_id=user.id)

    return templates.TemplateResponse(
        request=request,
        name="mes_annonces.html",
        context={
            "user": user,
            "items": user_items,
            "total_count": len(user_items),
            "active_page": "mes_annonces"
        }
    )


@router.post("/mes-annonces/{item_id}/supprimer")
def supprimer_annonce(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    delete_user_item(db, item_id=item_id, user_id=user.id)
    return RedirectResponse(url="/mes-annonces?success=deleted", status_code=303)


# ── Liste des contacts Administrateurs ENSAM ──
ADMIN_CONTACTS = [
    {
        "nom": "Bilal",
        "role": "Administrateur & Support Technique",
        "tel": "0679506233",
        "tel_format": "06 79 50 62 33",
        "whatsapp_url": "https://wa.me/212679506233?text=Bonjour%20Bilal,%20je%20vous%20contacte%20concernant%20la%20plateforme%20Lost%20%26%20Found%20ENSAM",
        "badge": "Support & Dev",
        "avatar_color": "#c0392b",
        "initiales": "B"
    },
    {
        "nom": "Adnane",
        "role": "Administrateur & Modération",
        "tel": "0603757147",
        "tel_format": "06 03 75 71 47",
        "whatsapp_url": "https://wa.me/212603757147?text=Bonjour%20Adnane,%20je%20vous%20contacte%20concernant%20la%20plateforme%20Lost%20%26%20Found%20ENSAM",
        "badge": "Modération",
        "avatar_color": "#2563eb",
        "initiales": "A"
    },
    {
        "nom": "Othmane",
        "role": "Administrateur & Assistance Étudiante",
        "tel": "0641696978",
        "tel_format": "06 41 69 69 78",
        "whatsapp_url": "https://wa.me/212641696978?text=Bonjour%20Othmane,%20je%20vous%20contacte%20concernant%20la%20plateforme%20Lost%20%26%20Found%20ENSAM",
        "badge": "Relations Étudiants",
        "avatar_color": "#059669",
        "initiales": "O"
    }
]


@router.get("/a-propos")
@router.get("/apropos")
def page_a_propos(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return templates.TemplateResponse(
        request=request,
        name="a_propos.html",
        context={
            "user": user,
            "active_page": "apropos"
        }
    )


@router.get("/contact")
def page_contact(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return templates.TemplateResponse(
        request=request,
        name="contact.html",
        context={
            "user": user,
            "admins": ADMIN_CONTACTS,
            "active_page": "contact"
        }
    )

