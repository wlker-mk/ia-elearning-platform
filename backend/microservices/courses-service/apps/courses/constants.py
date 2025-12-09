"""
Constantes partagées entre les modules du package courses.
"""

# ========== COURSE CONSTANTS ==========

COURSE_DIFFICULTIES = {
    'BEGINNER': 'beginner',
    'INTERMEDIATE': 'intermediate',
    'ADVANCED': 'advanced',
    'EXPERT': 'expert',
    'ALL_LEVELS': 'all_levels',
}

COURSE_TYPES = {
    'VIDEO_COURSE': 'video_course',
    'TEXT_BASED': 'text_based',
    'MIXED': 'mixed',
    'LIVE_CLASS': 'live_class',
    'WORKSHOP': 'workshop',
    'BOOTCAMP': 'bootcamp',
    'CERTIFICATION_PREP': 'certification_prep',
}

COURSE_LANGUAGES = {
    'ENGLISH': 'English',
    'FRENCH': 'Français',
    'SPANISH': 'Español',
    'GERMAN': 'Deutsch',
    'PORTUGUESE': 'Português',
    'CHINESE': '中文',
    'JAPANESE': '日本語',
    'ARABIC': 'العربية',
}

# ========== LESSON CONSTANTS ==========

RESOURCE_TYPES = {
    'PDF': 'PDF Document',
    'VIDEO': 'Video',
    'AUDIO': 'Audio',
    'ZIP': 'Archive (ZIP)',
    'DOCUMENT': 'Text Document',
    'CODE': 'Code File',
    'LINK': 'External Link',
    'IMAGE': 'Image',
}

VIDEO_FORMATS = [
    '.mp4', '.avi', '.mov', '.wmv', '.flv', 
    '.mkv', '.webm', '.m4v'
]

DOCUMENT_FORMATS = [
    '.pdf', '.doc', '.docx', '.txt', '.rtf',
    '.odt', '.pages'
]

AUDIO_FORMATS = [
    '.mp3', '.wav', '.aac', '.flac', '.m4a',
    '.ogg', '.wma'
]

IMAGE_FORMATS = [
    '.jpg', '.jpeg', '.png', '.gif', '.svg',
    '.webp', '.bmp'
]

# ========== CERTIFICATE CONSTANTS ==========

CERTIFICATE_GRADES = {
    'A+': 'Excellent (97-100%)',
    'A': 'Excellent (93-96%)',
    'A-': 'Excellent (90-92%)',
    'B+': 'Good (87-89%)',
    'B': 'Good (83-86%)',
    'B-': 'Good (80-82%)',
    'C+': 'Satisfactory (77-79%)',
    'C': 'Satisfactory (73-76%)',
    'C-': 'Satisfactory (70-72%)',
    'PASS': 'Pass',
    'MERIT': 'Merit',
    'DISTINCTION': 'Distinction',
}

CERTIFICATE_EXPIRY_DAYS = {
    'NEVER': None,
    'ONE_YEAR': 365,
    'TWO_YEARS': 730,
    'THREE_YEARS': 1095,
    'FIVE_YEARS': 1825,
}

# ========== PAGINATION CONSTANTS ==========

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# ========== FILE SIZE LIMITS (en bytes) ==========

MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500 MB
MAX_DOCUMENT_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_AUDIO_SIZE = 100 * 1024 * 1024  # 100 MB

# ========== DURATION CONSTANTS (en secondes) ==========

MIN_LESSON_DURATION = 60  # 1 minute
MAX_LESSON_DURATION = 7200  # 2 heures
AVERAGE_LESSON_DURATION = 600  # 10 minutes

MIN_COURSE_DURATION = 1800  # 30 minutes
MAX_COURSE_DURATION = 360000  # 100 heures

# ========== RATING CONSTANTS ==========

MIN_RATING = 0.0
MAX_RATING = 5.0
DEFAULT_RATING = 0.0

# ========== CACHE KEYS ==========

CACHE_KEYS = {
    'COURSE_DETAIL': 'course:detail:{course_id}',
    'COURSE_LIST': 'course:list:{page}:{filters_hash}',
    'POPULAR_COURSES': 'course:popular',
    'TRENDING_COURSES': 'course:trending',
    'CATEGORY_COURSES': 'course:category:{category_id}',
    'INSTRUCTOR_COURSES': 'course:instructor:{instructor_id}',
    'USER_CERTIFICATES': 'certificate:user:{user_id}',
    'COURSE_CERTIFICATE_COUNT': 'certificate:course:{course_id}:count',
}

# ========== CACHE TTL (en secondes) ==========

CACHE_TTL = {
    'SHORT': 300,  # 5 minutes
    'MEDIUM': 1800,  # 30 minutes
    'LONG': 3600,  # 1 heure
    'VERY_LONG': 86400,  # 24 heures
}

# ========== EVENT TYPES ==========

EVENT_TYPES = {
    # Course events
    'COURSE_CREATED': 'course.created',
    'COURSE_UPDATED': 'course.updated',
    'COURSE_DELETED': 'course.deleted',
    'COURSE_PUBLISHED': 'course.published',
    'COURSE_UNPUBLISHED': 'course.unpublished',
    
    # Lesson events
    'LESSON_CREATED': 'lesson.created',
    'LESSON_UPDATED': 'lesson.updated',
    'LESSON_DELETED': 'lesson.deleted',
    
    # Certificate events
    'CERTIFICATE_ISSUED': 'certificate.issued',
    'CERTIFICATE_VERIFIED': 'certificate.verified',
    'CERTIFICATE_REVOKED': 'certificate.revoked',
    'CERTIFICATE_READY': 'certificate.ready',
    
    # External events (listened to)
    'ENROLLMENT_CREATED': 'enrollment.created',
    'ENROLLMENT_DROPPED': 'enrollment.dropped',
    'COURSE_COMPLETED': 'course.completed',
    'REVIEW_CREATED': 'review.created',
}

# ========== RABBITMQ EXCHANGES ==========

RABBITMQ_EXCHANGES = {
    'COURSES_EVENTS': 'courses_events',
    'PLATFORM_EVENTS': 'platform_events',
}

# ========== STATUS CODES ==========

HTTP_STATUS_MESSAGES = {
    200: 'OK',
    201: 'Created',
    204: 'No Content',
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    409: 'Conflict',
    422: 'Unprocessable Entity',
    500: 'Internal Server Error',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
}

# ========== REGEX PATTERNS ==========

PATTERNS = {
    'SLUG': r'^[a-z0-9-]+$',
    'UUID': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    'CERTIFICATE_NUMBER': r'^CERT-\d{6}-[A-Z0-9]{10}$',
    'VIDEO_URL': r'^https?://.+\.(mp4|avi|mov|webm)$',
}