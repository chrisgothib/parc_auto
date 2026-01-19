# scripts/clean_test_data.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import SessionLocal
from core.models import Location, Voiture, Moto, Vehicule, Client

db = SessionLocal()

try:
    print("🧹 Suppression des données de test...")

    db.query(Location).delete()
    db.query(Voiture).delete()
    db.query(Moto).delete()
    db.query(Vehicule).delete()
    db.query(Client).delete()

    db.commit()
    print("✅ Données supprimées avec succès")
except Exception as e:
    db.rollback()
    print(f"❌ Erreur lors du nettoyage : {e}")
finally:
    db.close()
