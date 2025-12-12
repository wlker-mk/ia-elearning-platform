FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Node.js for Prisma
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Prisma CLI globally
RUN npm install -g prisma

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Make entrypoint executable
RUN chmod +x docker-entrypoint.sh

# Generate Prisma client
RUN prisma generate

# Expose port
EXPOSE 8004

# Start the application
CMD ["./docker-entrypoint.sh"]