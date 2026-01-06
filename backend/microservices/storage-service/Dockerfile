FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système y compris Node.js pour Prisma
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installer Prisma CLI globalement
RUN npm install -g prisma

# Copier l'application
COPY . .

# Créer le répertoire de logs
RUN mkdir -p /app/logs

# Rendre le point d'entrée exécutable
RUN chmod +x docker-entrypoint.sh

# Générer le client Prisma
RUN prisma generate

# Exposer le port
EXPOSE 8015

# Démarrer l'application
CMD ["./docker-entrypoint.sh"]