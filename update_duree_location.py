# update_duree_locations.py
from datetime import datetime
from sqlalchemy.orm import Session
from core.database import SessionLocal
from core.models import Location

def update_durees():
    db: Session = SessionLocal()
    try:
        locations = db.query(Location).all()
        for loc in locations:
            if loc.date_debut and loc.date_fin:
                loc.duree = (loc.date_fin - loc.date_debut).days
        db.commit()
        print("✅ Mise à jour des durées terminée.")
    except Exception as e:
        db.rollback()
        print("❌ Erreur :", e)
    finally:
        db.close()

if __name__ == "__main__":
    update_durees()
