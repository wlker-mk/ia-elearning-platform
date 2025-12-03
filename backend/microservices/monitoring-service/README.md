# Monitoring Service

Service de monitoring pour surveiller la santé et les performances des microservices.

## 🚀 Démarrage rapide

### Prérequis
- Go 1.21+
- Docker & Docker Compose
- PostgreSQL
- Redis

### Installation

1. Cloner le projet
```bash
cd monitoring-service
```

2. Copier le fichier d'environnement
```bash
cp .env.example .env
```

3. Installer les dépendances
```bash
go mod download
```

4. Lancer avec Docker
```bash
make docker-up
```

5. Lancer l'application
```bash
make run
```

L'API sera accessible sur `http://localhost:9090`

## 📁 Structure du projet

```
monitoring-service/
├── cmd/                    # Points d'entrée
├── internal/              # Code privé de l'application
│   ├── config/           # Configuration
│   ├── domain/           # Entités métier
│   ├── infrastructure/   # Implémentations techniques
│   ├── application/      # Logique applicative
│   └── interfaces/       # Adaptateurs (HTTP, gRPC)
├── pkg/                  # Code réutilisable
├── api/                  # Définitions API
└── deployments/          # Configuration déploiement
```

## 🔧 Commandes utiles

```bash
make build          # Compiler le projet
make run            # Lancer l'application
make test           # Lancer les tests
make docker-up      # Démarrer Docker
make docker-down    # Arrêter Docker
make help           # Afficher l'aide
```

## 📡 API Endpoints

### Health Check
```
GET /api/v1/health
```

### Monitoring
```
GET /api/v1/monitoring/services
GET /api/v1/monitoring/services/:name
GET /api/v1/monitoring/metrics
```

### Alerts
```
GET /api/v1/alerts
POST /api/v1/alerts
GET /api/v1/alerts/:id
```

## 🐳 Docker

Démarrer tous les services:
```bash
docker-compose -f deployments/docker/docker-compose.yml up -d
```

## 📝 License

MIT
