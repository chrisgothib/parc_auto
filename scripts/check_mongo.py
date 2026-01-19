
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.mongoconfig import get_mongo_db


db = get_mongo_db()
print("✅ Connexion réussie à MongoDB")
print("📂 Collections disponibles :", db.list_collection_names())
