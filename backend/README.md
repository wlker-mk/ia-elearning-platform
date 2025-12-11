# AI E-Learning Platform - Backend

## 🚀 Architecture Microservices

Plateforme d'e-learning avancée avec 21 microservices, Django, Prisma et Docker.

## 📦 Microservices

- **auth-service** (8001) - Authentification JWT
- **user-service** (8002) - Gestion utilisateurs
- **courses-service** (8003) - Cours et inscriptions
- **payments-service** (8006) - Paiements et abonnements
- ... et 17 autres services

## 🛠️ Technologies

- **Backend:** Django 5.0, Django REST Framework
- **Database:** PostgreSQL + Prisma ORM
- **Cache:** Redis
- **Search:** Elasticsearch
- **Queue:** RabbitMQ + Celery
- **Containers:** Docker + Docker Compose

## 🚀 Démarrage Rapide

```bash

# Cloner le projet

git clone <repo-url>
cd ai-elearning-platform

# Copier les variables d'environnement

cp .env.example .env

# Lancer tous les services

docker-compose up -d

# Appliquer les migrations Prisma

./scripts/migrate_all.sh

# Vérifier le statut

docker-compose ps


## 📚 Documentation

- [API Documentation](docs/api/)
- [Deployment Guide](docs/deployment/)
- [Development Setup](docs/development/setup.md)

## 🧪 Tests


```


## 📚 Documentation

- [API Documentation](docs/api/)
- [Deployment Guide](docs/deployment/)
- [Development Setup](docs/development/setup.md)

## 🧪 Tests

bash

# Tests unitaires

pytest tests/unit

# Tests d'intégration

pytest tests/integration

# Tous les tests

make test
```

## 📝 License

MIT License - voir LICENSE file
