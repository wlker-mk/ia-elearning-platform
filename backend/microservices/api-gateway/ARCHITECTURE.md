# Architecture de l'API Gateway

## Vue d'ensemble

L'API Gateway est construit sur une architecture en couches avec des responsabilités bien définies.

## Structure du projet
```
api-gateway/
├── cmd/
│   └── api-gateway/          # Point d'entrée
│       └── main.go
├── internal/
│   ├── auth/                 # Authentification JWT
│   ├── cache/                # Gestion du cache
│   ├── circuit/              # Circuit breaker
│   ├── config/               # Configuration
│   ├── discovery/            # Service discovery
│   ├── errors/               # Gestion des erreurs
│   ├── gateway/              # Cœur du gateway
│   ├── loadbalancer/         # Load balancing
│   ├── logger/               # Logging
│   ├── metrics/              # Métriques
│   ├── middleware/           # Middlewares
│   ├── ratelimit/            # Rate limiting
│   └── router/               # Routage
├── pkg/                      # Utilitaires réutilisables
├── configs/                  # Fichiers de configuration
├── deployments/              # Déploiement K8s/Docker
└── tests/                    # Tests
```

## Flux de requête
```
1. Client envoie requête
   ↓
2. Middleware Logger (log entrée)
   ↓
3. Middleware CORS (headers CORS)
   ↓
4. Middleware RequestID (génère ID unique)
   ↓
5. Middleware Security (headers sécurité)
   ↓
6. Middleware Auth (validation JWT) [si requis]
   ↓
7. Middleware RateLimit (vérif limite)
   ↓
8. Circuit Breaker (vérif état service)
   ↓
9. Load Balancer (sélection instance)
   ↓
10. Proxy HTTP (forward vers service)
   ↓
11. Service traite requête
   ↓
12. Réponse remonte via proxy
   ↓
13. Middleware Logger (log sortie)
   ↓
14. Client reçoit réponse
```

## Composants principaux

### 1. Gateway Core (`internal/gateway/`)

**Responsabilités:**
- Gestion du registry des services
- Configuration des proxies HTTP
- Coordination des composants

**Fichiers clés:**
- `gateway.go` - Structure principale et initialisation
- `config.go` - Enregistrement des services
- `proxy.go` - Logique de proxying
- `circuitbreaker.go` - Circuit breaker par service
- `ratelimiter.go` - Rate limiting avec Redis

### 2. Router (`internal/router/`)

**Responsabilités:**
- Définition des routes
- Association routes ↔ services
- Regroupement par niveau d'accès

**Fichiers clés:**
- `router.go` - Configuration complète des routes
- `health.go` - Endpoints de santé
- `handlers.go` - Handlers spécifiques

### 3. Middleware (`internal/middleware/`)

**Stack de middlewares:**
```
Recovery → Logger → CORS → RequestID → Security → Auth → RateLimit → Timeout
```

Chaque middleware:
- Peut court-circuiter la chaîne
- Enrichit le contexte
- Log ses actions
- Gère ses erreurs

### 4. Authentication (`internal/auth/`)

**JWT Flow:**
```
1. Client login → Auth Service
2. Auth Service génère JWT
3. Client stocke JWT
4. Client envoie JWT dans Authorization header
5. Gateway valide JWT
6. Gateway extrait claims (user_id, role)
7. Gateway injecte dans contexte
8. Service backend utilise X-User-ID header
```

### 5. Rate Limiting (`internal/ratelimit/`)

**Algorithme: Sliding Window avec Redis**
```
Key: ratelimit:{client_ip}
TTL: 60 secondes
Max: 100 requêtes

Pour chaque requête:
1. INCR ratelimit:{ip}
2. EXPIRE ratelimit:{ip} 60
3. Si count > 100 → 429 Too Many Requests
```

### 6. Circuit Breaker (`internal/circuit/`)

