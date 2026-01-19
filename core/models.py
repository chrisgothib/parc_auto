# core/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
from .database import Base
from core.utils import utc_now

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    adresse = Column(String)
    email = Column(String, unique=True, nullable=False)
    mot_de_passe = Column(String, nullable=False)  # ✅ Nouveau champ ajouté
    
    created_at = Column(DateTime, default=utc_now)
    
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)


    locations = relationship("Location", back_populates="client")

class Vehicule(Base):
    __tablename__ = "vehicules"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)  # "Voiture" ou "Moto"
    marque = Column(String, nullable=False)
    modele = Column(String, nullable=False)
    immatriculation = Column(String, unique=True, nullable=False)
    disponibilite = Column(Boolean, default=True)
    prix_journalier = Column(Integer, nullable=False)
    
    created_at = Column(DateTime, default=utc_now)
    
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

        



        # (Optionnel) 🧼 Ajoute __repr__ pour le debug
        # Cela t’aidera à afficher les objets plus lisiblement dans les logs
    def __repr__(self):
        return f"<Vehicule {self.marque} {self.modele} ({self.immatriculation})>"
    
     # ✅ Ajoute cette ligne si elle manque
    locations = relationship("Location", back_populates="vehicule")

    __mapper_args__ = {
    "polymorphic_on": type,
    "polymorphic_identity": "vehicule",
    "with_polymorphic": "*"
}


class Voiture(Vehicule):
        __tablename__ = "voitures"
        id = Column(Integer, ForeignKey("vehicules.id"), primary_key=True)
        nb_portes = Column(Integer)

        __mapper_args__ = {
        'polymorphic_identity': 'voiture',
        }

class Moto(Vehicule):
    __tablename__ = "motos"
    id = Column(Integer, ForeignKey("vehicules.id"), primary_key=True)
    cylindree = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'moto',
    }
    

class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    vehicule_id = Column(Integer, ForeignKey("vehicules.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    date_debut = Column(Date)
    date_fin = Column(Date)

    active = Column(Boolean, default=True)
    statut=Column(String, default="en cours")

    created_at = Column(DateTime, default=utc_now)
    
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    


    client = relationship("Client", back_populates="locations")
    vehicule = relationship("Vehicule", back_populates="locations")

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    created_at = Column(DateTime, default=utc_now)
    
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    


    def __repr__(self):
        return f"<Admin {self.username}>"


    def __init__(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(password)


    