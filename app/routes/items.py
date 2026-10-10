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

