import sys, os, random
from datetime import timedelta
from faker import Faker
from werkzeug.security import generate_password_hash

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import SessionLocal
from core.models import Client, Vehicule, Voiture, Moto, Location

faker = Faker("fr_FR")
db = SessionLocal()

try:
    print("🚀 Génération des données de test...")

    # 1. Générer 100 clients
    clients = []
    for _ in range(100):
        nom = faker.last_name()
        prenom = faker.first_name()
        adresse = f"{faker.street_address()}, {faker.city()}, {faker.region()}"
        email = faker.unique.email()
        mot_de_passe = generate_password_hash("test1234")

        client = Client(
            nom=nom,
            prenom=prenom,
            adresse=adresse,
            email=email,
            mot_de_passe=mot_de_passe
        )
        db.add(client)
        clients.append(client)

    db.commit()
    print("✅ 100 clients insérés")

    # 2. Générer 50 véhicules (voitures ou motos)
    vehicules = []
    for _ in range(50):
        type_vehicule = random.choice(["voiture", "moto"])
        marque = faker.company()
        modele = faker.word().capitalize()
        immatriculation = faker.unique.license_plate()
        disponibilite = True
        prix_journalier = random.randint(10000, 25000)

        if type_vehicule == "voiture":
            vehicule = Voiture(
                marque=marque,
                modele=modele,
                immatriculation=immatriculation,
                disponibilite=disponibilite,
                prix_journalier=prix_journalier,
                nb_portes=random.choice([3, 4, 5])
            )
        else:
            vehicule = Moto(
                marque=marque,
                modele=modele,
                immatriculation=immatriculation,
                disponibilite=disponibilite,
                prix_journalier=prix_journalier,
                cylindree=random.choice([125, 250, 500, 1000])
            )

        db.add(vehicule)
        vehicules.append(vehicule)

    db.commit()
    print("✅ 50 véhicules insérés (voitures et motos)")

    # 3. Générer 500 locations
    for _ in range(500):
        client = random.choice(clients)
        vehicule = random.choice(vehicules)

        date_debut = faker.date_between(start_date='-6M', end_date='-1d')
        duree = random.randint(1, 15)
        date_fin = date_debut + timedelta(days=duree)

        location = Location(
            client_id=client.id,
            vehicule_id=vehicule.id,
            date_debut=date_debut,
            date_fin=date_fin,
            statut="en cours",
            active=True
        )
        db.add(location)

    db.commit()
    print("✅ 500 locations insérées")

except Exception as e:
    db.rollback()
    print(f"❌ Erreur lors de la génération : {e}")
finally:
    db.close()