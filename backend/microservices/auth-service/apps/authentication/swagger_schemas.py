from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# ==========================================
# SCHEMA VIEW CONFIGURATION
# ==========================================

schema_view = get_schema_view(
    openapi.Info(
        title="Auth Service API",
        default_version='v1',
        description="""
# 🔐 Auth Service API Documentation

Service d'authentification et d'autorisation complet pour la plateforme LMS.

## 🚀 Fonctionnalités

### Authentification
- Inscription avec validation email
- Connexion avec session tokens
- MFA (Multi-Factor Authentication) avec TOTP
- OAuth (Google, GitHub)
- Réinitialisation de mot de passe
- Gestion des sessions multiples

### Sécurité
- Hash de mots de passe avec bcrypt
- Politique de mots de passe stricte
- Verrouillage de compte après tentatives échouées
- IP tracking et détection de localisation
- Alertes de sécurité

### Sessions
- Tokens JWT personnalisés
- Refresh tokens avec rotation
- Gestion multi-appareils
- Révocation de sessions

## 🔒 Authentification

Pour les endpoints protégés, incluez le header:
```
Authorization: Bearer <access_token>
```

## 📊 Codes de Statut

- `200` - Succès
- `201` - Créé avec succès
- `400` - Requête invalide
- `401` - Non authentifié
- `403` - Accès refusé (compte suspendu, email non vérifié)
- `404` - Ressource non trouvée
- `409` - Conflit (email déjà utilisé)
- `423` - Compte verrouillé
- `428` - MFA requis
- `500` - Erreur serveur

## 🌐 Environnements

- **Production**: `https://api.lms-platform.com`
- **Staging**: `https://staging-api.lms-platform.com`
- **Development**: `http://localhost:8001`
        """,
        terms_of_service="https://www.lms-platform.com/terms/",
        contact=openapi.Contact(
            name="LMS Platform Support",
            email="support@lms-platform.com",
            url="https://www.lms-platform.com/support"
        ),
        license=openapi.License(
            name="MIT License",
            url="https://opensource.org/licenses/MIT"
        ),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    patterns=[],
)


# ==========================================
# COMMON PARAMETERS
# ==========================================

bearer_token_param = openapi.Parameter(
    'Authorization',
    openapi.IN_HEADER,
    description="Bearer token pour l'authentification: Bearer <token>",
    type=openapi.TYPE_STRING,
    required=True,
)


# ==========================================
# AUTHENTICATION SCHEMAS
# ==========================================

register_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'username', 'password', 'password_confirm'],
    properties={
        'email': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_EMAIL,
            description='Adresse email unique',
            example='user@example.com'
        ),
        'username': openapi.Schema(
            type=openapi.TYPE_STRING,
            minLength=3,
            maxLength=50,
            description='Nom d\'utilisateur unique (3-50 caractères)',
            example='johndoe'
        ),
        'password': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_PASSWORD,
            minLength=8,
            description='Mot de passe (min 8 caractères, majuscules, minuscules, chiffres, caractères spéciaux)',
            example='SecurePass123!'
        ),
        'password_confirm': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_PASSWORD,
            description='Confirmation du mot de passe',
            example='SecurePass123!'
        ),
        'role': openapi.Schema(
            type=openapi.TYPE_STRING,
            enum=['STUDENT', 'INSTRUCTOR'],
            default='STUDENT',
            description='Rôle de l\'utilisateur'
        ),
    }
)

register_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'user': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'role': openapi.Schema(type=openapi.TYPE_STRING),
                'is_email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'mfa_enabled': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
            }
        ),
        'message': openapi.Schema(
            type=openapi.TYPE_STRING,
            example='Registration successful. Please verify your email.'
        ),
    }
)

login_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'password'],
    properties={
        'email': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_EMAIL,
            example='user@example.com'
        ),
        'password': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_PASSWORD,
            example='SecurePass123!'
        ),
        'remember_me': openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            default=False,
            description='Prolonger la durée de session'
        ),
    }
)

