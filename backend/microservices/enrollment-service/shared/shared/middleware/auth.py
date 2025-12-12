import jwt
from django.conf import settings
from django.http import JsonResponse


class JWTAuthenticationMiddleware:
    """
    Middleware pour authentifier les requêtes avec JWT
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_paths = [
            '/admin/',
            '/api/schema/',
            '/api/docs/',
            '/health/',
            '/static/',
            '/media/',
        ]
    
    def __call__(self, request):
        # Skip authentication for exempt paths
        if any(request.path.startswith(path) for path in self.exempt_paths):
            return self.get_response(request)
        
        # Get token from header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            request.user_data = None
            return self.get_response(request)
        
        token = auth_header.split(' ')[1]
        
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Attach user data to request
            request.user_data = payload
            request.user_id = payload.get('user_id')
            request.user_role = payload.get('role')
            
        except jwt.ExpiredSignatureError:
            return JsonResponse(
                {'error': 'Token has expired'},
                status=401
            )
        except jwt.InvalidTokenError:
            return JsonResponse(
                {'error': 'Invalid token'},
                status=401
            )
        
        return self.get_response(request)