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