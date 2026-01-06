# backend/microservices/user-service/apps/users/swagger_schemas.py

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# ==========================================
# SCHEMA VIEW CONFIGURATION
# ==========================================

schema_view = get_schema_view(
    openapi.Info(
        title="User Service API",
        default_version='v1',
        description="""
# 👥 User Service API Documentation

Service de gestion des utilisateurs, profils, étudiants et instructeurs.

## 🚀 Fonctionnalités

### Profils Utilisateurs
- Création et gestion de profils complets
- Informations personnelles
- Photos de profil et bannière
- Liens réseaux sociaux
- Préférences (langue, timezone, devise)

### Étudiants
- Système de points et niveaux (gamification)
- Suivi du streak d'activité
- Statistiques d'apprentissage
- Classement (leaderboard)
- Catégories préférées

### Instructeurs
- Profil professionnel
- Spécialisations et expertise
- Certifications
- Système de notation
- Vérification des instructeurs
- Statistiques (étudiants, cours)

## 🎯 Workflows Principaux

### 📝 Étudiant
1. Créer profil → `POST /api/users/profiles/me/`
2. Créer profil étudiant → `POST /api/users/students/me/`
3. Ajouter XP → `POST /api/users/students/experience/`
4. Mettre à jour streak → `POST /api/users/students/streak/`

### 🎓 Instructeur
1. Créer profil → `POST /api/users/profiles/me/`
2. Créer profil instructeur → `POST /api/users/instructors/me/`
3. Vérification (admin) → `POST /api/users/instructors/verify/{user_id}/`

## 🔒 Authentification

**Note**: Ce service utilise l'authentification centralisée du Auth Service.

Header requis:
```
Authorization: Bearer <access_token>
```

## 📊 Codes de Statut

- `200` - Succès
- `201` - Créé
- `400` - Requête invalide
- `401` - Non authentifié
- `403` - Accès refusé
- `404` - Non trouvé
- `500` - Erreur serveur

## 🌐 Environnements

- **Production**: `https://api.lms-platform.com`
- **Development**: `http://localhost:8002`
        """,
        terms_of_service="https://www.lms-platform.com/terms/",
        contact=openapi.Contact(
            name="LMS Platform Support",
            email="support@lms-platform.com"
        ),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


# ==========================================
# PROFILE SCHEMAS
# ==========================================

profile_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['first_name', 'last_name'],
    properties={
        'first_name': openapi.Schema(
            type=openapi.TYPE_STRING,
            maxLength=100,
            description='Prénom',
            example='John'
        ),
        'last_name': openapi.Schema(
            type=openapi.TYPE_STRING,
            maxLength=100,
            description='Nom de famille',
            example='Doe'
        ),
        'phone_number': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Numéro de téléphone',
            example='+1234567890'
        ),
        'date_of_birth': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE,
            description='Date de naissance',
            example='1990-01-01'
        ),
        'profile_image_url': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_URI,
            description='URL de la photo de profil',
            example='https://cdn.example.com/avatar.jpg'
        ),
        'cover_image_url': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_URI,
            description='URL de la bannière'
        ),
        'bio': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Biographie',
            example='Développeur passionné par l\'apprentissage'
        ),
        'website': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_URI,
            example='https://johndoe.com'
        ),
        'linkedin': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_URI,
            example='https://linkedin.com/in/johndoe'
        ),
        'github': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_URI,
            example='https://github.com/johndoe'
        ),
        'country': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Pays',
            example='USA'
        ),
        'city': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Ville',
            example='New York'
        ),
        'timezone': openapi.Schema(
            type=openapi.TYPE_STRING,
            default='UTC',
            description='Fuseau horaire',
            example='America/New_York'
        ),
        'language': openapi.Schema(
            type=openapi.TYPE_STRING,
            default='en',
            description='Langue préférée',
            example='en'
        ),
    }
)

profile_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        'user_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
        'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
        'date_of_birth': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        'profile_image_url': openapi.Schema(type=openapi.TYPE_STRING),
        'bio': openapi.Schema(type=openapi.TYPE_STRING),
        'country': openapi.Schema(type=openapi.TYPE_STRING),
        'city': openapi.Schema(type=openapi.TYPE_STRING),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
    }
)


