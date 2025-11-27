FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Prisma
RUN pip install prisma

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Generate Prisma client
RUN prisma generate

# Expose port
EXPOSE 8002

# Start directly without entrypoint
CMD ["python", "manage.py", "runserver", "0.0.0.0:8002"]