# config.py
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

# URL de connexion à la base de données (ex: PostgreSQL, SQLite, etc.)
DATABASE_URL = os.getenv("DATABASE_URL")

# Clé secrète pour le chiffrement ou la sécurité (si besoin)
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
