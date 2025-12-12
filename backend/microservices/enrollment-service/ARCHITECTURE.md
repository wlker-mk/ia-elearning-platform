# Architecture du Service d'Inscriptions

## Vue d'ensemble

Le service d'inscriptions est un microservice Django qui gère tout le cycle de vie des inscriptions des étudiants, leur progression dans les cours, ainsi que la génération de certificats.

## Stack Technique

### Backend

- **Django 4.2** - Framework web
- **Django REST Framework** - API REST
- **Prisma** - ORM pour Python
- **PostgreSQL 15** - Base de données
- **Redis 7** - Cache et broker Celery
- **Celery** - Tâches asynchrones

### Infrastructure

- **Docker & Docker Compose** - Conteneurisation
- **Gunicorn** - Serveur WSGI pour production
- **Nginx** - (optionnel) Reverse proxy

## Architecture des Modules

``` a
enrollments-service/
│
├── config/                      # Configuration Django
│   ├── settings/               # Settings par environnement
│   ├── celery.py              # Configuration Celery
│   └── urls.py                # Routing principal
│
├── apps/
│   └── enrollments/           # App principale
│       ├── enrollments/       # Module Inscriptions
│       │   ├── views.py      # Endpoints API
│       │   ├── services.py   # Logique métier
│       │   ├── serializers.py # Validation
│       │   ├── tasks.py      # Tâches async
│       │   └── urls.py       # Routes
│       │
│       ├── progress/          # Module Progression
│       │   ├── views.py
│       │   ├── services.py
│       │   ├── serializers.py
│       │   ├── tasks.py
│       │   └── urls.py
│       │
│       └── notes/             # Module Notes & Certificats
│           ├── views.py
│           ├── services.py
│           ├── serializers.py
│           └── urls.py
│
├── shared/                     # Code partagé
│   └── shared/
│       ├── middleware/        # Middleware (JWT auth)
│       └── utils/            # Utilities (exceptions, responses)
│
└── prisma/
    ├── schema.prisma          # Schéma de base de données
    └── seed.py               # Données de test
```

## Modèle de Données

### Enrollment (Inscription)

- Représente l'inscription d'un étudiant à un cours
- Statuts : ACTIVE, COMPLETED, SUSPENDED, EXPIRED, CANCELLED
- Lien avec le paiement et le cours

### Progress (Progression)

- Suivi de la progression par leçon
- Temps passé, pourcentage complété
- Scores de quiz et tentatives
- Position de lecture pour les vidéos

### Certificate (Certificat)

- Certificat généré après complétion
- Numéro unique et code de vérification
- Note et grade calculés automatiquement

### Note

- Notes textuelles des étudiants
- Surlignages de contenu
- Questions sauvegardées
- Liées à des leçons spécifiques

### Bookmark

- Signets sur les leçons
- Timestamps pour les vidéos
- Liens vers des ressources

### StudySession (Session d'étude)

- Enregistrement des sessions d'apprentissage
- Calcul automatique de la durée
- Tracking des appareils et IPs

## Flux de Données

### 1. Création d'Inscription

``` b
Client → POST /enrollments/
    ↓
EnrollmentView → EnrollmentService
    ↓
Validation → Vérification enrollment existant
    ↓
Création enrollment → Mise à jour BDD
    ↓
Response avec enrollment créé
```

### 2. Mise à Jour de Progression

``` a
Client → POST /progress/
    ↓
ProgressView → ProgressService
    ↓
Récupération enrollment
    ↓
Création/Mise à jour progress
    ↓
Calcul progression globale → Mise à jour enrollment
    ↓
Response avec progress
```

### 3. Complétion de Cours

``` c
Client → POST /enrollments/{id}/complete/
    ↓
EnrollmentService
    ↓
Vérification progression (≥80%)
    ↓
Mise à jour enrollment (COMPLETED)
    ↓
Tâche async → generate_certificate_task
    ↓
    ├─ Fetch course & user details
    ├─ Calcul score moyen
    ├─ Génération certificat
    └─ Envoi email (optionnel)
```

## Tâches Asynchrones (Celery)

### Tâches Périodiques

| Tâche | Fréquence | Description |
|-------|-----------|-------------|
| `update_enrollment_statuses` | Toutes les 6h | Marque les enrollments expirés |
| `cleanup_inactive_sessions` | Quotidien 2h | Termine les sessions inactives |
| `generate_daily_progress_reports` | Quotidien 8h | Génère les rapports de progression |

### Tâches à la Demande

- `generate_certificate_task` - Génération de certificat
- `send_certificate_email_task` - Envoi d'email de certificat
- `sync_enrollment_progress` - Synchronisation de la progression

## Communication Inter-Services

Le service communique avec d'autres microservices :

### Services Externes

