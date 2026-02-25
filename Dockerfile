# Image de base Python 3.13
FROM python:3.13-slim

# Répertoire de travail dans le conteneur
WORKDIR /app

# Copier les dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code du projet
COPY . .

# Exposer le port (adapter selon ton app, ex: Flask = 5000, Django = 8000)
EXPOSE 5000

# Commande de lancement (adapter selon ton fichier principal)
CMD ["python", "app/main.py"]
