from rest_framework import permissions

class IsInstructor(permissions.BasePermission):
    """Permission: l'utilisateur doit être instructeur"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user, 'role', None) == 'instructor'
        )

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permission: propriétaire pour modifications, lecture pour tous"""
    
    def has_object_permission(self, request, view, obj):
        # Lecture autorisée pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Écriture uniquement pour le propriétaire
        return obj.instructorId == str(request.user.id)

class IsCourseInstructor(permissions.BasePermission):
    """Permission: l'utilisateur doit être l'instructeur du cours"""
    
    def has_permission(self, request, view):
        # Nécessite d'être authentifié et instructeur
        if not request.user or not request.user.is_authenticated:
            return False
        
        return getattr(request.user, 'role', None) == 'instructor'
    
    def has_object_permission(self, request, view, obj):
        # Vérifier que l'utilisateur est l'instructeur du cours
        # obj peut être un cours, section, leçon, etc.
        if hasattr(obj, 'instructorId'):
            return obj.instructorId == str(request.user.id)
        elif hasattr(obj, 'course'):
            return obj.course.instructorId == str(request.user.id)
        elif hasattr(obj, 'section'):
            return obj.section.course.instructorId == str(request.user.id)
        
        return False

class IsAdminOrInstructor(permissions.BasePermission):
    """Permission: administrateur ou instructeur"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_role = getattr(request.user, 'role', None)
        return user_role in ['admin', 'instructor']

class CanPublishCourse(permissions.BasePermission):
    """Permission: peut publier un cours (instructeur vérifié ou admin)"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_role = getattr(request.user, 'role', None)
        if user_role == 'admin':
            return True
        
        if user_role == 'instructor':
            # Vérifier si l'instructeur est vérifié
            return getattr(request.user, 'is_verified', False)
        
        return False

class CanManageCategories(permissions.BasePermission):
    """Permission: peut gérer les catégories (admin uniquement)"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user or not request.user.is_authenticated:
            return False
        
        return getattr(request.user, 'role', None) == 'admin'