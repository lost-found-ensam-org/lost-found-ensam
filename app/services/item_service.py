from sqlalchemy.orm import Session
from app.models.item import Item

def get_recent_items(db: Session, limit: int = 10):
    """Récupère les objets récemment signalés"""
    return db.query(Item).order_by(Item.created_at.desc()).limit(limit).all()