1. **Courses Service** (`COURSES_SERVICE_URL`)
   - Récupération des détails de cours
   - Validation des IDs de cours/leçons

2. **Users Service** (`USERS_SERVICE_URL`)
   - Récupération des infos étudiants
   - Validation des IDs utilisateurs

3. **Payments Service** (`PAYMENTS_SERVICE_URL`)
   - Lien avec les transactions
   - Validation des paiements

### Méthode de Communication

- **HTTP REST** - Appels synchrones pour les opérations critiques
- **Events** (futur) - Messages asynchrones via RabbitMQ/Kafka

## Authentification & Autorisation

### JWT Authentication

Le service utilise un middleware JWT personnalisé :

```python
Authorization: Bearer <jwt-token>
```

Le token JWT doit contenir :

- `user_id` - ID de l'utilisateur
- `role` - Rôle (student, instructor, admin)
- `email` - Email de l'utilisateur

### Permissions

- **Student** : Accès à ses propres données
- **Instructor** : Peut voir les données de ses cours
- **Admin** : Accès complet

## Patterns et Principes

### Service Layer Pattern

Chaque module utilise un service layer pour la logique métier :

```python
with EnrollmentService() as service:
    enrollment = service.create_enrollment(user_id, data)
```

### Repository Pattern

Les services utilisent Prisma comme abstraction de données :

```python
enrollment = self.db.enrollment.create(data={...})
```

### Context Manager

Les services implémentent le context manager pour gérer les connexions :

```python
def __enter__(self):
    self.db.connect()
    return self

def __exit__(self, exc_type, exc_val, exc_tb):
    self.db.disconnect()
```

## Gestion des Erreurs

### Exceptions Personnalisées

- `EnrollmentAlreadyExists` - 409 Conflict
- `EnrollmentNotFound` - 404 Not Found
- `EnrollmentExpired` - 403 Forbidden
- `InsufficientProgress` - 400 Bad Request
- etc.

### Format de Réponse Standard

```json
{
  "success": true/false,
  "message": "Message descriptif",
  "data": {...},
  "errors": {...}
}
```

## Scalabilité

### Horizontal Scaling

Le service est stateless et peut être scalé horizontalement :

```yaml
services:
  web:
    deploy:
      replicas: 3
```

### Caching Strategy

- **Redis** pour le cache de sessions
- **Database indexes** pour les requêtes fréquentes

### Optimisations

- Connexions poolées pour PostgreSQL
- Batch processing pour les tâches Celery
- Pagination sur tous les endpoints de liste

## Monitoring & Logging

### Logs Structurés

```python
logger.info(f"Enrollment {enrollment_id} completed by {student_id}")
```

### Métriques Clés

- Nombre d'inscriptions actives
- Temps moyen de complétion
- Taux de génération de certificats
- Performance des tâches Celery

### Health Checks

```http
GET /health/
→ {"status": "healthy"}
```

## Sécurité

### Mesures Implémentées

1. **Authentication JWT** - Tous les endpoints protégés
2. **Input Validation** - Serializers DRF
3. **SQL Injection** - Protection via Prisma ORM
4. **CORS** - Configuration stricte
5. **Rate Limiting** - (à implémenter)
6. **HTTPS Only** - En production

### Données Sensibles

- Tokens JWT avec expiration
- Pas de stockage de mots de passe
- Logs sans données sensibles

## Déploiement

### Environnements

1. **Development** - Docker Compose local
2. **Staging** - Kubernetes staging cluster
3. **Production** - Kubernetes production cluster

### CI/CD Pipeline

``` CI/CD Pipeline
Code Push → Tests → Build Docker Image → Deploy to K8s
```

### Rolling Updates

```bash
kubectl rollout status deployment/enrollments-service
kubectl rollout history deployment/enrollments-service
```

## Performance

### Benchmarks Cibles

- Temps de réponse API : < 200ms (p95)
- Throughput : > 1000 req/s
- Uptime : 99.9%

### Database Queries

- Indexes sur les colonnes fréquemment filtrées
- Pagination obligatoire sur les listes
- Lazy loading des relations

## Tests

### Types de Tests

1. **Unit Tests** - Services et utils
2. **Integration Tests** - Flux complets
3. **API Tests** - Endpoints REST

### Coverage Target

- Minimum 80% de couverture de code
- 100% sur la logique métier critique

## Roadmap

### Prochaines Fonctionnalités

- [ ] Webhooks pour les événements
- [ ] GraphQL API
- [ ] Analytics avancés
- [ ] Gamification (badges, points)
- [ ] Recommendations de cours
- [ ] Mobile SDK

### Améliorations Techniques

- [ ] Caching Redis avancé
- [ ] Event-driven architecture
- [ ] Kubernetes auto-scaling
- [ ] APM integration (Datadog/New Relic)
- [ ] Feature flags
