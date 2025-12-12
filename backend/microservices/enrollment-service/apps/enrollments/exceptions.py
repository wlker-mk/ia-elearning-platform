from rest_framework.exceptions import APIException
from rest_framework import status


class EnrollmentAlreadyExists(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Student is already enrolled in this course'
    default_code = 'enrollment_exists'


class EnrollmentNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Enrollment not found'
    default_code = 'enrollment_not_found'


class EnrollmentExpired(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Enrollment has expired'
    default_code = 'enrollment_expired'


class EnrollmentSuspended(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Enrollment has been suspended'
    default_code = 'enrollment_suspended'


class ProgressNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Progress record not found'
    default_code = 'progress_not_found'


class CertificateNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Certificate not found'
    default_code = 'certificate_not_found'


class CertificateAlreadyIssued(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Certificate has already been issued for this enrollment'
    default_code = 'certificate_exists'


class InsufficientProgress(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Insufficient progress to complete the course'
    default_code = 'insufficient_progress'


class InvalidVerificationCode(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid verification code'
    default_code = 'invalid_verification_code'


class NoteNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Note not found'
    default_code = 'note_not_found'


class BookmarkNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Bookmark not found'
    default_code = 'bookmark_not_found'