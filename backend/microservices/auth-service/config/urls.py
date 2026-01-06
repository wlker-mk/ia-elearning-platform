from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Schema view pour Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="🔐 Auth Service API",
        default_version='v1',
        description="""
# Auth Service - API Documentation

Service d'authentification et d'autorisation pour la plateforme LMS.

## 🚀 Fonctionnalités Principales

### 🔑 Authentification
- **Inscription** avec validation email
- **Connexion** avec sessions sécurisées
- **OAuth** (Google, GitHub)
- **MFA** avec TOTP et codes de backup
- **Réinitialisation** de mot de passe

### 🛡️ Sécurité
- Hash bcrypt (12 rounds)
- Politique de mot de passe stricte
- Verrouillage après 5 tentatives
- IP tracking et géolocalisation
- Alertes de sécurité

### 📊 Gestion
- Sessions multiples
- Historique de connexion
- Statistiques d'utilisation

## 🔒 Authentification API

Pour accéder aux endpoints protégés:

```http
Authorization: Bearer <votre_access_token>
```

## 📝 Workflow Typique

### 1. Inscription
```
POST /api/auth/register/
```

### 2. Vérification Email
```
POST /api/auth/verify-email/
```

### 3. Connexion
```
POST /api/auth/login/
```

### 4. Activation MFA (optionnel)
```
POST /api/auth/mfa/enable/
POST /api/auth/mfa/verify/
```

## 🌐 Environnements

| Env | URL | Swagger |
|-----|-----|---------|
| Production | https://api.lms.com | [Docs](https://api.lms.com/swagger/) |
| Staging | https://staging-api.lms.com | [Docs](https://staging-api.lms.com/swagger/) |
| Development | http://localhost:8001 | [Docs](http://localhost:8001/swagger/) |

## 📞 Support

- Email: support@lms-platform.com
- Documentation: https://docs.lms-platform.com
- Status: https://status.lms-platform.com
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

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ==========================================
    # API ENDPOINTS
    # ==========================================
    path('api/auth/', include('apps.authentication.urls')),
    
    # ==========================================
    # API DOCUMENTATION
    # ==========================================
    # Swagger UI
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    
    # ReDoc UI (alternative)
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
    
    # ==========================================
    # API ROOT (info endpoint)
    # ==========================================
    path('', lambda request: {
        'service': 'auth-service',
        'version': 'v1',
        'status': 'running',
        'documentation': {
            'swagger': '/swagger/',
            'redoc': '/redoc/',
            'openapi_json': '/swagger.json'
        },
        'endpoints': {
            'health': '/api/auth/health/',
            'register': '/api/auth/register/',
            'login': '/api/auth/login/',
            'docs': '/swagger/'
        }
    }),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)