from core.mongoconfig import get_mongo_db
from datetime import datetime

def aggregate_kpis():
    mongo = get_mongo_db()
    events = mongo.events
    kpis = mongo.kpi_dashboard

    # Filtrer uniquement les événements validés et avec prix_total numérique
    pipeline_global = [
        {"$match": {"event_type": "rental_created", "payload.prix_total": {"$type": "number"}}},
        {"$group": {
            "_id": None,
            "chiffre_affaires": {"$sum": "$payload.prix_total"},
            "nb_locations": {"$sum": 1},
            "duree_totale_jours": {
                "$sum": {
                    "$divide": [
                        {"$subtract": [
                            {"$toDate": "$payload.date_fin"},
                            {"$toDate": "$payload.date_debut"}
                        ]},
                        1000 * 60 * 60 * 24
                    ]
                }
            }
        }},
        {"$addFields": {
            "duree_moyenne_jours": {
                "$cond": [
                    {"$gt": ["$nb_locations", 0]},
                    {"$round": [{"$divide": ["$duree_totale_jours", "$nb_locations"]}, 2]},
                    0
                ]
            }
        }}
    ]

    # CA par mois (YYYY-MM)
    pipeline_ca_mois = [
        {"$match": {"event_type": "rental_created", "payload.prix_total": {"$type": "number"}}},
        {"$addFields": {
            "mois": {"$substr": ["$payload.date_debut", 0, 7]}  # ex: "2025-12"
        }},
        {"$group": {
            "_id": "$mois",
            "ca_mois": {"$sum": "$payload.prix_total"},
            "locations_mois": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]

    # CA par région
    pipeline_ca_region = [
        {"$match": {"event_type": "rental_created", "payload.prix_total": {"$type": "number"}}},
        {"$group": {
            "_id": {"region": "$payload.region"},
            "ca_region": {"$sum": "$payload.prix_total"},
            "locations_region": {"$sum": 1}
        }},
        {"$sort": {"ca_region": -1}}
    ]

    global_res = list(events.aggregate(pipeline_global))
    mois_res = list(events.aggregate(pipeline_ca_mois))
    region_res = list(events.aggregate(pipeline_ca_region))

    doc = {
        "updated_at": datetime.utcnow(),
        "global": global_res[0] if global_res else {
            "chiffre_affaires": 0,
            "nb_locations": 0,
            "duree_totale_jours": 0,
            "duree_moyenne_jours": 0
        },
        "par_mois": mois_res,
        "par_region": region_res
    }

    # Upsert unique (document unique pour le dashboard)
    kpis.replace_one({}, doc, upsert=True)