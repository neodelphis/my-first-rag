# Utiliser une image de base Python légère
FROM python:3.12-slim

# Copier uv depuis l'image officielle (très rapide)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier des dépendances
COPY requirements.txt .

# Installer les dépendances Python avec uv (beaucoup plus rapide que pip !)
RUN uv pip install --system --no-cache -r requirements.txt

# Copier le reste du code de l'application
COPY . .

# Exposer le port par défaut de Streamlit
EXPOSE 8501

# Commande pour lancer l'application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
