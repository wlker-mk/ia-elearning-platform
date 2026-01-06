# backend/microservices/user-service/config/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Schema view pour Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="👥 User Service API",
        default_version='v1',
        description="""
# User Service - API Documentation

Service de gestion des utilisateurs, profils, étudiants et instructeurs.

## 🎯 Vue d'ensemble

Ce service gère toutes les données utilisateurs:
- **Profils** personnels
- **Étudiants** avec système de gamification
- **Instructeurs** avec certifications et ratings
- **Préférences** utilisateur

## 📋 Structure des Données

### Profil Utilisateur
- Informations personnelles
- Photo de profil et bannière
- Réseaux sociaux
- Localisation
- Préférences (langue, timezone)

### Étudiant
- Code étudiant unique (STU + année + 6 chiffres)
- Points et niveau (gamification)
- Streak d'activité
- Statistiques d'apprentissage
- Catégories préférées

### Instructeur
- Code instructeur unique (INS + année + 6 chiffres)
- Spécialisations et expertise
- Certifications
- Rating et reviews
- Statistiques (étudiants, cours)
- Taux horaire
- Vérification (badge)

## 🎮 Système de Gamification

### Points et Niveaux
- 1 point = 10 XP
- 100 XP = 1 niveau
- XP gagné par:
  - Complétion de cours
  - Exercices réussis
  - Certifications obtenues
  - Streak d'activité

### Streak
- +1 jour pour activité quotidienne
- Reset si gap > 24h
- Max streak sauvegardé
- Bonus XP pour long streak

## 🏆 Leaderboard

Classement des étudiants par:
1. Points totaux
2. Niveau
3. Streak actuel

## 🔒 Authentification

Service intégré avec **Auth Service** pour l'authentification.

Header requis:
```
Authorization: Bearer <access_token>
```

## 📊 Endpoints Principaux

### Profils
- `GET/POST /api/users/profiles/me/` - Mon profil
- `PUT /api/users/profiles/me/` - Mettre à jour
- `GET /api/users/profiles/{user_id}/` - Profil public

### Étudiants
- `GET/POST /api/users/students/me/` - Mon profil étudiant
- `POST /api/users/students/experience/` - Ajouter XP
- `POST /api/users/students/streak/` - Mettre à jour streak
- `GET /api/users/students/leaderboard/` - Classement

### Instructeurs
- `GET/POST /api/users/instructors/me/` - Mon profil instructeur
- `GET /api/users/instructors/{user_id}/` - Profil public
- `GET /api/users/instructors/top/` - Meilleurs instructeurs
- `GET /api/users/instructors/search/` - Rechercher

## 🌐 Environnements

| Environment | URL | Status |
|-------------|-----|--------|
| Production | https://api.lms.com | 🟢 Live |
| Staging | https://staging-api.lms.com | 🟡 Testing |
| Development | http://localhost:8002 | 🔵 Local |

## 📞 Support

- Email: support@lms-platform.com
- Docs: https://docs.lms-platform.com
- Status: https://status.lms-platform.com

## 🔄 Intégrations

- **Auth Service** - Authentification
- **Course Service** - Cours et inscriptions
- **Analytics Service** - Statistiques
- **Notification Service** - Notifications
        """,
        terms_of_service="https://www.lms-platform.com/terms/",
        contact=openapi.Contact(
            name="LMS Platform API Team",
            email="api@lms-platform.com"
        ),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

def health_check(request):
    """Endpoint de santé du service"""
    return JsonResponse({
        "status": "healthy",
        "service": "user-service",
        "version": "v1.0.0"
    })

def api_root(request):
    """Endpoint racine avec informations du service"""
    return JsonResponse({
        "service": "user-service",
        "version": "v1.0.0",
        "description": "Service de gestion des utilisateurs, profils, étudiants et instructeurs",
        "status": "running",
        "documentation": {
            "swagger": request.build_absolute_uri('/swagger/'),
            "redoc": request.build_absolute_uri('/redoc/'),
            "openapi_json": request.build_absolute_uri('/swagger.json'),
            "openapi_yaml": request.build_absolute_uri('/swagger.yaml')
        },
        "endpoints": {
            "health": "/api/health/",
            "profiles": "/api/users/profiles/",
            "students": "/api/users/students/",
            "instructors": "/api/users/instructors/"
        },
        "features": {
            "profiles": "Gestion des profils utilisateurs",
            "students": "Profils étudiants avec gamification",
            "instructors": "Profils instructeurs avec certifications",
            "leaderboard": "Classement des étudiants",
            "search": "Recherche d'instructeurs"
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ==========================================
    # HEALTH & INFO
    # ==========================================
    path('', api_root, name='api-root'),
    path('api/health/', health_check, name='health_check'),
    
    # ==========================================
    # API ENDPOINTS
    # ==========================================
    path('api/users/', include('apps.users.urls')),
    
    # ==========================================
    # API DOCUMENTATION
    # ==========================================
    # Swagger JSON/YAML
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    
    # Swagger UI (interface interactive)
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    
    # ReDoc UI (documentation alternative)
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
]

# Servir les fichiers médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)