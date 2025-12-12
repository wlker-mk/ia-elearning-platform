from enum import Enum


class EnrollmentStatus(str, Enum):
    ACTIVE = 'ACTIVE'
    COMPLETED = 'COMPLETED'
    SUSPENDED = 'SUSPENDED'
    EXPIRED = 'EXPIRED'
    CANCELLED = 'CANCELLED'
    IN_PROGRESS = 'IN_PROGRESS'
    PAUSED = 'PAUSED'


class NoteType(str, Enum):
    TEXT = 'TEXT'
    HIGHLIGHT = 'HIGHLIGHT'
    QUESTION = 'QUESTION'


class BookmarkType(str, Enum):
    LESSON = 'LESSON'
    TIMESTAMP = 'TIMESTAMP'
    RESOURCE = 'RESOURCE'


# Certificate Settings
CERTIFICATE_EXPIRY_DAYS = 365 * 5  # 5 years
CERTIFICATE_NUMBER_PREFIX = 'CERT'
CERTIFICATE_VERIFICATION_CODE_LENGTH = 12

# Progress Settings
MIN_COMPLETION_PERCENTAGE = 80  # Minimum percentage to mark as completed
MIN_VIDEO_WATCH_PERCENTAGE = 90  # Minimum video watch percentage

# Study Session Settings
INACTIVE_SESSION_TIMEOUT = 30  # minutes
MAX_DAILY_STUDY_HOURS = 12

# Grade Mapping
GRADE_MAPPING = {
    (90, 100): 'A+',
    (85, 89): 'A',
    (80, 84): 'B+',
    (75, 79): 'B',
    (70, 74): 'C+',
    (65, 69): 'C',
    (60, 64): 'D',
    (0, 59): 'F',
}