# core/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

# Création du moteur SQLAlchemy avec l'URL de la base de données
engine = create_engine(DATABASE_URL, echo=False)

# Session locale pour interagir avec la base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base de tous les modèles
Base = declarative_base()

def init_db():
    """
    Initialise la base de données en créant toutes les tables définies dans les modèles.
    À appeler une seule fois au démarrage de l'application.
    """
    from core import models  # Import ici pour éviter les boucles circulaires
    Base.metadata.create_all(bind=engine)
