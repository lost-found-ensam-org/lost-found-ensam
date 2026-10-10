import urllib.parse
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), index=True, nullable=True)
    location = Column(String(200), nullable=True)
    item_type = Column(String(50), index=True)  # 'perdu' ou 'trouve'
    image_url = Column(String(255), nullable=True)
    date_event = Column(String(100), nullable=True)
    color = Column(String(50), nullable=True)
    location_keeper = Column(String(200), nullable=True)  # où l'objet est gardé pour les objets trouvés
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    author = relationship("User", back_populates="items")

    @property
    def whatsapp_url(self) -> str:
        """Génère le lien direct WhatsApp vers le numéro de l'auteur de l'annonce"""
        if not self.author or not self.author.telephone:
            return "#"

        digits = "".join(filter(str.isdigit, self.author.telephone))
        if not digits:
            return "#"

        # Formatage marocain (indicatif +212)
        if digits.startswith("0") and len(digits) == 10:
            digits = "212" + digits[1:]
        elif not digits.startswith("212") and len(digits) == 9:
            digits = "212" + digits

        type_str = "perdu" if self.item_type == "perdu" else "trouvé"
        msg = f"Bonjour {self.author.prenom}, je vous contacte depuis la plateforme Lost & Found ENSAM Rabat concernant votre annonce : '{self.title}' (Objet {type_str})."
        
        return f"https://wa.me/{digits}?text={urllib.parse.quote(msg)}"
