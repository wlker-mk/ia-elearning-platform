import uuid
import string
import random
from datetime import datetime, timedelta
from django.conf import settings
import requests
from .constants import CERTIFICATE_NUMBER_PREFIX, CERTIFICATE_VERIFICATION_CODE_LENGTH, GRADE_MAPPING


def generate_certificate_number():
    """Generate unique certificate number"""
    timestamp = datetime.now().strftime('%Y%m%d')
    random_part = ''.join(random.choices(string.digits, k=6))
    return f"{CERTIFICATE_NUMBER_PREFIX}-{timestamp}-{random_part}"


def generate_verification_code():
    """Generate verification code for certificate"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=CERTIFICATE_VERIFICATION_CODE_LENGTH))


def calculate_grade(score):
    """Calculate letter grade from score"""
    for (min_score, max_score), grade in GRADE_MAPPING.items():
        if min_score <= score <= max_score:
            return grade
    return 'F'


def calculate_course_progress(enrollment_id):
    """Calculate overall course progress based on completed lessons"""
    from prisma import Prisma
    
    db = Prisma()
    db.connect()
    
    try:
        # Get all progress records for this enrollment
        progress_records = db.progress.find_many(
            where={'enrollmentId': enrollment_id}
        )
        
        if not progress_records:
            return 0.0
        
        # Calculate average completion percentage
        total_percentage = sum(p.percentage for p in progress_records)
        average_percentage = total_percentage / len(progress_records)
        
        return round(average_percentage, 2)
    finally:
        db.disconnect()


def fetch_course_details(course_id):
    """Fetch course details from courses service"""
    try:
        response = requests.get(
            f"{settings.COURSES_SERVICE_URL}/api/v1/courses/{course_id}/",
            timeout=5
        )
        response.raise_for_status()
        return response.json().get('data')
    except requests.RequestException as e:
        print(f"Error fetching course details: {e}")
        return None


def fetch_user_details(user_id):
    """Fetch user details from users service"""
    try:
        response = requests.get(
            f"{settings.USERS_SERVICE_URL}/api/v1/users/{user_id}/",
            timeout=5
        )
        response.raise_for_status()
        return response.json().get('data')
    except requests.RequestException as e:
        print(f"Error fetching user details: {e}")
        return None


def check_enrollment_validity(enrollment):
    """Check if enrollment is valid and active"""
    if enrollment.status == 'EXPIRED':
        return False, 'Enrollment has expired'
    
    if enrollment.status == 'SUSPENDED':
        return False, 'Enrollment is suspended'
    
    if enrollment.status == 'CANCELLED':
        return False, 'Enrollment has been cancelled'
    
    if enrollment.expiresAt and enrollment.expiresAt < datetime.now():
        return False, 'Enrollment has expired'
    
    return True, None


def format_duration(seconds):
    """Format duration in seconds to human-readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def is_course_completed(enrollment_id):
    """Check if course is completed based on progress"""
    from prisma import Prisma
    from .constants import MIN_COMPLETION_PERCENTAGE
    
    db = Prisma()
    db.connect()
    
    try:
        progress = calculate_course_progress(enrollment_id)
        return progress >= MIN_COMPLETION_PERCENTAGE
    finally:
        db.disconnect()