# ==========================================
# STUDENT SCHEMAS
# ==========================================

student_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'preferred_categories': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
            description='Catégories de cours préférées',
            example=['Programming', 'Data Science', 'Web Development']
        ),
    }
)

student_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        'user_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        'student_code': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Code étudiant unique',
            example='STU2024123456'
        ),
        'points': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description='Points totaux',
            example=150
        ),
        'level': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description='Niveau actuel',
            example=2
        ),
        'experience_points': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description='Points d\'expérience',
            example=250
        ),
        'streak': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description='Série de jours consécutifs',
            example=5
        ),
        'max_streak': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description='Record de streak',
            example=10
        ),
        'total_courses_enrolled': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            example=3
        ),
        'total_courses_completed': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            example=1
        ),
        'preferred_categories': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING)
        ),
    }
)

add_experience_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['points'],
    properties={
        'points': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            minimum=1,
            description='Points d\'expérience à ajouter',
            example=150
        ),
    }
)


# ==========================================
# INSTRUCTOR SCHEMAS
# ==========================================

instructor_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'title': openapi.Schema(
            type=openapi.TYPE_STRING,
            maxLength=100,
            description='Titre professionnel',
            example='Senior Developer'
        ),
        'headline': openapi.Schema(
            type=openapi.TYPE_STRING,
            maxLength=255,
            description='Accroche courte',
            example='Expert in Python and Django'
        ),
        'specializations': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
            description='Spécialisations',
            example=['Python', 'Django', 'REST API']
        ),
        'expertise': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
            description='Domaines d\'expertise',
            example=['Backend Development', 'Database Design']
        ),
        'certifications': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
            description='Certifications',
            example=['AWS Certified', 'Python Expert']
        ),
        'years_of_experience': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            minimum=0,
            description='Années d\'expérience',
            example=5
        ),
        'hourly_rate': openapi.Schema(
            type=openapi.TYPE_NUMBER,
            format=openapi.FORMAT_FLOAT,
            minimum=0,
            description='Taux horaire en USD',
            example=50.00
        ),
    }
)

instructor_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        'user_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        'instructor_code': openapi.Schema(
            type=openapi.TYPE_STRING,
            example='INS2024123456'
        ),
        'title': openapi.Schema(type=openapi.TYPE_STRING),
        'headline': openapi.Schema(type=openapi.TYPE_STRING),
        'specializations': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING)
        ),
        'years_of_experience': openapi.Schema(type=openapi.TYPE_INTEGER),
        'hourly_rate': openapi.Schema(type=openapi.TYPE_NUMBER),
        'rating': openapi.Schema(
            type=openapi.TYPE_NUMBER,
            description='Note moyenne',
            example=4.5
        ),
        'total_reviews': openapi.Schema(type=openapi.TYPE_INTEGER),
        'total_students': openapi.Schema(type=openapi.TYPE_INTEGER),
        'total_courses': openapi.Schema(type=openapi.TYPE_INTEGER),
        'is_verified': openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description='Instructeur vérifié'
        ),
    }
)


# ==========================================
# COMMON PARAMETERS
# ==========================================

limit_param = openapi.Parameter(
    'limit',
    openapi.IN_QUERY,
    description="Nombre maximum de résultats",
    type=openapi.TYPE_INTEGER,
    default=10
)

user_id_param = openapi.Parameter(
    'user_id',
    openapi.IN_PATH,
    description="ID utilisateur (UUID)",
    type=openapi.TYPE_STRING,
    required=True
)


# ==========================================
# ERROR SCHEMAS
# ==========================================

error_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'error': openapi.Schema(type=openapi.TYPE_STRING)
    }
)

validation_error = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    additionalProperties=openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=openapi.Schema(type=openapi.TYPE_STRING)
    )
)


# ==========================================
# RESPONSES DICTIONARY
# ==========================================

standard_responses = {
    '200': openapi.Response('Succès', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
    '201': openapi.Response('Créé', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
    '400': openapi.Response('Requête invalide', schema=validation_error),
    '401': openapi.Response('Non authentifié', schema=error_response),
    '403': openapi.Response('Accès refusé', schema=error_response),
    '404': openapi.Response('Non trouvé', schema=error_response),
    '500': openapi.Response('Erreur serveur', schema=error_response),
}