FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including multimedia libraries
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    ffmpeg \
    libmagic1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Prisma
RUN pip install prisma

# Copy application
COPY . .

# Create media and logs directories
RUN mkdir -p /app/media /app/logs

# Make entrypoint executable
RUN chmod +x docker-entrypoint.sh

# Generate Prisma client
RUN prisma generate

# Expose port
EXPOSE 8003

# Start the application
CMD ["./docker-entrypoint.sh"]