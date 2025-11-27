#!/bin/bash
set -e  # Exit on error

echo '🚀 Starting user service...'

# Create logs directory
mkdir -p /app/logs

# Environment variables with defaults
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-user_db}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-rene}"

echo "📊 Database configuration:"
echo "  Host: $POSTGRES_HOST"
echo "  Port: $POSTGRES_PORT"
echo "  Database: $POSTGRES_DB"
echo "  User: $POSTGRES_USER"

# Wait for PostgreSQL with timeout
echo '⏳ Waiting for PostgreSQL...'
MAX_RETRIES=30
RETRY_COUNT=0

until PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo '❌ PostgreSQL connection timeout after 60 seconds'
        exit 1
    fi
    echo "  Attempt $RETRY_COUNT/$MAX_RETRIES - PostgreSQL not ready yet..."
    sleep 2
done

echo '✅ PostgreSQL is available'

# Test database connection
echo '🔍 Testing database connection...'
if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c 'SELECT 1;' > /dev/null 2>&1; then
    echo '✅ Database connection successful'
else
    echo '❌ Database connection failed'
    exit 1
fi

# Generate Prisma client if not already generated
if [ ! -d "/app/prisma/generated" ]; then
    echo '🎯 Generating Prisma client...'
    prisma generate || {
        echo '❌ Prisma client generation failed'
        exit 1
    }
    echo '✅ Prisma client generated'
fi

# Apply Prisma migrations
echo '📋 Applying Prisma migrations...'
prisma migrate deploy || {
    echo '⚠️  Prisma migrations failed, continuing anyway...'
}

# Apply Django migrations (for auth tables only)
echo '🔄 Applying Django migrations...'
python manage.py migrate --noinput || {
    echo '⚠️  Django migrations failed, continuing anyway...'
}

# Collect static files in production
if [ "$DEBUG" = "False" ] || [ "$DJANGO_ENV" = "production" ]; then
    echo '📦 Collecting static files...'
    python manage.py collectstatic --noinput || {
        echo '⚠️  Static files collection failed'
    }
fi

# Create superuser if it doesn't exist (development only)
if [ "$DEBUG" = "True" ] && [ "$CREATE_SUPERUSER" = "True" ]; then
    echo '👤 Creating superuser...'
    python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@example.com').exists():
    User.objects.create_superuser(
        email='admin@example.com',
        username='admin',
        password='admin123'
    )
    print('Superuser created: admin@example.com / admin123')
else:
    print('Superuser already exists')
END
fi

echo '🎯 Starting Django server on 0.0.0.0:8002...'
exec python manage.py runserver 0.0.0.0:8002