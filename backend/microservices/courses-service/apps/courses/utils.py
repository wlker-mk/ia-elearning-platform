"""
Utilitaires partagés entre les modules du package courses.
"""

import asyncio
import logging
from typing import Coroutine, Any
from functools import wraps

logger = logging.getLogger(__name__)


def run_async(coro: Coroutine) -> Any:
    """
    Helper pour exécuter des coroutines asynchrones.
    Utilisé dans les views et tests.
    
    Args:
        coro: La coroutine à exécuter
    
    Returns:
        Le résultat de la coroutine
    
    Example:
        >>> service = CoursesService()
        >>> result = run_async(service.get_course_by_id(course_id))
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def async_action(func):
    """
    Décorateur pour simplifier l'exécution de méthodes asynchrones
    dans les ViewSets Django REST Framework.
    
    Example:
        @async_action
        def my_view(self, request):
            service = MyService()
            await service.connect()
            result = await service.do_something()
            await service.disconnect()
            return result
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return run_async(func(*args, **kwargs))
    return wrapper


class ServiceContextManager:
    """
    Context manager pour gérer automatiquement la connexion/déconnexion
    des services Prisma.
    
    Example:
        async with ServiceContextManager(CoursesService()) as service:
            course = await service.get_course_by_id(course_id)
    """
    
    def __init__(self, service):
        self.service = service
    
    async def __aenter__(self):
        await self.service.connect()
        return self.service
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.service.disconnect()
        if exc_type:
            logger.error(f"Error in service: {exc_val}")
        return False


def format_duration(seconds: int) -> str:
    """
    Formater une durée en secondes en format lisible.
    
    Args:
        seconds: Durée en secondes
    
    Returns:
        Durée formatée (ex: "2h 30m", "45m", "1h 15m 30s")
    
    Example:
        >>> format_duration(9000)
        '2h 30m'
    """
    if seconds < 60:
        return f"{seconds}s"
    
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    if minutes < 60:
        if remaining_seconds > 0:
            return f"{minutes}m {remaining_seconds}s"
        return f"{minutes}m"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if remaining_minutes > 0:
        if remaining_seconds > 0:
            return f"{hours}h {remaining_minutes}m {remaining_seconds}s"
        return f"{hours}h {remaining_minutes}m"
    return f"{hours}h"


def validate_uuid(value: str) -> bool:
    """
    Valider qu'une chaîne est un UUID valide.
    
    Args:
        value: La chaîne à valider
    
    Returns:
        True si valide, False sinon
    """
    import uuid
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError):
        return False


def get_client_ip(request) -> str:
    """
    Récupérer l'adresse IP du client depuis une requête Django.
    Gère les proxies et load balancers.
    
    Args:
        request: Objet HttpRequest de Django
    
    Returns:
        Adresse IP du client
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def paginate_queryset(items: list, page: int = 1, page_size: int = 20) -> dict:
    """
    Paginer une liste d'éléments.
    
    Args:
        items: Liste des éléments
        page: Numéro de page (commence à 1)
        page_size: Nombre d'éléments par page
    
    Returns:
        Dictionnaire avec les résultats paginés et métadonnées
    
    Example:
        >>> items = [1, 2, 3, 4, 5]
        >>> paginate_queryset(items, page=1, page_size=2)
        {
            'results': [1, 2],
            'total': 5,
            'page': 1,
            'page_size': 2,
            'total_pages': 3,
            'has_next': True,
            'has_previous': False
        }
    """
    total = len(items)
    total_pages = (total + page_size - 1) // page_size
    
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        'results': items[start:end],
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_previous': page > 1
    }


class ErrorMessages:
    """Messages d'erreur standardisés pour tous les modules."""
    
    # Génériques
    NOT_FOUND = "Resource not found"
    UNAUTHORIZED = "You are not authorized to perform this action"
    INVALID_DATA = "Invalid data provided"
    ALREADY_EXISTS = "Resource already exists"
    
    # Courses
    COURSE_NOT_FOUND = "Course not found"
    COURSE_ALREADY_PUBLISHED = "Course is already published"
    COURSE_NOT_PUBLISHED = "Course is not published yet"
    
    # Lessons
    LESSON_NOT_FOUND = "Lesson not found"
    LESSON_ACCESS_DENIED = "You don't have access to this lesson"
    LESSON_REQUIRES_ENROLLMENT = "This lesson requires course enrollment"
    
    # Certificates
    CERTIFICATE_NOT_FOUND = "Certificate not found"
    CERTIFICATE_ALREADY_ISSUED = "Certificate already issued for this course"
    CERTIFICATE_EXPIRED = "Certificate has expired"
    CERTIFICATE_REVOKED = "Certificate has been revoked"
    INVALID_CERTIFICATE_NUMBER = "Invalid certificate number"


class SuccessMessages:
    """Messages de succès standardisés pour tous les modules."""
    
    # Génériques
    CREATED = "Resource created successfully"
    UPDATED = "Resource updated successfully"
    DELETED = "Resource deleted successfully"
    
    # Courses
    COURSE_PUBLISHED = "Course published successfully"
    COURSE_UNPUBLISHED = "Course unpublished successfully"
    
    # Certificates
    CERTIFICATE_ISSUED = "Certificate issued successfully"
    CERTIFICATE_VERIFIED = "Certificate is valid"