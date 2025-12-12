# Enrollments Service 🎓

Service de gestion des inscriptions, progression, notes et certificats pour une plateforme d'apprentissage en ligne (LMS).

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-4.2-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Démarrage Rapide](#-démarrage-rapide)
- [Documentation](#-documentation)
- [API Endpoints](#-api-endpoints)
- [Configuration](#️-configuration)
- [Développement](#-développement)
- [Tests](#-tests)
- [Déploiement](#-déploiement)
- [Contribution](#-contribution)

## ✨ Fonctionnalités

### 📚 Inscriptions (Enrollments)

- ✅ Inscription des étudiants aux cours
- ✅ Gestion des statuts (ACTIVE, COMPLETED, SUSPENDED, etc.)
- ✅ Suivi du temps passé et dernier accès
- ✅ Support des inscriptions payantes
- ✅ Expiration automatique des inscriptions

### 📊 Progression (Progress)

- ✅ Suivi détaillé par leçon
- ✅ Enregistrement du temps passé
- ✅ Position de lecture vidéo
- ✅ Scores et tentatives des quiz
- ✅ Sessions d'étude avec tracking
- ✅ Calcul des streaks d'apprentissage

### 📝 Notes et Bookmarks

- ✅ Prise de notes textuelles
- ✅ Surlignage de contenu
- ✅ Notes de type question
- ✅ Bookmarks avec timestamps
- ✅ Organisation par leçon

### 🏆 Certificats

- ✅ Génération automatique
- ✅ Numéro et code de vérification uniques
- ✅ Calcul automatique des notes
- ✅ Validation et révocation
- ✅ API de vérification publique

## 🚀 Démarrage Rapide

### Avec Docker (Recommandé)

```bash
# Cloner le repository
git clone <repository-url>
cd enrollments-service

# Configuration
cp .env.example .env
# Éditer .env avec vos valeurs

# Démarrer tous les services
make build && make up

# Initialiser la base de données
make prisma-generate
make prisma-push

# (Optionnel) Charger des données de test
make seed

# Vérifier que tout fonctionne
make health
```

✅ L'API est maintenant accessible sur http:/localhost:8004

📚 Documentation API : http://localhost:8004/api/docs/

### Installation Manuelle

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env

# Générer le client Prisma
prisma generate
prisma db push

# Démarrer le serveur
python manage.py runserver
```

## 🏗️ Architecture

```text
enrollments-service/
├── 📁 apps/
│   └── enrollments/
│       ├── enrollments/      # Module Inscriptions
│       ├── progress/         # Module Progression
│       └── notes/           # Module Notes & Certificats
├── 📁 config/               # Configuration Django
├── 📁 shared/               # Code partagé (middleware, utils)
├── 📁 prisma/               # Schéma et migrations
└── 🐳 docker-compose.yml    # Orchestration
```

**Stack Technique:**

- 🐍 Python 3.11+ / Django 4.2
- 🗄️ PostgreSQL 15 (via Prisma ORM)
- 🔴 Redis 7 (Cache & Celery)
- 📦 Docker & Docker Compose
- 🔄 Celery (Tâches asynchrones)

Pour plus de détails : [ARCHITECTURE.md](ARCHITECTURE.md)

## 📚 Documentation

- 📖 [Quick Start Guide](QUICK_START.md) - Démarrage en 5 minutes
- 🏗️ [Architecture](ARCHITECTURE.md) - Architecture détaillée
- 🤝 [Contributing](CONTRIBUTING.md) - Guide de contribution
- 📋 [API Documentation](http://localhost:8004/api/docs/) - Swagger UI

## 🔌 API Endpoints

### Inscriptions

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/api/v1/enrollments/` | Créer une inscription |
| `GET` | `/api/v1/enrollments/` | Liste des inscriptions |
| `GET` | `/api/v1/enrollments/{id}/` | Détails d'une inscription |
| `PATCH` | `/api/v1/enrollments/{id}/` | Mettre à jour |
| `DELETE` | `/api/v1/enrollments/{id}/` | Annuler |
| `POST` | `/api/v1/enrollments/{id}/complete/` | Compléter un cours |
| `GET` | `/api/v1/enrollments/my-enrollments/` | Mes inscriptions |
| `GET` | `/api/v1/enrollments/stats/` | Statistiques |

### Progression

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/api/v1/enrollments/progress/` | Créer/Mettre à jour |
| `GET` | `/api/v1/enrollments/progress/{id}/` | Détails |
| `GET` | `/api/v1/enrollments/progress/course/{id}/` | Progression par cours |
| `GET` | `/api/v1/enrollments/progress/stats/` | Statistiques |
| `POST` | `/api/v1/enrollments/progress/sessions/start/` | Démarrer session |
| `POST` | `/api/v1/enrollments/progress/sessions/{id}/end/` | Terminer session |

### Notes & Certificats

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/api/v1/enrollments/notes/` | Créer une note |
| `GET` | `/api/v1/enrollments/notes/` | Liste des notes |
| `PATCH` | `/api/v1/enrollments/notes/{id}/` | Mettre à jour |
| `DELETE` | `/api/v1/enrollments/notes/{id}/` | Supprimer |
| `POST` | `/api/v1/enrollments/notes/bookmarks/` | Créer bookmark |
| `GET` | `/api/v1/enrollments/notes/certificates/` | Liste certificats |
| `GET` | `/api/v1/enrollments/notes/certificates/verify/{code}/` | Vérifier |

## ⚙️ Configuration

### Variables d'environnement essentielles

```bash
# Base de données
DATABASE_URL=postgresql://user:pass@localhost:5432/enrollments_db

# Redis & Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# Services externes
COURSES_SERVICE_URL=http://localhost:8001
USERS_SERVICE_URL=http://localhost:8002
PAYMENTS_SERVICE_URL=http://localhost:8003

# Certificats
CERTIFICATE_DOMAIN=https://yourdomain.com
```

Voir [.env.example](.env.example) pour la liste complète.

## 💻 Développement

### Commandes utiles

```bash
# Démarrer les services
make up                 # Démarrer tout
make logs              # Voir les logs
make shell             # Django shell
make bash              # Bash dans le container

# Base de données
make prisma-generate   # Générer client Prisma
make prisma-push       # Appliquer le schéma
make seed              # Charger données test

# Tests
make test              # Lancer les tests
make test-coverage     # Tests avec couverture

# Maintenance
make restart           # Redémarrer
make down              # Arrêter
make clean             # Nettoyer tout
```

### Structure d'un Module

```python
# apps/enrollments/[module]/
├── views.py          # Endpoints REST API
├── services.py       # Logique métier
├── serializers.py    # Validation DRF
├── tasks.py          # Tâches Celery
├── urls.py           # Routes
└── tests.py          # Tests
```

## 🧪 Tests

```bash
# Lancer tous les tests
make test

# Tests avec couverture
make test-coverage

# Tests spécifiques
docker-compose exec web pytest apps/enrollments/tests/test_enrollments.py -v

# Ouvrir le rapport de couverture
open htmlcov/index.html
```

**Couverture cible :** 80% minimum

## 🚀 Déploiement

### Docker Compose (Staging)

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Kubernetes (Production)

```bash
kubectl apply -f k8s/
kubectl rollout status deployment/enrollments-service
```

### Variables d'environnement en Production

```bash
DEBUG=False
ALLOWED_HOSTS=api.yourdomain.com
DJANGO_SETTINGS_MODULE=config.settings.production
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour :

- Standards de code
- Workflow Git
- Process de review
- Templates de PR/Issues

### Quick Contribution

```bash
# Fork et clone
git clone https://github.com/your-username/enrollments-service.git

# Créer une branche
git checkout -b feature/ma-fonctionnalite

# Faire vos changements et tests
make format
make lint
make test

# Commit et push
git commit -m "feat: ajouter ma fonctionnalité"
git push origin feature/ma-fonctionnalite

# Créer une Pull Request
```

## 📊 Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8004/health/

# Celery status
docker-compose exec celery celery -A config inspect active
```

### Tâches Celery Planifiées

- ⏰ **Toutes les 6h** : Mise à jour statuts d'inscription
- ⏰ **Quotidien 2h** : Nettoyage sessions inactives
- ⏰ **Quotidien 8h** : Rapports de progression

## 🔐 Sécurité

- ✅ Authentification JWT requise
- ✅ Validation stricte des inputs
- ✅ Protection contre injection SQL (Prisma)
- ✅ Configuration CORS sécurisée
- ✅ HTTPS only en production
- ✅ Rate limiting (à configurer)

## 📝 License

MIT License - voir [LICENSE](LICENSE)

## 🎯 Roadmap

### Version 2.0

- [ ] GraphQL API
- [ ] Webhooks pour événements
- [ ] Analytics avancés
- [ ] Gamification (badges, points)
- [ ] Mobile SDK

### Améliorations Techniques

- [ ] Event-driven architecture
- [ ] Kubernetes auto-scaling
- [ ] APM integration
- [ ] Feature flags

---