**États:**
```
CLOSED (normal)
  │ 5 erreurs consécutives
  ↓
OPEN (bloque requêtes)
  │ Attente 30s
  ↓
HALF_OPEN (teste service)
  │ Succès → CLOSED
  │ Échec → OPEN
```

**Configuration par service:**
- Threshold: 5 erreurs
- Timeout: 30 secondes
- Reset automatique

### 7. Load Balancer (`internal/loadbalancer/`)

**Algorithmes disponibles:**

1. **Round Robin** (défaut)
```
S1 → S2 → S3 → S1 → ...
```

2. **Least Connections**
```
Choisit le serveur avec le moins de connexions actives
```

### 8. Service Discovery (`internal/discovery/`)

**Mode statique (actuel):**
- Services définis dans .env
- Enregistrement au démarrage
- URLs hardcodées

**Migration future vers Consul:**
- Service registration automatique
- Health checks distribués
- DNS-based discovery

### 9. Cache (`internal/cache/`)

**Stratégies:**

1. **Redis Cache** (production)
- Cache distribué
- Persistance optionnelle
- TTL configurable

2. **Memory Cache** (dev/test)
- Cache local
- Pas de persistance
- Rapide pour tests

### 10. Metrics (`internal/metrics/`)

**Métriques exposées:**
- `gateway_requests_total` - Total requêtes
- `gateway_request_duration_seconds` - Latence
- `gateway_errors_total` - Total erreurs
- `gateway_circuit_breaker_state` - État CB
- `gateway_active_connections` - Connexions actives

## Patterns utilisés

### 1. Middleware Pattern
Chaîne de responsabilité pour traiter requêtes

### 2. Circuit Breaker Pattern
Protection contre cascades de pannes

### 3. Proxy Pattern
Encapsulation des appels services

### 4. Factory Pattern
Création d'objets (cache, limiters)

### 5. Singleton Pattern
Instance unique du gateway

## Scalabilité

### Horizontal Scaling
```
Load Balancer (L7)
    │
    ├─→ Gateway Instance 1
    ├─→ Gateway Instance 2
    └─→ Gateway Instance 3
        ↓
    Redis (shared state)
```

**Avantages:**
- Pas de session affinity requise
- État partagé dans Redis
- Scale indépendamment des services

### Vertical Scaling

**Optimisations possibles:**
- Augmenter pool de connexions HTTP
- Buffer sizes plus grands
- More goroutines pour proxy

## Sécurité

### Headers de sécurité
```go
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
```

### Rate Limiting layers

1. **Global** - 1000 req/min par IP
2. **Par endpoint** - Limites spécifiques
3. **Par utilisateur** - Quota personnalisé

### JWT Security

- Secret minimum 32 caractères
- Expiration 24h
- Refresh token 7 jours
- Validation signature systématique

## Performance

### Latence cible

- P50: < 10ms (overhead gateway)
- P95: < 50ms
- P99: < 100ms

### Optimisations

1. **Connection pooling**
```go
MaxIdleConns: 100
MaxIdleConnsPerHost: 100
IdleConnTimeout: 90s
```

2. **Keep-alive**
```go
DisableKeepAlives: false
```

3. **Timeouts**
```go
Timeout: 30s
ReadTimeout: 15s
WriteTimeout: 15s
```

## Observabilité

### Logging
```json
{
  "level": "info",
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "uuid",
  "method": "GET",
  "path": "/api/users",
  "status": 200,
  "latency": "15ms",
  "service": "user-service"
}
```

### Tracing

Integration avec Jaeger/Zipkin:
- Trace ID propagation
- Span creation par service
- Visualisation des appels

### Alerting

Alertes configurées sur:
- Taux d'erreur > 1%
- Latence P99 > 500ms
- Circuit breaker OPEN
- Service down > 1min

## Évolution future

### Phase 2
- [ ] Service mesh integration (Istio)
- [ ] gRPC support
- [ ] GraphQL federation
- [ ] WebSocket support

### Phase 3
- [ ] Multi-region deployment
- [ ] Chaos engineering
- [ ] A/B testing support
- [ ] API versioning