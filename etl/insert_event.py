from core.database import SessionLocal
from core.models import Location, Client,Vehicule
from core.mongoconfig import get_mongo_db
from core.utils import utc_now, extraire_region_ville
from core.mongo_aggregations import aggregate_kpis  # ✅ importer en haut

from core.database import SessionLocal
from core.models import Location, Client
from core.mongoconfig import get_mongo_db
from core.utils import utc_now, extraire_region_ville
from core.mongo_aggregations import aggregate_kpis

def log_rental_created(location_id):
    db = SessionLocal()
    mongo = get_mongo_db()

    location = db.query(Location).filter_by(id=location_id).first()
    if not location:
        db.close()
        return

    # ✅ Empêcher les doublons
    existe = mongo.events.find_one({
        "event_type": "rental_created",
        "payload.location_id": location.id
    })
    if existe:
        print(f"[BI] Événement déjà existant pour location ID {location.id}, insertion ignorée.")
        db.close()
        return

    client = db.query(Client).filter_by(id=location.client_id).first()
    vehicule = location.vehicule

    adresse = client.adresse or ""
    region, ville = extraire_region_ville(adresse)

    duree = (location.date_fin - location.date_debut).days if location.date_debut and location.date_fin else 0
    prix_total = (duree * vehicule.prix_journalier) if (vehicule and duree > 0) else None

    # ✅ Ne pas insérer si prix_total invalide
    if prix_total is None:
        print(f"[BI] Location {location.id} ignorée : prix_total manquant.")
        db.close()
        return

    event = {
        "event_type": "rental_created",
        "timestamp": utc_now(),
        "source": "app_client",
        "payload": {
            "location_id": location.id,
            "client_id": location.client_id,
            "vehicule_id": location.vehicule_id,
            "date_debut": location.date_debut.isoformat() if location.date_debut else None,
            "date_fin": location.date_fin.isoformat() if location.date_fin else None,
            "prix_total": prix_total,
            "region": region,
            "ville": ville,
            "type": vehicule.type if vehicule else None  # ✅ Ajout du type de véhicule
        },
        "processed": False
    }

    try:
        mongo.events.insert_one(event)
        print(f"[BI] Événement rental_created inséré avec succès pour location ID {location.id}")
    except Exception as e:
        print(f"[BI] Erreur MongoDB pour location ID {location.id} : {e}")

    # ✅ Mise à jour automatique des KPIs
    aggregate_kpis()
    db.close()

    