from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response = {
            'success': False,
            'error': {
                'message': str(exc),
                'type': exc.__class__.__name__,
            }
        }
        
        if hasattr(exc, 'detail'):
            custom_response['error']['details'] = exc.detail
        
        response.data = custom_response
    else:
        # Log unhandled exceptions
        logger.error(f'Unhandled exception: {exc}', exc_info=True)
        
        response = Response(
            {
                'success': False,
                'error': {
                    'message': 'An unexpected error occurred',
                    'type': 'InternalServerError',
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response


class ServiceException(Exception):
    """Base exception for service errors"""
    pass


class EnrollmentException(ServiceException):
    """Exception for enrollment-related errors"""
    pass


class ProgressException(ServiceException):
    """Exception for progress-related errors"""
    pass


class CertificateException(ServiceException):
    """Exception for certificate-related errors"""
    pass