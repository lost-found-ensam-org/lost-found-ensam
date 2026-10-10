from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), index=True)
    prenom = Column(String(100), index=True)
    email = Column(String(191), unique=True, index=True)
    telephone = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))

    items = relationship("Item", back_populates="author", cascade="all, delete-orphan")
