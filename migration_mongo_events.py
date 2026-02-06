from core.database import SessionLocal
from core.models import Vehicule
from core.mongoconfig import get_mongo_db

# Dictionnaire de correspondance code région → nom lisible
REGIONS = {
    "19": "Littoral",
    "10": "Centre",
    "05": "Nord",
    # Ajoute d'autres codes si nécessaire
}

def migrer_evenements_anciens():
    db = SessionLocal()
    mongo = get_mongo_db()
    events = mongo.events

    anciens = events.find({
        "event_type": "rental_created",
        "$or": [
            {"payload.type": {"$exists": False}},
            {"payload.region_nom": {"$exists": False}}
        ]
    })

    compteur = 0
    for event in anciens:
        payload = event.get("payload", {})
        vehicule_id = payload.get("vehicule_id")
        region_code = payload.get("region")

        # Récupération du type de véhicule
        type_vehicule = None
        if vehicule_id:
            vehicule = db.query(Vehicule).filter_by(id=vehicule_id).first()
            if vehicule:
                type_vehicule = vehicule.type

        # Récupération du nom de région
        region_nom = REGIONS.get(region_code, "Inconnu")

        # Construction du dictionnaire de mise à jour
        update_fields = {}
        if type_vehicule:
            update_fields["payload.type"] = type_vehicule
        if region_nom:
            update_fields["payload.region_nom"] = region_nom

        if update_fields:
            events.update_one(
                {"_id": event["_id"]},
                {"$set": update_fields}
            )
            compteur += 1

    db.close()
    print(f"[Migration] {compteur} événement(s) mis à jour avec succès.")
