from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import QuizAttempt, ProctoringSession
from .tasks import (
    send_quiz_result_notification,
    calculate_quiz_statistics,
    process_proctoring_data
)
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=QuizAttempt)
def quiz_attempt_submitted(sender, instance, created, **kwargs):
    """Handle quiz attempt submission"""
    if not created and instance.submitted_at:
        logger.info(f"Quiz attempt {instance.id} submitted by student {instance.student_id}")
        
        # Send notification asynchronously
        send_quiz_result_notification.delay(str(instance.id))
        
        # Update quiz statistics
        calculate_quiz_statistics.delay(str(instance.quiz_id))
        
        # Log performance
        if instance.is_passed:
            logger.info(
                f"Student {instance.student_id} passed quiz {instance.quiz_id} "
                f"with {instance.percentage}%"
            )
        else:
            logger.info(
                f"Student {instance.student_id} failed quiz {instance.quiz_id} "
                f"with {instance.percentage}%"
            )


@receiver(post_save, sender=ProctoringSession)
def proctoring_session_updated(sender, instance, created, **kwargs):
    """Handle proctoring session updates"""
    if instance.flagged_for_review and not instance.reviewed_at:
        logger.warning(
            f"Proctoring session {instance.id} flagged for review - "
            f"Tab switches: {instance.tab_switches}, "
            f"Multiple faces: {instance.multiple_faces}, "
            f"No face: {instance.no_face_detected}, "
            f"Copy/paste: {instance.copy_paste_detected}"
        )
        
        # Process proctoring data asynchronously
        data = {
            'tab_switches': instance.tab_switches,
            'multiple_faces': instance.multiple_faces,
            'no_face_detected': instance.no_face_detected,
            'copy_paste_detected': instance.copy_paste_detected,
        }
        process_proctoring_data.delay(str(instance.id), data)
    
    if instance.reviewed_at and instance.reviewed_by:
        logger.info(
            f"Proctoring session {instance.id} reviewed by {instance.reviewed_by}"
        )


@receiver(pre_delete, sender=QuizAttempt)
def quiz_attempt_deleted(sender, instance, **kwargs):
    """Handle quiz attempt deletion"""
    logger.info(f"Quiz attempt {instance.id} is being deleted")
    
    # Clean up associated proctoring session
    try:
        ProctoringSession.objects.filter(quiz_attempt_id=instance.id).delete()
        logger.info(f"Proctoring session for attempt {instance.id} deleted")
    except Exception as e:
        logger.error(f"Error deleting proctoring session: {e}")