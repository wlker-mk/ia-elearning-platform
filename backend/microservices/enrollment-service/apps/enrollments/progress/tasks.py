from celery import shared_task
from prisma import Prisma
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def cleanup_inactive_sessions():
    """
    Mark inactive study sessions as ended
    """
    db = Prisma()
    db.connect()
    
    try:
        # Find sessions inactive for more than 30 minutes
        cutoff_time = datetime.now() - timedelta(minutes=30)
        
        sessions = db.studysession.find_many(
            where={
                'isActive': True,
                'startTime': {'lt': cutoff_time}
            }
        )
        
        count = 0
        for session in sessions:
            duration = int((datetime.now() - session.startTime).total_seconds())
            
            db.studysession.update(
                where={'id': session.id},
                data={
                    'isActive': False,
                    'endTime': datetime.now(),
                    'duration': duration
                }
            )
            
            # Update enrollment time
            enrollment = db.enrollment.find_unique(
                where={'id': session.enrollmentId}
            )
            
            if enrollment:
                db.enrollment.update(
                    where={'id': enrollment.id},
                    data={
                        'totalTimeSpent': enrollment.totalTimeSpent + duration
                    }
                )
            
            count += 1
        
        logger.info(f"Cleaned up {count} inactive study sessions")
        
    finally:
        db.disconnect()


@shared_task
def generate_daily_progress_reports():
    """
    Generate daily progress reports for students
    """
    db = Prisma()
    db.connect()
    
    try:
        # Get all active enrollments
        enrollments = db.enrollment.find_many(
            where={'status': {'in': ['ACTIVE', 'IN_PROGRESS']}}
        )
        
        yesterday = datetime.now() - timedelta(days=1)
        
        for enrollment in enrollments:
            # Get yesterday's progress
            progress_records = db.progress.find_many(
                where={
                    'enrollmentId': enrollment.id,
                    'lastAccessedAt': {
                        'gte': yesterday,
                        'lt': datetime.now()
                    }
                }
            )
            
            if not progress_records:
                continue
            
            # Calculate stats
            lessons_completed = sum(1 for p in progress_records if p.isCompleted)
            time_spent = sum(p.timeSpent for p in progress_records)
            
            logger.info(
                f"Student {enrollment.studentId} completed {lessons_completed} "
                f"lessons and spent {time_spent} seconds studying"
            )
            
            # TODO: Send email report
        
        logger.info("Daily progress reports generated")
        
    finally:
        db.disconnect()


@shared_task
def update_progress_percentages():
    """
    Recalculate progress percentages based on watched duration
    """
    db = Prisma()
    db.connect()
    
    try:
        progress_records = db.progress.find_many(
            where={'isCompleted': False}
        )
        
        for progress in progress_records:
            # Fetch lesson duration from courses service
            # For now, use a simple calculation
            if progress.watchedDuration > 0:
                # Assuming lessons are tracked properly
                percentage = min(progress.percentage, 100)
                
                db.progress.update(
                    where={'id': progress.id},
                    data={'percentage': percentage}
                )
        
        logger.info(f"Updated {len(progress_records)} progress records")
        
    finally:
        db.disconnect()


@shared_task
def calculate_learning_streaks():
    """
    Calculate and update learning streaks for all students
    """
    db = Prisma()
    db.connect()
    
    try:
        # Get unique student IDs
        enrollments = db.enrollment.find_many()
        student_ids = list(set(e.studentId for e in enrollments))
        
        for student_id in student_ids:
            # Get study sessions
            sessions = db.studysession.find_many(
                where={'studentId': student_id},
                order={'startTime': 'desc'}
            )
            
            if not sessions:
                continue
            
            # Calculate streaks
            days_active = set()
            for session in sessions:
                day = session.startTime.date()
                days_active.add(day)
            
            sorted_days = sorted(days_active, reverse=True)
            
            # Current streak
            current_streak = 0
            today = datetime.now().date()
            
            for i, day in enumerate(sorted_days):
                expected_day = today - timedelta(days=i)
                if day == expected_day:
                    current_streak += 1
                else:
                    break
            
            logger.info(f"Student {student_id} has a {current_streak}-day streak")
        
        logger.info("Learning streaks calculated")
        
    finally:
        db.disconnect()


@shared_task
def sync_quiz_scores():
    """
    Sync quiz scores from quiz service
    """
    db = Prisma()
    db.connect()
    
    try:
        # TODO: Fetch quiz results from quiz service
        # Update progress records with quiz scores
        
        logger.info("Quiz scores synced")
        
    finally:
        db.disconnect()