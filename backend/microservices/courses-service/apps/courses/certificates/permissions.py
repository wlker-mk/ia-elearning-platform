# ========== permissions.py ==========
from rest_framework import permissions

class CanIssueCertificate(permissions.BasePermission):
    """Permission: peut émettre un certificat"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Seuls les instructeurs et admins peuvent émettre des certificats
        return getattr(request.user, 'role', None) in ['instructor', 'admin']

class CanAccessCertificate(permissions.BasePermission):
    """Permission: peut accéder à un certificat"""
    
    def has_object_permission(self, request, view, obj):
        # L'utilisateur propriétaire peut toujours accéder
        if obj.userId == str(request.user.id):
            return True
        
        # Les admins et instructeurs peuvent aussi accéder
        return getattr(request.user, 'role', None) in ['admin', 'instructor']

class CanManageTemplates(permissions.BasePermission):
    """Permission: peut gérer les templates"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Seuls les admins peuvent gérer les templates
        return getattr(request.user, 'role', None) == 'admin'