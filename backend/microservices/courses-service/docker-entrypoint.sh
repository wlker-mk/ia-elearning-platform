#!/bin/bash
set -e

echo "📚 Starting Courses Service..."

# Create directories
mkdir -p /app/media /app/logs

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
POSTGRES_HOST="${POSTGRES_HOST:-courses-postgres}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-courses_db}"
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

# Create media directories
mkdir -p /app/media/courses /app/media/lessons /app/media/certificates

# Start the server
echo "🎯 Starting Django server on port 8003..."
exec python manage.py runserver 0.0.0.0:8003