login_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'user': openapi.Schema(type=openapi.TYPE_OBJECT),
        'access_token': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Token d\'accès JWT'
        ),
        'refresh_token': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Token de rafraîchissement'
        ),
        'expires_at': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATETIME,
            description='Date d\'expiration du token'
        ),
        'message': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

mfa_required_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'requires_mfa': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
        'user_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        'message': openapi.Schema(type=openapi.TYPE_STRING, example='MFA code required'),
    }
)


# ==========================================
# MFA SCHEMAS
# ==========================================

enable_mfa_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'secret': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Secret TOTP (à sauvegarder)',
            example='JBSWY3DPEHPK3PXP'
        ),
        'qr_code': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='QR code en base64 pour Google Authenticator',
            example='data:image/png;base64,iVBORw0KGgoAAAANS...'
        ),
        'backup_codes': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
            description='Codes de secours à usage unique',
            example=['1234-5678', '8765-4321', '5555-6666']
        ),
        'message': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

verify_mfa_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['code'],
    properties={
        'code': openapi.Schema(
            type=openapi.TYPE_STRING,
            minLength=6,
            maxLength=6,
            description='Code TOTP à 6 chiffres',
            example='123456'
        ),
    }
)


# ==========================================
# OAUTH SCHEMAS
# ==========================================

google_oauth_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['code', 'redirect_uri'],
    properties={
        'code': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Code d\'autorisation Google',
            example='4/0AX4XfWh...'
        ),
        'redirect_uri': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_URI,
            description='URI de redirection (doit correspondre à la config OAuth)',
            example='http://localhost:3000/auth/google/callback'
        ),
    }
)

github_oauth_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['code'],
    properties={
        'code': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Code d\'autorisation GitHub',
            example='abc123def456'
        ),
    }
)

oauth_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'user': openapi.Schema(type=openapi.TYPE_OBJECT),
        'access_token': openapi.Schema(type=openapi.TYPE_STRING),
        'refresh_token': openapi.Schema(type=openapi.TYPE_STRING),
        'expires_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'is_new_user': openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description='True si c\'est un nouveau compte créé'
        ),
        'message': openapi.Schema(type=openapi.TYPE_STRING),
    }
)


# ==========================================
# SESSION SCHEMAS
# ==========================================

session_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        'token': openapi.Schema(type=openapi.TYPE_STRING),
        'expires_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'ip_address': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_IPV4),
        'device': openapi.Schema(type=openapi.TYPE_STRING, example='Desktop'),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
    }
)


# ==========================================
# ERROR SCHEMAS
# ==========================================

error_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'error': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Message d\'erreur'
        ),
    }
)

validation_error_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'field_name': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
            description='Messages d\'erreur pour ce champ'
        ),
    }
)


# ==========================================
# RESPONSES DICTIONARY
# ==========================================

responses_dict = {
    '200': openapi.Response(
        description='Succès',
        schema=openapi.Schema(type=openapi.TYPE_OBJECT)
    ),
    '201': openapi.Response(
        description='Créé avec succès',
        schema=openapi.Schema(type=openapi.TYPE_OBJECT)
    ),
    '400': openapi.Response(
        description='Requête invalide',
        schema=validation_error_response
    ),
    '401': openapi.Response(
        description='Non authentifié',
        schema=error_response
    ),
    '403': openapi.Response(
        description='Accès refusé',
        schema=error_response
    ),
    '404': openapi.Response(
        description='Ressource non trouvée',
        schema=error_response
    ),
    '409': openapi.Response(
        description='Conflit (ressource déjà existante)',
        schema=error_response
    ),
    '423': openapi.Response(
        description='Compte verrouillé',
        schema=error_response
    ),
    '428': openapi.Response(
        description='MFA requis',
        schema=mfa_required_response
    ),
    '500': openapi.Response(
        description='Erreur serveur',
        schema=error_response
    ),
}