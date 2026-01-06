#!/bin/bash
set -e

echo "📝 Démarrage du service de stockage..."

# Créer le répertoire de logs
mkdir -p /app/logs

# Attendre PostgreSQL
echo "⏳ Attente de PostgreSQL..."
POSTGRES_HOST="${POSTGRES_HOST:-storage-postgres}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-storage_db}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-rene}"

until PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
    echo "📊 PostgreSQL n'est pas encore prêt..."
    sleep 2
done
echo "✅ PostgreSQL est disponible"

# Attendre Redis
echo "⏳ Attente de Redis..."
REDIS_HOST="${REDIS_HOST:-storage-redis}"
REDIS_PORT="${REDIS_PORT:-6379}"

until redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping | grep -q "PONG"; do
    echo "🔴 Redis n'est pas encore prêt..."
    sleep 2
done
echo "✅ Redis est disponible"

# Appliquer les migrations Prisma si le schéma existe
if [ -f "prisma/schema.prisma" ]; then
    echo "📦 Génération du client Prisma..."
    prisma generate
    
    echo "🔄 Application des migrations Prisma..."
    prisma migrate deploy
    
    # Exécuter le seeding si nécessaire
    if [ -f "prisma/seed.py" ] && [ "$RUN_SEED" = "true" ]; then
        echo "🌱 Exécution du seeding..."
        python prisma/seed.py
    fi
fi

# Appliquer les migrations Django
echo "📋 Application des migrations Django..."
python manage.py migrate

# Collecter les fichiers statiques
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Créer les répertoires média s'ils n'existent pas
echo "📁 Création des répertoires média..."
mkdir -p /app/media/uploads
mkdir -p /app/media/thumbnails
mkdir -p /app/media/temp

# Définir les permissions appropriées
chmod -R 755 /app/media

# Démarrer le serveur
echo "🎯 Démarrage du serveur Django sur le port 8015..."
exec python manage.py runserver 0.0.0.0:8015