from rest_framework import permissions

class CanAccessLesson(permissions.BasePermission):
    """
    Permission: peut accéder à une leçon
    - Leçons gratuites: tout le monde
    - Leçons payantes: utilisateurs inscrits au cours
    """
    
    def has_object_permission(self, request, view, obj):
        # Les leçons gratuites sont accessibles à tous
        if obj.isFree:
            return True
        
        # Pour les leçons payantes, vérifier l'inscription
        # Cette vérification devrait être faite avec enrollments-service
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Ici on devrait faire un appel API à enrollments-service
        # pour vérifier si l'utilisateur est inscrit au cours
        # Pour l'instant, on suppose que c'est géré par la view
        
        return True

class CanModifyLesson(permissions.BasePermission):
    """
    Permission: peut modifier une leçon
    - Instructeur du cours uniquement
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user or not request.user.is_authenticated:
            return False
        
        return getattr(request.user, 'role', None) == 'instructor'
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Vérifier que l'utilisateur est l'instructeur du cours
        # obj est une Lesson, on doit remonter jusqu'au cours
        # lesson -> section -> course -> instructorId
        
        if hasattr(obj, 'section'):
            if hasattr(obj.section, 'course'):
                return obj.section.course.instructorId == str(request.user.id)
        
        return False

class CanDownloadResource(permissions.BasePermission):
    """
    Permission: peut télécharger une ressource
    - Leçons gratuites: tout le monde
    - Leçons payantes: utilisateurs inscrits
    """
    
    def has_object_permission(self, request, view, obj):
        # obj est une Resource
        if not obj.isDownloadable:
            return False
        
        # Vérifier si la leçon parente est gratuite
        if hasattr(obj, 'lesson') and obj.lesson.isFree:
            return True
        
        # Sinon, nécessite une inscription
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Vérification avec enrollments-service
        return True