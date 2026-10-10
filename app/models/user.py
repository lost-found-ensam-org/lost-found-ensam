from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    prenom = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    telephone = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    items = relationship("Item", back_populates="author", cascade="all, delete-orphan")
