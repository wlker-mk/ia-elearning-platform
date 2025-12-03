# 🚀 API Gateway - Go

Point d'entrée unique haute performance pour l'architecture microservices.

## ✨ Caractéristiques

- ✅ **Haute performance** - Écrit en Go pour une vitesse maximale
- ✅ **Faible latence** - Proxy inversé optimisé
- ✅ **Rate Limiting** - Protection avec Redis
- ✅ **Circuit Breaker** - Résilience des services
- ✅ **JWT Authentication** - Sécurité intégrée
- ✅ **22 Microservices** - Architecture complète

## 🏗️ Architecture
```
Client → API Gateway :8000 → [22 Microservices]
           ↓
     [Redis Cache]
     [Rate Limiter]
     [Circuit Breaker]
     [JWT Auth]
```

## 📦 Installation

### Prérequis

- Go 1.21+
- Docker & Docker Compose
- Redis

### Quick Start
```bash
# 1. Cloner le projet
cd api-gateway

# 2. Copier .env
cp .env.example .env

# 3. Modifier les variables
nano .env

# 4. Installer les dépendances
make deps

# 5. Lancer avec Docker
make docker-run

# 6. Vérifier
make health
```

## 🚀 Utilisation

### Développement local
```bash
# Démarrer le gateway
make run

# Avec hot reload
make dev
```

### Avec Docker
```bash
# Build & Run
make docker-build
make docker-run

# Logs
make docker-logs

# Stop
make docker-stop
```

## 📡 Services disponibles

| Service | Port | URL |
|---------|------|-----|
| API Gateway | 8000 | http://localhost:8000 |
| User Service | 8001 | http://user-service:8001 |
| Auth Service | 8002 | http://auth-service:8002 |
| Courses Service | 8003 | http://courses-service:8003 |
| ... | ... | ... |

## 🔌 API Endpoints

### Authentification (Public)
```
POST   /api/auth/login
POST   /api/auth/register
POST   /api/auth/refresh
```

### Users (Protected)
```
GET    /api/users
POST   /api/users
GET    /api/users/:id
PUT    /api/users/:id
DELETE /api/users/:id
```

### Courses (Protected)
```
GET    /api/courses
POST   /api/courses
GET    /api/courses/:id
PUT    /api/courses/:id
DELETE /api/courses/:id
```

## ⚙️ Configuration

### Variables d'environnement
```bash
SERVICE_PORT=8000
JWT_SECRET=your-secret-key
REDIS_URL=redis:6379
RATE_LIMIT_MAX=100
RATE_LIMIT_WINDOW=60
```

## 🧪 Tests
```bash
# Tous les tests
make test

# Avec couverture
make test-coverage

# Benchmarks
make benchmark
```

## 📊 Monitoring
```bash
# Health check
curl http://localhost:8000/health

# Services health
curl http://localhost:8000/api/services/health

# Gateway stats
curl http://localhost:8000/api/gateway/stats
```

## 🛠️ Commandes Make
```bash
make help              # Aide
make build             # Build
make run               # Run local
make test              # Tests
make docker-build      # Build Docker
make docker-run        # Run Docker
make health            # Health check
make clean             # Clean
```

## 📝 License

MIT
# API Gateway Documentation

Bienvenue dans la documentation de l'API Gateway.

## Table des matières

1. [Architecture](./ARCHITECTURE.md)
2. [API Reference](./API.md)
3. [Deployment Guide](./DEPLOYMENT.md)
4. [Monitoring Guide](./MONITORING.md)
5. [Contributing Guide](./CONTRIBUTING.md)

## Vue d'ensemble

L'API Gateway est le point d'entrée unique pour l'architecture microservices. Il gère:

- **Routage** - Redirection vers les services appropriés
- **Authentification** - Validation JWT
- **Rate Limiting** - Protection contre les abus
- **Circuit Breaker** - Résilience des services
- **Load Balancing** - Distribution de charge
- **Monitoring** - Métriques et logs

## Démarrage rapide
```bash
# Cloner le projet
git clone <repository-url>
cd api-gateway

# Installer les dépendances
make deps

# Configurer l'environnement
cp .env.example .env
nano .env

# Lancer le gateway
make run
```

## Architecture
```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│       API Gateway :8000         │
│  ┌──────────────────────────┐   │
│  │  Rate Limiter (Redis)    │   │
│  ├──────────────────────────┤   │
│  │  Circuit Breaker         │   │
│  ├──────────────────────────┤   │
│  │  JWT Auth                │   │
│  ├──────────────────────────┤   │
│  │  Load Balancer           │   │
│  └──────────────────────────┘   │
└─────────────┬───────────────────┘
              │
    ┌─────────┴─────────┐
    ▼                   ▼
┌─────────┐       ┌─────────┐
│Service 1│  ...  │Service N│
└─────────┘       └─────────┘
```

## Configuration

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|---------|
| SERVICE_PORT | Port du gateway | 8000 |
| JWT_SECRET | Secret JWT | - |
| REDIS_URL | URL Redis | localhost:6379 |
| RATE_LIMIT_MAX | Limite de requêtes | 100 |
| RATE_LIMIT_WINDOW | Fenêtre (secondes) | 60 |

### Services disponibles

Le gateway route vers 21 microservices:

1. User Service (8001)
2. Auth Service (8002)
3. Courses Service (8003)
4. Enrollment Service (8004)
5. Quizzes Service (8005)
6. Payments Service (8006)
7. Bookings Service (8007)
8. Notifications Service (8008)
9. Communications Service (8009)
10. Chatbot Service (8010)
11. Analytics Service (8011)
12. Monitoring Service (8012)
13. Search Service (8013)
14. Cache Service (8014)
15. Storage Service (8015)
16. Gamification Service (8016)
17. Reviews Service (8017)
18. Webinars Service (8018)
19. Sponsors Service (8019)
20. I18n Service (8020)
21. Security Service (8021)

## Endpoints

### Public Endpoints
```
POST   /api/auth/login        - Connexion utilisateur
POST   /api/auth/register     - Inscription utilisateur
POST   /api/auth/refresh      - Rafraîchir le token
GET    /health                - Health check
```

### Protected Endpoints

Nécessitent un token JWT valide dans le header Authorization:
```
Authorization: Bearer <token>
```
```
GET    /api/users             - Liste des utilisateurs
GET    /api/courses           - Liste des cours
POST   /api/courses           - Créer un cours
GET    /api/payments          - Historique des paiements
...
```

### Admin Endpoints

Nécessitent un rôle admin:
```
GET    /api/admin/users       - Gestion utilisateurs
GET    /api/admin/statistics  - Statistiques système
POST   /api/admin/cache/clear - Vider le cache
```

## Tests
```bash
# Tous les tests
make test

# Tests avec couverture
make test-coverage

# Tests d'intégration
go test ./tests/integration/... -v

# Tests e2e
go test ./tests/e2e/... -v
```

## Monitoring

Le gateway expose des métriques Prometheus sur `/metrics`:

- Nombre de requêtes par service
- Latence moyenne
- Taux d'erreur
- État du circuit breaker
- Utilisation du cache

## Support

Pour toute question ou problème:

- Ouvrir une issue sur GitHub
- Consulter la [documentation complète](./docs/)
- Contacter l'équipe via Slack

## License

MIT License - voir [LICENSE](../LICENSE)