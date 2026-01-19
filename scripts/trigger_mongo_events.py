import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import SessionLocal
from core.models import Location
from etl.insert_event import log_rental_created  # ✅ Assure-toi que le chemin est correct

def main():
    db = SessionLocal()
    try:
        print("🚀 Déclenchement des événements MongoDB pour les locations...")

        locations = db.query(Location).all()
        total = len(locations)
        print(f"🔎 {total} locations trouvées")

        for i, loc in enumerate(locations, start=1):
            print(f"➡️  [{i}/{total}] Insertion de la location ID {loc.id}...")
            log_rental_created(loc.id)

        print("✅ Tous les événements ont été insérés dans MongoDB")

    except Exception as e:
        print(f"❌ Erreur lors du déclenchement : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()