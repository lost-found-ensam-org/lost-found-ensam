import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.config import STATIC_DIR
from app.models.item import Item

UPLOADS_DIR = STATIC_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


async def save_uploaded_photo(photo: Optional[UploadFile]) -> Optional[str]:
    """Sauvegarde le fichier photo uploadé et retourne son URL relative"""
    if not photo or not photo.filename:
        return None

    # Extraction de l'extension
    suffix = Path(photo.filename).suffix.lower()
    if suffix not in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
        return None

    unique_filename = f"{uuid.uuid4().hex}{suffix}"
    destination = UPLOADS_DIR / unique_filename

    contents = await photo.read()
    if not contents:
        return None

    with open(destination, "wb") as f:
        f.write(contents)

    return f"/static/uploads/{unique_filename}"


def create_item(
    db: Session,
    user_id: int,
    item_type: str,
    title: str,
    category: str,
    location: str,
    date_event: str,
    description: Optional[str] = None,
    color: Optional[str] = None,
    location_keeper: Optional[str] = None,
    image_url: Optional[str] = None
) -> Item:
    """Crée et enregistre un objet perdu ou trouvé dans la base de données"""
    new_item = Item(
        user_id=user_id,
        item_type=item_type,
        title=title.strip(),
        category=category.strip() if category else None,
        location=location.strip() if location else None,
        date_event=date_event.strip() if date_event else None,
        description=description.strip() if description else None,
        color=color.strip() if color else None,
        location_keeper=location_keeper.strip() if location_keeper else None,
        image_url=image_url
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


def get_recent_items(db: Session, limit: int = 6):
    """Récupère les objets récents (les plus récents en premier)"""
    return db.query(Item).order_by(Item.created_at.desc(), Item.id.desc()).limit(limit).all()


def count_items(db: Session, item_type: Optional[str] = None) -> int:
    """Compte le nombre total d'objets"""
    query = db.query(Item)
    if item_type:
        query = query.filter(Item.item_type == item_type)
    return query.count()


def get_all_items(
    db: Session,
    item_type: Optional[str] = None,
    search: Optional[str] = None,
    category: Optional[str] = None
):
    """Récupère tous les objets avec filtres optionnels"""
    query = db.query(Item)
    if item_type and item_type in ["perdu", "trouve"]:
        query = query.filter(Item.item_type == item_type)
    if category:
        query = query.filter(Item.category == category)
    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Item.title.ilike(search_term),
                Item.description.ilike(search_term),
                Item.location.ilike(search_term)
            )
        )
    return query.order_by(Item.created_at.desc(), Item.id.desc()).all()


def get_user_items(db: Session, user_id: int):
    """Récupère les objets publiés par l'utilisateur connecté"""
    return db.query(Item).filter(Item.user_id == user_id).order_by(Item.created_at.desc(), Item.id.desc()).all()


def delete_user_item(db: Session, item_id: int, user_id: int) -> bool:
    """Supprime une annonce appartenant à l'utilisateur (ex: objet retrouvé/restitué)"""
    item = db.query(Item).filter(Item.id == item_id, Item.user_id == user_id).first()
    if item:
        db.delete(item)
        db.commit()
        return True
    return False

