# ========== signals.py ==========
import logging
from apps.courses.courses.signals import publish_event

logger = logging.getLogger(__name__)

def certificate_issued_handler(certificate_id: str, user_id: str, course_id: str):
    """Handler appelé quand un certificat est émis"""
    logger.info(f"Certificate issued: {certificate_id}")
    
    # Publier l'événement
    publish_event('certificate.issued', {
        'certificateId': certificate_id,
        'userId': user_id,
        'courseId': course_id
    })
    
    # Incrémenter le compteur de complétions du cours
    from apps.courses.courses.services import CoursesService
    import asyncio
    
    async def _increment():
        service = CoursesService()
        await service.connect()
        try:
            await service.increment_completion_count(course_id)
        finally:
            await service.disconnect()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_increment())
    loop.close()

def certificate_verified_handler(certificate_id: str, ip_address: str = None):
    """Handler appelé quand un certificat est vérifié"""
    logger.info(f"Certificate verified: {certificate_id}")
    
    # Publier un événement pour analytics
    publish_event('certificate.verified', {
        'certificateId': certificate_id,
        'ipAddress': ip_address
    })

def certificate_revoked_handler(certificate_id: str, reason: str = None):
    """Handler appelé quand un certificat est révoqué"""
    logger.info(f"Certificate revoked: {certificate_id}")
    
    # Publier l'événement
    publish_event('certificate.revoked', {
        'certificateId': certificate_id,
        'reason': reason
    })
    
    # Notifier l'utilisateur
    # send_notification('certificate_revoked', ...)