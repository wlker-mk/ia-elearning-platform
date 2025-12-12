from celery import shared_task
import logging
from .services import QuizzesService
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)


def run_async(coro):
    """Helper to run async functions in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@shared_task
def calculate_quiz_statistics(quiz_id: str):
    """Calculate and cache quiz statistics"""
    logger.info(f"Calculating statistics for quiz: {quiz_id}")
    
    async def _calculate():
        service = QuizzesService()
        await service.connect()
        try:
            stats = await service.get_quiz_statistics(quiz_id)
            logger.info(f"Statistics calculated for quiz {quiz_id}: {stats}")
            return stats
        finally:
            await service.disconnect()
    
    return run_async(_calculate())


@shared_task
def auto_submit_expired_attempts():
    """Auto-submit quiz attempts that have exceeded their time limit"""
    logger.info("Checking for expired quiz attempts...")
    
    async def _auto_submit():
        service = QuizzesService()
        await service.connect()
        try:
            # This would need custom query - simplified example
            from prisma import Prisma
            db = Prisma()
            await db.connect()
            
            # Find attempts that are not submitted and started more than duration ago
            # This is a simplified version - you'd need to join with Quiz to get duration
            now = datetime.now()
            
            logger.info("Expired attempts check completed")
            await db.disconnect()
        finally:
            await service.disconnect()
    
    return run_async(_auto_submit())


@shared_task
def process_proctoring_data(session_id: str, data: dict):
    """Process and analyze proctoring data"""
    logger.info(f"Processing proctoring data for session: {session_id}")
    
    async def _process():
        service = QuizzesService()
        await service.connect()
        try:
            # Analyze proctoring data for suspicious patterns
            suspicious_events = []
            
            # Check for excessive tab switches
            if data.get('tab_switches', 0) > 5:
                suspicious_events.append({
                    'type': 'excessive_tab_switches',
                    'severity': 'high',
                    'details': f"User switched tabs {data['tab_switches']} times"
                })
            
            # Check for face detection issues
            if data.get('no_face_detected'):
                suspicious_events.append({
                    'type': 'no_face_detected',
                    'severity': 'medium',
                    'details': 'Face was not detected during the session'
                })
            
            # Check for multiple faces
            if data.get('multiple_faces'):
                suspicious_events.append({
                    'type': 'multiple_faces',
                    'severity': 'critical',
                    'details': 'Multiple faces detected in frame'
                })
            
            # Update session if suspicious activity found
            if suspicious_events:
                await service.update_proctoring_session(session_id, {
                    'suspicious_activity': suspicious_events,
                    'flagged_for_review': True
                })
                logger.warning(f"Session {session_id} flagged: {len(suspicious_events)} suspicious events")
            
            return suspicious_events
        finally:
            await service.disconnect()
    
    return run_async(_process())


@shared_task
def send_quiz_result_notification(attempt_id: str):
    """Send notification to student about quiz results"""
    logger.info(f"Sending result notification for attempt: {attempt_id}")
    
    async def _send():
        service = QuizzesService()
        await service.connect()
        try:
            from prisma import Prisma
            db = Prisma()
            await db.connect()
            
            attempt = await db.quizattempt.find_unique(where={'id': attempt_id})
            
            if not attempt:
                logger.error(f"Attempt {attempt_id} not found")
                return
            
            # Here you would integrate with your notification service
            # For now, just log
            logger.info(
                f"Quiz result - Student: {attempt.studentId}, "
                f"Score: {attempt.percentage}%, "
                f"Passed: {attempt.isPassed}"
            )
            
            await db.disconnect()
        finally:
            await service.disconnect()
    
    return run_async(_send())


@shared_task
def generate_quiz_report(quiz_id: str):
    """Generate comprehensive quiz report"""
    logger.info(f"Generating report for quiz: {quiz_id}")
    
    async def _generate():
        service = QuizzesService()
        await service.connect()
        try:
            stats = await service.get_quiz_statistics(quiz_id)
            attempts = await service.get_quiz_attempts(quiz_id)
            
            report = {
                'quiz_id': quiz_id,
                'generated_at': datetime.now().isoformat(),
                'statistics': stats,
                'total_students': len(set(a.studentId for a in attempts)),
                'completion_rate': len([a for a in attempts if a.submittedAt]) / len(attempts) * 100 if attempts else 0,
            }
            
            logger.info(f"Report generated for quiz {quiz_id}")
            return report
        finally:
            await service.disconnect()
    
    return run_async(_generate())


@shared_task
def cleanup_old_proctoring_media(days: int = 90):
    """Clean up old proctoring media files"""
    logger.info(f"Cleaning up proctoring media older than {days} days")
    
    async def _cleanup():
        service = QuizzesService()
        await service.connect()
        try:
            from prisma import Prisma
            db = Prisma()
            await db.connect()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Find old sessions
            old_sessions = await db.proctoringsession.find_many(
                where={
                    'endedAt': {'lt': cutoff_date}
                }
            )
            
            # Here you would delete the actual media files from storage
            # and update the database records
            logger.info(f"Found {len(old_sessions)} old proctoring sessions")
            
            await db.disconnect()
        finally:
            await service.disconnect()
    
    return run_async(_cleanup())


@shared_task
def flag_anomalous_attempts():
    """Flag quiz attempts with anomalous patterns"""
    logger.info("Checking for anomalous quiz attempts...")
    
    async def _flag():
        service = QuizzesService()
        await service.connect()
        try:
            from prisma import Prisma
            db = Prisma()
            await db.connect()
            
            # Find attempts with suspiciously high scores and low time spent
            attempts = await db.quizattempt.find_many(
                where={
                    'percentage': {'gte': 90},
                    'timeSpent': {'not': None}
                }
            )
            
            flagged_count = 0
            for attempt in attempts:
                # Get quiz to check duration
                quiz = await db.quiz.find_unique(where={'id': attempt.quizId})
                
                if quiz and quiz.duration:
                    expected_min_time = quiz.duration * 60 * 0.2  # 20% of quiz duration in seconds
                    
                    if attempt.timeSpent < expected_min_time:
                        # Flag the proctoring session
                        session = await db.proctoringsession.find_unique(
                            where={'quizAttemptId': attempt.id}
                        )
                        
                        if session:
                            await service.update_proctoring_session(session.id, {
                                'flagged_for_review': True,
                                'suspicious_activity': [
                                    {
                                        'type': 'anomalous_completion_time',
                                        'severity': 'high',
                                        'details': f'Completed in {attempt.timeSpent}s with {attempt.percentage}% score'
                                    }
                                ]
                            })
                            flagged_count += 1
            
            logger.info(f"Flagged {flagged_count} anomalous attempts")
            await db.disconnect()
        finally:
            await service.disconnect()
    
    return run_async(_flag())