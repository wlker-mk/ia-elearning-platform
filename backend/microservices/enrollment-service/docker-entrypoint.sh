#!/bin/bash
set -e

echo "🎓 Starting Enrollments Service..."

# Create logs directory
mkdir -p /app/logs

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
POSTGRES_HOST="${POSTGRES_HOST:-enrollments-postgres}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-enrollments_db}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-rene}"

until PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
    echo "📊 PostgreSQL not ready yet..."
    sleep 2
done
echo "✅ PostgreSQL is available"

# Apply Prisma migrations if schema exists
if [ -f "prisma/schema.prisma" ]; then
    echo "📦 Generating Prisma client..."
    prisma generate
    
    echo "🔄 Applying Prisma migrations..."
    prisma migrate deploy
    
    # Seed if necessary
    if [ -f "prisma/seed.py" ] && [ "$RUN_SEED" = "true" ]; then
        echo "🌱 Running seeding..."
        python prisma/seed.py
    fi
fi

# Apply Django migrations
echo "📋 Applying Django migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Start the server
echo "🎯 Starting Django server on port 8004..."
exec python manage.py runserver 0.0.0.0:8004