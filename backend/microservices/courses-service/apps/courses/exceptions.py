"""
Exceptions personnalisées pour le package courses.
"""

from rest_framework.exceptions import APIException
from rest_framework import status


class CoursesBaseException(APIException):
    """Exception de base pour tous les modules du package courses."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'An error occurred in the courses service.'
    default_code = 'courses_error'


# ========== COURSES EXCEPTIONS ==========

class CourseNotFoundException(CoursesBaseException):
    """Exception levée quand un cours n'est pas trouvé."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Course not found.'
    default_code = 'course_not_found'


class CourseAlreadyPublishedException(CoursesBaseException):
    """Exception levée quand on tente de publier un cours déjà publié."""
    default_detail = 'Course is already published.'
    default_code = 'course_already_published'


class CourseNotPublishedException(CoursesBaseException):
    """Exception levée quand on tente d'accéder à un cours non publié."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Course is not published yet.'
    default_code = 'course_not_published'


class InvalidCourseDataException(CoursesBaseException):
    """Exception levée quand les données du cours sont invalides."""
    default_detail = 'Invalid course data.'
    default_code = 'invalid_course_data'


class SectionNotFoundException(CoursesBaseException):
    """Exception levée quand une section n'est pas trouvée."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Section not found.'
    default_code = 'section_not_found'


class CategoryNotFoundException(CoursesBaseException):
    """Exception levée quand une catégorie n'est pas trouvée."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Category not found.'
    default_code = 'category_not_found'


# ========== LESSONS EXCEPTIONS ==========

class LessonNotFoundException(CoursesBaseException):
    """Exception levée quand une leçon n'est pas trouvée."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Lesson not found.'
    default_code = 'lesson_not_found'


class LessonAccessDeniedException(CoursesBaseException):
    """Exception levée quand l'accès à une leçon est refusé."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have access to this lesson.'
    default_code = 'lesson_access_denied'


class LessonRequiresEnrollmentException(CoursesBaseException):
    """Exception levée quand une leçon nécessite une inscription."""
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'This lesson requires course enrollment.'
    default_code = 'lesson_requires_enrollment'


class ResourceNotFoundException(CoursesBaseException):
    """Exception levée quand une ressource n'est pas trouvée."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found.'
    default_code = 'resource_not_found'


class InvalidVideoFormatException(CoursesBaseException):
    """Exception levée quand le format vidéo est invalide."""
    default_detail = 'Invalid video format.'
    default_code = 'invalid_video_format'


# ========== CERTIFICATES EXCEPTIONS ==========

class CertificateNotFoundException(CoursesBaseException):
    """Exception levée quand un certificat n'est pas trouvé."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Certificate not found.'
    default_code = 'certificate_not_found'


class CertificateAlreadyIssuedException(CoursesBaseException):
    """Exception levée quand un certificat existe déjà."""
    default_detail = 'Certificate already issued for this course.'
    default_code = 'certificate_already_issued'


class CertificateExpiredException(CoursesBaseException):
    """Exception levée quand un certificat a expiré."""
    status_code = status.HTTP_410_GONE
    default_detail = 'Certificate has expired.'
    default_code = 'certificate_expired'


class CertificateRevokedException(CoursesBaseException):
    """Exception levée quand un certificat a été révoqué."""
    status_code = status.HTTP_410_GONE
    default_detail = 'Certificate has been revoked.'
    default_code = 'certificate_revoked'


class InvalidCertificateNumberException(CoursesBaseException):
    """Exception levée quand le numéro de certificat est invalide."""
    default_detail = 'Invalid certificate number.'
    default_code = 'invalid_certificate_number'


class TemplateNotFoundException(CoursesBaseException):
    """Exception levée quand un template n'est pas trouvé."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Certificate template not found.'
    default_code = 'template_not_found'


class DefaultTemplateException(CoursesBaseException):
    """Exception levée lors d'opération invalide sur template par défaut."""
    default_detail = 'Cannot perform this action on default template.'
    default_code = 'default_template_error'


class PDFGenerationException(CoursesBaseException):
    """Exception levée quand la génération du PDF échoue."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Failed to generate certificate PDF.'
    default_code = 'pdf_generation_failed'


# ========== PERMISSIONS EXCEPTIONS ==========

class InsufficientPermissionsException(CoursesBaseException):
    """Exception levée quand l'utilisateur n'a pas les permissions."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'insufficient_permissions'


class NotCourseInstructorException(CoursesBaseException):
    """Exception levée quand l'utilisateur n'est pas l'instructeur du cours."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You are not the instructor of this course.'
    default_code = 'not_course_instructor'


# ========== SERVICE EXCEPTIONS ==========

class ServiceConnectionException(CoursesBaseException):
    """Exception levée quand la connexion au service échoue."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable.'
    default_code = 'service_unavailable'


class ExternalServiceException(CoursesBaseException):
    """Exception levée quand un service externe échoue."""
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = 'External service error.'
    default_code = 'external_service_error'


# ========== VALIDATION EXCEPTIONS ==========

class ValidationException(CoursesBaseException):
    """Exception levée pour les erreurs de validation."""
    default_detail = 'Validation error.'
    default_code = 'validation_error'
    
    def __init__(self, errors: dict = None, detail: str = None):
        """
        Args:
            errors: Dictionnaire des erreurs de validation par champ
            detail: Message d'erreur global
        """
        if errors:
            super().__init__(detail={'errors': errors})
        else:
            super().__init__(detail=detail)