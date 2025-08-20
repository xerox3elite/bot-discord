# Arsenal Bot - Dockerfile pour Oracle Cloud
FROM python:3.10-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Répertoire de travail
WORKDIR /app

# Installation dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers requirements
COPY requirements.txt .

# Installation dépendances Python
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Création des répertoires nécessaires
RUN mkdir -p logs data backups

# Permissions
RUN chmod +x start_bot.sh || true
RUN chmod 755 logs data

# Port expose (si nécessaire pour monitoring)
EXPOSE 8080

# Sanity check
RUN python -m py_compile main.py

# Variables d'environnement par défaut
ENV ENV=production
ENV DEBUG=false

# Point d'entrée
CMD ["python", "main.py"]
