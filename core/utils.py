from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)


def extraire_region_ville(adresse: str) -> tuple[str, str]:
    """
    Extrait la région et la ville à partir d'une adresse au format "Région, Ville".
    Si l'information est manquante, retourne "NaN".
    """
    if not adresse:
        return "NaN", "NaN"

    parts = adresse.split(",")
    region = parts[0].strip() if len(parts) > 0 else "NaN"
    ville = parts[1].strip() if len(parts) > 1 else "NaN"
    return region, ville


