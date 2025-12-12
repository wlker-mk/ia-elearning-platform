from celery import shared_task
from prisma import Prisma
from datetime import datetime
import logging
from apps.enrollments.utils import (
    generate_certificate_number,
    generate_verification_code,
    calculate_grade,
    fetch_course_details,
    fetch_user_details
)

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_certificate_task(self, enrollment_id: str):
    """
    Generate certificate for completed enrollment
    """
    db = Prisma()
    db.connect()
    
    try:
        # Get enrollment
        enrollment = db.enrollment.find_unique(
            where={'id': enrollment_id}
        )
        
        if not enrollment:
            logger.error(f"Enrollment {enrollment_id} not found")
            return
        
        if enrollment.certificateIssued:
            logger.info(f"Certificate already issued for enrollment {enrollment_id}")
            return
        
        # Get course and user details
        course = fetch_course_details(enrollment.courseId)
        user = fetch_user_details(enrollment.studentId)
        
        if not course or not user:
            logger.error(f"Could not fetch course or user details")
            raise Exception("Missing course or user data")
        
        # Calculate average score from progress
        progress_records = db.progress.find_many(
            where={'enrollmentId': enrollment_id}
        )
        
        scores = [p.quizScore for p in progress_records if p.quizScore]
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Generate certificate
        certificate = db.certificate.create(
            data={
                'studentId': enrollment.studentId,
                'courseId': enrollment.courseId,
                'enrollmentId': enrollment_id,
                'certificateNumber': generate_certificate_number(),
                'verificationCode': generate_verification_code(),
                'studentName': f"{user.get('firstName', '')} {user.get('lastName', '')}",
                'studentEmail': user.get('email', ''),
                'courseTitle': course.get('title', ''),
                'completionDate': enrollment.completedAt or datetime.now(),
                'score': round(average_score, 2),
                'grade': calculate_grade(average_score),
                'isValid': True
            }
        )
        
        # Update enrollment
        db.enrollment.update(
            where={'id': enrollment_id},
            data={
                'certificateIssued': True,
                'certificateId': certificate.id
            }
        )
        
        logger.info(f"Certificate {certificate.id} generated for enrollment {enrollment_id}")
        
        # Send email notification (optional)
        send_certificate_email_task.delay(certificate.id)
        
    except Exception as e:
        logger.error(f"Error generating certificate: {e}")
        raise self.retry(exc=e, countdown=60)
    finally:
        db.disconnect()


@shared_task
def send_certificate_email_task(certificate_id: str):
    """
    Send certificate email to student
    """
    db = Prisma()
    db.connect()
    
    try:
        certificate = db.certificate.find_unique(where={'id': certificate_id})
        
        if not certificate:
            return
        
        # TODO: Implement email sending
        logger.info(f"Certificate email sent to {certificate.studentEmail}")
        
    finally:
        db.disconnect()


@shared_task
def update_enrollment_statuses():
    """
    Update enrollment statuses based on expiration dates
    """
    db = Prisma()
    db.connect()
    
    try:
        # Find expired enrollments
        enrollments = db.enrollment.find_many(
            where={
                'expiresAt': {'lt': datetime.now()},
                'status': {'in': ['ACTIVE', 'IN_PROGRESS']}
            }
        )
        
        count = 0
        for enrollment in enrollments:
            db.enrollment.update(
                where={'id': enrollment.id},
                data={'status': 'EXPIRED'}
            )
            count += 1
        
        logger.info(f"Updated {count} expired enrollments")
        
    finally:
        db.disconnect()


@shared_task
def sync_enrollment_progress():
    """
    Sync enrollment progress from progress records
    """
    db = Prisma()
    db.connect()
    
    try:
        enrollments = db.enrollment.find_many(
            where={'status': {'in': ['ACTIVE', 'IN_PROGRESS']}}
        )
        
        for enrollment in enrollments:
            # Get progress records
            progress_records = db.progress.find_many(
                where={'enrollmentId': enrollment.id}
            )
            
            if not progress_records:
                continue
            
            # Calculate overall progress
            total_percentage = sum(p.percentage for p in progress_records)
            average_progress = total_percentage / len(progress_records)
            
            # Update enrollment
            db.enrollment.update(
                where={'id': enrollment.id},
                data={'progress': round(average_progress, 2)}
            )
        
        logger.info(f"Synced progress for {len(enrollments)} enrollments")
        
    finally:
        db.disconnect()


@shared_task
def cleanup_cancelled_enrollments():
    """
    Cleanup old cancelled enrollments
    """
    db = Prisma()
    db.connect()
    
    try:
        from datetime import timedelta
        
        # Delete enrollments cancelled more than 90 days ago
        cutoff_date = datetime.now() - timedelta(days=90)
        
        deleted = db.enrollment.delete_many(
            where={
                'status': 'CANCELLED',
                'updatedAt': {'lt': cutoff_date}
            }
        )
        
        logger.info(f"Cleaned up {deleted} cancelled enrollments")
        
    finally:
        db.disconnect()